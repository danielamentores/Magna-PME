"""Leitura de faturas com Gemini 2.5 Flash."""
from __future__ import annotations

import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import date

import google.generativeai as genai

from core.config import get_settings
from core.models import DadosExtraidosFatura

logger = logging.getLogger(__name__)


PROMPT_EXTRACAO = """
Es um assistente especialista em ler faturas portuguesas. Le esta fatura e
extrai os seguintes campos. Responde APENAS com um JSON valido, sem texto antes
ou depois, sem ``` markdown.

Campos a extrair:
{
  "numero_fatura": "string ou null",
  "data_fatura": "string YYYY-MM-DD ou null",
  "valor_total": "numero decimal ou null (ex: 123.45)",
  "nif_emitente": "string 9 digitos ou null",
  "nif_destinatario": "string 9 digitos ou null",
  "nome_emitente": "string ou null",
  "descricao": "string ou null",
  "confianca": "numero entre 0 e 1",
  "erros": ["array de strings com problemas"]
}

Regras:
- Valores monetarios SEM simbolo (so o numero)
- Datas em formato ISO YYYY-MM-DD
- NIFs portugueses tem 9 digitos
- Se nao encontrares um campo, poe null
- "confianca" baixa (<0.5) se ilegivel ou faltam dados criticos

Retorna SO o JSON.
"""


def _parse_data(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_decimal(v):
    if v is None:
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _limpar_nif(nif):
    if not nif:
        return None
    apenas_digitos = "".join(c for c in str(nif) if c.isdigit())
    return apenas_digitos if len(apenas_digitos) == 9 else None


def ler_fatura(conteudo: bytes, mime_type: str = "application/pdf") -> DadosExtraidosFatura:
    """Le uma fatura e devolve dados estruturados."""
    settings = get_settings()
    api_key = settings.require("gemini_api_key")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(settings.gemini_model)

    try:
        response = model.generate_content(
            [{"mime_type": mime_type, "data": conteudo}, PROMPT_EXTRACAO],
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )
        dados_raw = json.loads(response.text.strip())

        return DadosExtraidosFatura(
            numero_fatura=dados_raw.get("numero_fatura"),
            data_fatura=_parse_data(dados_raw.get("data_fatura")),
            valor_total=_parse_decimal(dados_raw.get("valor_total")),
            nif_emitente=_limpar_nif(dados_raw.get("nif_emitente")),
            nif_destinatario=_limpar_nif(dados_raw.get("nif_destinatario")),
            nome_emitente=dados_raw.get("nome_emitente"),
            descricao=dados_raw.get("descricao"),
            confianca=float(dados_raw.get("confianca", 0.0)),
            erros=dados_raw.get("erros", []) or [],
        )

    except json.JSONDecodeError as e:
        logger.exception("Gemini devolveu JSON invalido")
        return DadosExtraidosFatura(confianca=0.0, erros=[f"JSON invalido: {e}"])
    except Exception as e:
        logger.exception("Erro inesperado")
        return DadosExtraidosFatura(confianca=0.0, erros=[f"{type(e).__name__}: {e}"])


def leitura_e_valida(conteudo: bytes, mime_type: str = "application/pdf") -> tuple[DadosExtraidosFatura, bool]:
    """Le e valida. Devolve (dados, ok)."""
    dados = ler_fatura(conteudo, mime_type)
    confianca_minima = 0.7
    campos_criticos = [dados.numero_fatura, dados.data_fatura, dados.valor_total, dados.nif_emitente]
    ok = dados.confianca >= confianca_minima and all(c is not None for c in campos_criticos)
    return dados, ok
