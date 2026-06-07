"""Adaptador para a plataforma Magna (Excel agora, API depois)."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

import pandas as pd

from core.config import get_settings
from core.models import AcaoEstado

logger = logging.getLogger(__name__)


class AcaoMagnaDTO:
    """Acao tal como vem da Magna."""

    def __init__(
        self, magna_id, nome, estado, codigo=None, empresa_cliente=None,
        formador_email=None, coordenador_email=None, data_inicio=None,
        data_fim=None, volume_horas=None, formandos_inscritos=None,
        formandos_certificados=None, valor_formador=None, valor_consultor=None,
        valor_empresa=None, fechada_em=None,
    ):
        self.magna_id = magna_id
        self.nome = nome
        self.estado = estado
        self.codigo = codigo
        self.empresa_cliente = empresa_cliente
        self.formador_email = formador_email
        self.coordenador_email = coordenador_email
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.volume_horas = volume_horas
        self.formandos_inscritos = formandos_inscritos
        self.formandos_certificados = formandos_certificados
        self.valor_formador = valor_formador
        self.valor_consultor = valor_consultor
        self.valor_empresa = valor_empresa
        self.fechada_em = fechada_em

    def __repr__(self):
        return f"<AcaoMagna {self.magna_id} {self.nome} {self.estado.value}>"


class MagnaAdapter(ABC):
    @abstractmethod
    def listar_acoes(self) -> list[AcaoMagnaDTO]: ...

    @abstractmethod
    def obter_acao(self, magna_id: str) -> Optional[AcaoMagnaDTO]: ...

    @abstractmethod
    def procurar_acao_por_nome(self, nome: str) -> Optional[AcaoMagnaDTO]: ...


COLUNAS_EXCEL = {
    "magna_id": ["ID", "Id Acao", "Codigo Magna"],
    "nome": ["Nome", "Acao", "Designacao"],
    "estado": ["Estado", "Situacao"],
    "codigo": ["Codigo", "Cod"],
    "empresa_cliente": ["Empresa", "Cliente"],
    "formador_email": ["Email Formador", "Formador Email"],
    "coordenador_email": ["Email Coordenador", "Coordenador Email"],
    "data_inicio": ["Data Inicio", "Inicio"],
    "data_fim": ["Data Fim", "Fim"],
    "volume_horas": ["Volume", "Horas"],
    "formandos_inscritos": ["Inscritos", "Formandos Inscritos"],
    "formandos_certificados": ["Certificados", "Formandos Certificados"],
    "valor_formador": ["Valor Formador"],
    "valor_consultor": ["Valor Consultor"],
    "valor_empresa": ["Valor Empresa"],
}

ESTADO_MAP = {
    "planeada": AcaoEstado.PLANEADA,
    "planeado": AcaoEstado.PLANEADA,
    "a decorrer": AcaoEstado.A_DECORRER,
    "em curso": AcaoEstado.A_DECORRER,
    "terminada": AcaoEstado.TERMINADA_SEM_FECHO,
    "terminado": AcaoEstado.TERMINADA_SEM_FECHO,
    "terminada sem fecho": AcaoEstado.TERMINADA_SEM_FECHO,
    "fechada": AcaoEstado.FECHADA,
    "fechado": AcaoEstado.FECHADA,
    "encerrada": AcaoEstado.FECHADA,
}


def _pick_col(df, candidates):
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


class MagnaExcelAdapter(MagnaAdapter):
    """Le acoes a partir de um Excel exportado da Magna."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self._cache = None

    def _carregar(self):
        if self._cache is not None:
            return self._cache

        if not self.caminho.exists():
            logger.warning("Excel da Magna nao encontrado: %s", self.caminho)
            self._cache = []
            return self._cache

        df = pd.read_excel(self.caminho)
        cols = {k: _pick_col(df, v) for k, v in COLUNAS_EXCEL.items()}

        for o in ["magna_id", "nome", "estado"]:
            if cols[o] is None:
                raise ValueError(
                    f"Coluna obrigatoria '{o}' nao encontrada. Candidatos: {COLUNAS_EXCEL[o]}"
                )

        acoes = []
        for _, row in df.iterrows():
            estado_raw = str(row[cols["estado"]]).lower().strip()
            estado = ESTADO_MAP.get(estado_raw, AcaoEstado.PLANEADA)
            acoes.append(AcaoMagnaDTO(
                magna_id=str(row[cols["magna_id"]]),
                nome=str(row[cols["nome"]]),
                estado=estado,
                codigo=_safe_str(row, cols["codigo"]),
                empresa_cliente=_safe_str(row, cols["empresa_cliente"]),
                formador_email=_safe_str(row, cols["formador_email"]),
                coordenador_email=_safe_str(row, cols["coordenador_email"]),
                data_inicio=_safe_date(row, cols["data_inicio"]),
                data_fim=_safe_date(row, cols["data_fim"]),
                volume_horas=_safe_decimal(row, cols["volume_horas"]),
                formandos_inscritos=_safe_int(row, cols["formandos_inscritos"]),
                formandos_certificados=_safe_int(row, cols["formandos_certificados"]),
                valor_formador=_safe_decimal(row, cols["valor_formador"]),
                valor_consultor=_safe_decimal(row, cols["valor_consultor"]),
                valor_empresa=_safe_decimal(row, cols["valor_empresa"]),
            ))

        self._cache = acoes
        logger.info("Carregadas %d acoes de %s", len(acoes), self.caminho)
        return acoes

    def listar_acoes(self):
        return self._carregar()

    def obter_acao(self, magna_id):
        return next((a for a in self._carregar() if a.magna_id == magna_id), None)

    def procurar_acao_por_nome(self, nome):
        nome_lower = nome.lower().strip()
        for a in self._carregar():
            if a.nome.lower().strip() == nome_lower:
                return a
        for a in self._carregar():
            if nome_lower in a.nome.lower():
                return a
        return None

    def refresh(self):
        self._cache = None


class MagnaApiAdapter(MagnaAdapter):
    """Adaptador para a API da Magna (a implementar quando estiver disponivel)."""

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def listar_acoes(self):
        raise NotImplementedError("API da Magna ainda nao implementada.")

    def obter_acao(self, magna_id):
        raise NotImplementedError

    def procurar_acao_por_nome(self, nome):
        raise NotImplementedError


def get_magna_adapter() -> MagnaAdapter:
    settings = get_settings()
    if settings.magna_mode == "api":
        return MagnaApiAdapter(
            api_url=settings.require("magna_api_url"),
            api_key=settings.require("magna_api_key"),
        )
    return MagnaExcelAdapter(caminho=settings.magna_excel_path)


def _safe_str(row, col):
    if col is None:
        return None
    v = row[col]
    return None if pd.isna(v) else str(v).strip()


def _safe_int(row, col):
    if col is None:
        return None
    v = row[col]
    if pd.isna(v):
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def _safe_decimal(row, col):
    if col is None:
        return None
    v = row[col]
    if pd.isna(v):
        return None
    try:
        return Decimal(str(v))
    except Exception:
        return None


def _safe_date(row, col):
    if col is None:
        return None
    v = row[col]
    if pd.isna(v):
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return pd.to_datetime(v).date()
    except Exception:
        return None
