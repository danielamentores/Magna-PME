"""
Geração de Nota de Honorários em .docx
Usa node + docx-js via subprocess.
Chama: gerar_nh(dados_dict) → bytes do ficheiro Word
"""
from __future__ import annotations
import json
import subprocess
import tempfile
import os
from pathlib import Path


# Caminho para o script JS (colocar em app/)
_JS_PATH = Path(__file__).parent / "gerar_nh.js"


def calcular_valor_acao(ch: int, formandos: int) -> float:
    """Regra: <13 formandos → 2,50€/vol; ≥13 → 3,12€/vol"""
    rate = 3.12 if formandos >= 13 else 2.50
    return round(ch * formandos * rate, 2)


def calcular_totais(acoes: list[dict]) -> dict:
    valor_base = sum(a.get("valor", 0) for a in acoes)
    return {
        "valor_base":    round(valor_base, 2),
        "iva_valor":     0.00,
        "irs_valor":     0.00,
        "valor_liquido": round(valor_base, 2),
    }


def gerar_nh(dados: dict) -> bytes:
    """
    Gera a NH em .docx e devolve os bytes.

    dados = {
        "nh_numero": int,
        "consultor": { nome, nif, dgert, iva, irs, morada, cod_postal, localidade, iban },
        "projeto":   { nome, codigo },
        "destinatario": { nif, nome, morada },
        "condicoes": str,
        "descritivo": str,
        "acoes": [ { empresa, operacao, ufcd, inicio, fim, ch, formandos, valor } ],
        "data_inicial": str,
        "data_final": str,
        "valor_base": float,
        "iva_valor": float,
        "irs_valor": float,
        "valor_liquido": float,
    }
    """
    # Escreve dados em ficheiro temporário
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)
        json_path = f.name

    out_path = json_path.replace(".json", ".docx")

    try:
        result = subprocess.run(
            ["node", str(_JS_PATH), json_path, out_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"Erro na geração da NH: {result.stderr}")

        with open(out_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(json_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def construir_dados_nh(
    nh_numero: int,
    consultor: dict,
    projeto: dict,
    acoes: list[dict],
) -> dict:
    """
    Constrói o dict completo para gerar_nh() a partir dos dados da BD.
    consultor = linha da tabela profiles
    projeto   = linha da tabela acoes (magna_id, nome)
    acoes     = lista de linhas da tabela acoes
    """
    acoes_nh = []
    for a in acoes:
        ch        = int(a.get("volume_horas") or 0)
        formandos = int(a.get("formandos_certificados") or 0)
        valor     = calcular_valor_acao(ch, formandos)
        acoes_nh.append({
            "empresa":   a.get("empresa_cliente") or "—",
            "operacao":  a.get("codigo") or a.get("magna_id") or "—",
            "ufcd":      a.get("nome") or "—",
            "inicio":    str(a.get("data_inicio") or "—"),
            "fim":       str(a.get("data_fim") or "—"),
            "ch":        ch,
            "formandos": formandos,
            "valor":     valor,
        })

    totais = calcular_totais(acoes_nh)
    datas  = sorted([a["inicio"] for a in acoes_nh if a["inicio"] != "—"])

    return {
        "nh_numero":    nh_numero,
        "consultor": {
            "nome":       consultor.get("nome") or "—",
            "nif":        consultor.get("nif") or "—",
            "dgert":      "Sim",
            "iva":        "0%",
            "irs":        "0%",
            "morada":     "—",
            "cod_postal": "—",
            "localidade": "—",
            "iban":       consultor.get("iban") or "—",
        },
        "projeto": {
            "nome":   projeto.get("nome") or "—",
            "codigo": projeto.get("magna_id") or "—",
        },
        "destinatario": {
            "nif":    "513348301",
            "nome":   "Mentores & Tutores - Associação Para O Desenvolvimento Empresarial e dos Territórios",
            "morada": "Rua Padre Estêvão Cabral nº 72 - 2º andar, 3000-316 Coimbra",
        },
        "condicoes": "Valor ajustado ao volume realizado e em reembolso na plataforma Magna. Turmas <13 formandos: 2,50 € × volume. Turmas ≥13 formandos: 3,12 € × volume.",
        "descritivo": f"Serviços conexos à organização da formação/consultoria de diagnóstico, planeamento e implementação de formação em contexto empresarial no projeto {projeto.get('magna_id', '')}",
        "acoes":        acoes_nh,
        "data_inicial": datas[0] if datas else "—",
        "data_final":   datas[-1] if datas else "—",
        **totais,
    }
