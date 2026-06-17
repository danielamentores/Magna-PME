"""
Camada de dados para o financeiro.
Todas as queries ao Supabase ficam aqui.
O financeiro.py importa daqui — nunca acede à BD diretamente.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional
import streamlit as st
from supabase import create_client, Client
from core.config import get_settings


# ---------------------------------------------------------------------------
# CLIENTE SUPABASE (cached por sessão)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_supabase() -> Client:
    settings = get_settings()
    return create_client(
        settings.require("supabase_url"),
        settings.require("supabase_key"),
    )


def get_supabase_admin() -> Client:
    """Cliente com service role — usar só para operações admin (ex: aprovar/rejeitar)."""
    settings = get_settings()
    return create_client(
        settings.require("supabase_url"),
        settings.require("supabase_service_key"),
    )


# ---------------------------------------------------------------------------
# DASHBOARD — métricas de topo
# ---------------------------------------------------------------------------

def get_metricas_dashboard() -> dict:
    """
    Devolve contagens e totais por estado para os cards de topo.
    """
    sb = get_supabase()

    estados = ["submetida", "aprovada", "paga", "rejeitada", "leitura_falhada", "acao_nao_fechada"]
    resultado = {
        "pre_aprovacao_total": 0,
        "pre_aprovacao_count": 0,
        "aprovado_total": 0,
        "aprovado_count": 0,
        "pago_mes_total": 0,
        "pago_mes_count": 0,
        "vencido_total": 0,
        "vencido_count": 0,
    }

    try:
        # Pré-aprovação = submetidas + leitura_falhada + acao_nao_fechada
        r = sb.table("faturas").select("valor, estado").in_(
            "estado", ["submetida", "leitura_falhada", "acao_nao_fechada"]
        ).execute()
        resultado["pre_aprovacao_count"] = len(r.data)
        resultado["pre_aprovacao_total"] = sum(row["valor"] or 0 for row in r.data)

        # Aprovadas a pagar
        r = sb.table("faturas").select("valor").eq("estado", "aprovada").execute()
        resultado["aprovado_count"] = len(r.data)
        resultado["aprovado_total"] = sum(row["valor"] or 0 for row in r.data)

        # Pagas este mês
        inicio_mes = date.today().replace(day=1).isoformat()
        r = sb.table("faturas").select("valor").eq("estado", "paga").gte("pago_em", inicio_mes).execute()
        resultado["pago_mes_count"] = len(r.data)
        resultado["pago_mes_total"] = sum(row["valor"] or 0 for row in r.data)

        # Vencidas (aprovadas com prazo_pagamento < hoje)
        r = sb.table("faturas").select("valor").eq("estado", "aprovada").lt(
            "prazo_pagamento", date.today().isoformat()
        ).execute()
        resultado["vencido_count"] = len(r.data)
        resultado["vencido_total"] = sum(row["valor"] or 0 for row in r.data)

    except Exception as e:
        st.error(f"Erro ao carregar métricas: {e}")

    return resultado


# ---------------------------------------------------------------------------
# DASHBOARD — faturas recentes
# ---------------------------------------------------------------------------

def get_faturas_recentes(limit: int = 10) -> list[dict]:
    """
    Últimas faturas submetidas, com nome do formador e ação associada.
    """
    sb = get_supabase()
    try:
        r = sb.table("faturas").select(
            "id, numero_fatura, valor, estado, created_at, "
            "profiles(nome), acoes(nome, magna_id)"
        ).order("created_at", desc=True).limit(limit).execute()
        return r.data
    except Exception as e:
        st.error(f"Erro ao carregar faturas recentes: {e}")
        return []


# ---------------------------------------------------------------------------
# DASHBOARD — despesa por projeto
# ---------------------------------------------------------------------------

def get_despesa_por_projeto() -> list[dict]:
    """
    Total pago + aprovado por ação (projeto), agrupado por magna_id.
    """
    sb = get_supabase()
    try:
        r = sb.table("faturas").select(
            "valor, estado, acoes(nome, magna_id)"
        ).in_("estado", ["aprovada", "paga"]).execute()

        agrupado: dict[str, dict] = {}
        for row in r.data:
            acao = row.get("acoes") or {}
            nome = acao.get("nome") or "Sem projeto"
            valor = row.get("valor") or 0
            if nome not in agrupado:
                agrupado[nome] = {"projeto": nome, "valor": 0}
            agrupado[nome]["valor"] += valor

        return sorted(agrupado.values(), key=lambda x: x["valor"], reverse=True)
    except Exception as e:
        st.error(f"Erro ao carregar despesa por projeto: {e}")
        return []


# ---------------------------------------------------------------------------
# ALERTAS — pré-aprovação manual
# ---------------------------------------------------------------------------

def get_faturas_pre_aprovacao(projeto: Optional[str] = None) -> list[dict]:
    """
    Faturas que falharam validação automática e precisam de aprovação manual.
    Estados: submetida, leitura_falhada, acao_nao_fechada
    """
    sb = get_supabase()
    try:
        q = sb.table("faturas").select(
            "id, numero_fatura, valor, estado, erro_leitura, notas, created_at, ficheiro_url, "
            "profiles(nome, email), acoes(nome, magna_id)"
        ).in_("estado", ["submetida", "leitura_falhada", "acao_nao_fechada"]).order("created_at", desc=True)

        r = q.execute()
        dados = r.data

        if projeto and projeto != "Todos":
            dados = [d for d in dados if (d.get("acoes") or {}).get("nome") == projeto]

        return dados
    except Exception as e:
        st.error(f"Erro ao carregar pré-aprovação: {e}")
        return []


# ---------------------------------------------------------------------------
# ALERTAS — faturas vencidas
# ---------------------------------------------------------------------------

def get_faturas_vencidas(projeto: Optional[str] = None) -> list[dict]:
    """
    Faturas aprovadas cujo prazo_pagamento já passou.
    """
    sb = get_supabase()
    try:
        r = sb.table("faturas").select(
            "id, numero_fatura, valor, prazo_pagamento, data_fatura, "
            "profiles(nome, email), acoes(nome, magna_id)"
        ).eq("estado", "aprovada").lt(
            "prazo_pagamento", date.today().isoformat()
        ).order("prazo_pagamento").execute()

        dados = r.data
        if projeto and projeto != "Todos":
            dados = [d for d in dados if (d.get("acoes") or {}).get("nome") == projeto]

        # Calcular dias em atraso
        for row in dados:
            prazo = date.fromisoformat(row["prazo_pagamento"]) if row.get("prazo_pagamento") else date.today()
            row["atraso"] = (date.today() - prazo).days

        return dados
    except Exception as e:
        st.error(f"Erro ao carregar faturas vencidas: {e}")
        return []


# ---------------------------------------------------------------------------
# ALERTAS — faturas a vencer (próximos N dias)
# ---------------------------------------------------------------------------

def get_faturas_a_vencer(dias: int = 30, projeto: Optional[str] = None) -> list[dict]:
    """
    Faturas aprovadas com prazo_pagamento entre hoje e hoje+dias.
    """
    sb = get_supabase()
    hoje = date.today()
    limite = (hoje + timedelta(days=dias)).isoformat()
    try:
        r = sb.table("faturas").select(
            "id, numero_fatura, valor, prazo_pagamento, data_fatura, "
            "profiles(nome, email), acoes(nome, magna_id)"
        ).eq("estado", "aprovada").gte(
            "prazo_pagamento", hoje.isoformat()
        ).lte("prazo_pagamento", limite).order("prazo_pagamento").execute()

        dados = r.data
        if projeto and projeto != "Todos":
            dados = [d for d in dados if (d.get("acoes") or {}).get("nome") == projeto]

        for row in dados:
            prazo = date.fromisoformat(row["prazo_pagamento"]) if row.get("prazo_pagamento") else hoje
            row["dias"] = (prazo - hoje).days

        return dados
    except Exception as e:
        st.error(f"Erro ao carregar faturas a vencer: {e}")
        return []


# ---------------------------------------------------------------------------
# ALERTAS — top formadores pendentes
# ---------------------------------------------------------------------------

def get_top_formadores_pendentes(limit: int = 5) -> list[dict]:
    sb = get_supabase()
    try:
        r = sb.table("faturas").select(
            "valor, profiles(nome)"
        ).in_("estado", ["aprovada", "submetida"]).execute()

        agrupado: dict[str, float] = {}
        for row in r.data:
            nome = (row.get("profiles") or {}).get("nome") or "Desconhecido"
            agrupado[nome] = agrupado.get(nome, 0) + (row.get("valor") or 0)

        ordenado = sorted(agrupado.items(), key=lambda x: x[1], reverse=True)
        return [{"formador": nome, "valor": val} for nome, val in ordenado[:limit]]
    except Exception as e:
        st.error(f"Erro ao carregar top formadores: {e}")
        return []


# ---------------------------------------------------------------------------
# ALERTAS — pendente por projeto
# ---------------------------------------------------------------------------

def get_pendente_por_projeto() -> list[dict]:
    sb = get_supabase()
    try:
        r = sb.table("faturas").select(
            "valor, acoes(nome)"
        ).in_("estado", ["aprovada", "submetida"]).execute()

        agrupado: dict[str, float] = {}
        for row in r.data:
            nome = (row.get("acoes") or {}).get("nome") or "Sem projeto"
            agrupado[nome] = agrupado.get(nome, 0) + (row.get("valor") or 0)

        return sorted(
            [{"projeto": k, "valor": v} for k, v in agrupado.items()],
            key=lambda x: x["valor"], reverse=True,
        )
    except Exception as e:
        st.error(f"Erro ao carregar pendente por projeto: {e}")
        return []


# ---------------------------------------------------------------------------
# AÇÕES — aprovar / rejeitar / marcar pago
# ---------------------------------------------------------------------------

def aprovar_fatura(fatura_id: str, user_nome: str) -> bool:
    sb = get_supabase_admin()
    try:
        sb.table("faturas").update({
            "estado": "aprovada",
            "notas": f"Aprovado manualmente por {user_nome}",
        }).eq("id", fatura_id).execute()

        _log_evento("fatura_aprovada_manual", f"Fatura {fatura_id} aprovada por {user_nome}", {"fatura_id": fatura_id})
        return True
    except Exception as e:
        st.error(f"Erro ao aprovar fatura: {e}")
        return False


def rejeitar_fatura(fatura_id: str, motivo: str, user_nome: str) -> bool:
    sb = get_supabase_admin()
    try:
        sb.table("faturas").update({
            "estado": "rejeitada",
            "notas": motivo,
        }).eq("id", fatura_id).execute()

        _log_evento("fatura_rejeitada", f"Fatura {fatura_id} rejeitada por {user_nome}: {motivo}", {"fatura_id": fatura_id, "motivo": motivo})
        return True
    except Exception as e:
        st.error(f"Erro ao rejeitar fatura: {e}")
        return False


def marcar_paga(fatura_id: str, user_nome: str) -> bool:
    sb = get_supabase_admin()
    try:
        from datetime import datetime
        sb.table("faturas").update({
            "estado": "paga",
            "pago_em": datetime.utcnow().isoformat(),
            "notas": f"Marcado como pago por {user_nome}",
        }).eq("id", fatura_id).execute()

        _log_evento("fatura_paga", f"Fatura {fatura_id} marcada como paga por {user_nome}", {"fatura_id": fatura_id})
        return True
    except Exception as e:
        st.error(f"Erro ao marcar fatura como paga: {e}")
        return False


# ---------------------------------------------------------------------------
# CASHFLOW — saídas semanais previstas
# ---------------------------------------------------------------------------

def get_cashflow_previsto(semanas: int = 13) -> tuple[list[str], list[float]]:
    """
    Agrupa faturas aprovadas por semana de prazo_pagamento.
    Devolve (labels, valores).
    """
    sb = get_supabase()
    hoje = date.today()
    limite = (hoje + timedelta(weeks=semanas)).isoformat()
    try:
        r = sb.table("faturas").select(
            "valor, prazo_pagamento"
        ).eq("estado", "aprovada").gte(
            "prazo_pagamento", hoje.isoformat()
        ).lte("prazo_pagamento", limite).execute()

        semana_map: dict[str, float] = {}
        for row in r.data:
            if not row.get("prazo_pagamento"):
                continue
            prazo = date.fromisoformat(row["prazo_pagamento"])
            # Número da semana ISO
            ano, sem, _ = prazo.isocalendar()
            label = f"S{sem} {prazo.strftime('%b')}"
            semana_map[label] = semana_map.get(label, 0) + (row.get("valor") or 0)

        labels = list(semana_map.keys())
        valores = list(semana_map.values())
        return labels, valores
    except Exception as e:
        st.error(f"Erro ao carregar cashflow: {e}")
        return [], []


# ---------------------------------------------------------------------------
# PROJETOS — lista para filtros
# ---------------------------------------------------------------------------

def get_projetos() -> list[dict]:
    """Lista de ações/projetos ativos para os filtros."""
    sb = get_supabase()
    try:
        r = sb.table("acoes").select("id, nome, magna_id").order("nome").execute()
        return r.data
    except Exception as e:
        st.error(f"Erro ao carregar projetos: {e}")
        return []


# ---------------------------------------------------------------------------
# HISTÓRICO — log de eventos do financeiro
# ---------------------------------------------------------------------------

def get_historico_financeiro(limit: int = 50) -> list[dict]:
    sb = get_supabase()
    try:
        r = sb.table("agent_events").select("*").ilike(
            "tipo", "fatura_%"
        ).order("criado_em", desc=True).limit(limit).execute()
        return r.data
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        return []


# ---------------------------------------------------------------------------
# HELPER INTERNO — log de eventos
# ---------------------------------------------------------------------------

def _log_evento(tipo: str, descricao: str, dados: dict) -> None:
    try:
        get_supabase_admin().table("agent_events").insert({
            "tipo": tipo,
            "descricao": descricao,
            "dados": dados,
            "sucesso": True,
        }).execute()
    except Exception:
        pass  # log nunca deve quebrar a app
