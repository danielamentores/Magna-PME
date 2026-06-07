"""Modelos de dados do Gestform."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    FORMADOR = "formador"
    COORDENADOR = "coordenador"
    GESTOR_PROJETO = "gestor_projeto"
    FINANCEIRO = "financeiro"
    ADMIN = "admin"


class AcaoEstado(str, Enum):
    PLANEADA = "planeada"
    A_DECORRER = "a_decorrer"
    TERMINADA_SEM_FECHO = "terminada_sem_fecho"
    FECHADA = "fechada"


class FaturaEstado(str, Enum):
    SUBMETIDA = "submetida"
    LEITURA_FALHADA = "leitura_falhada"
    ACAO_NAO_FECHADA = "acao_nao_fechada"
    APROVADA = "aprovada"
    PAGA = "paga"
    REJEITADA = "rejeitada"


class FaturacaoEstado(str, Enum):
    DISPONIVEL = "disponivel"
    SELECIONADA = "selecionada"
    AGUARDA_CONFIRMACAO = "aguarda_confirmacao"
    CONFIRMADA = "confirmada"
    FATURA_EMITIDA = "fatura_emitida"
    PAGA = "paga"


class ReembolsoEstado(str, Enum):
    DISPONIVEL = "disponivel"
    SELECIONADO = "selecionado"
    EM_PROCESSAMENTO = "em_processamento"
    CONCLUIDO = "concluido"


class Profile(BaseModel):
    id: UUID
    email: EmailStr
    nome: str
    nif: Optional[str] = None
    iban: Optional[str] = None
    role: UserRole = UserRole.FORMADOR
    ativo: bool = True
    magna_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Acao(BaseModel):
    id: UUID
    magna_id: str
    nome: str
    codigo: Optional[str] = None
    empresa_cliente: Optional[str] = None
    formador_id: Optional[UUID] = None
    coordenador_id: Optional[UUID] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    volume_horas: Optional[Decimal] = None
    formandos_inscritos: Optional[int] = None
    formandos_certificados: Optional[int] = None
    valor_formador: Optional[Decimal] = None
    valor_consultor: Optional[Decimal] = None
    valor_empresa: Optional[Decimal] = None
    estado: AcaoEstado = AcaoEstado.PLANEADA
    fechada_em: Optional[datetime] = None
    last_sync_magna: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Fatura(BaseModel):
    id: UUID
    formador_id: UUID
    acao_id: Optional[UUID] = None
    acao_nome_submetido: Optional[str] = None
    numero_fatura: Optional[str] = None
    data_fatura: Optional[date] = None
    valor: Optional[Decimal] = None
    nif_emitente: Optional[str] = None
    nif_destinatario: Optional[str] = None
    ficheiro_url: Optional[str] = None
    comprovativo_url: Optional[str] = None
    estado: FaturaEstado = FaturaEstado.SUBMETIDA
    dados_extraidos: Optional[dict] = None
    erro_leitura: Optional[str] = None
    prazo_pagamento: Optional[date] = None
    pago_em: Optional[datetime] = None
    ultimo_alerta_em: Optional[datetime] = None
    num_alertas_enviados: int = 0
    notas: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DadosExtraidosFatura(BaseModel):
    """Output estruturado da leitura de fatura pelo Gemini."""
    numero_fatura: Optional[str] = Field(None, description="Numero da fatura")
    data_fatura: Optional[date] = Field(None, description="Data de emissao")
    valor_total: Optional[Decimal] = Field(None, description="Total com IVA")
    nif_emitente: Optional[str] = Field(None, description="NIF do formador")
    nif_destinatario: Optional[str] = Field(None, description="NIF da empresa")
    nome_emitente: Optional[str] = None
    descricao: Optional[str] = None
    confianca: float = Field(0.0, ge=0.0, le=1.0)
    erros: list[str] = Field(default_factory=list)
