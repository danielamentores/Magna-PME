"""
Tab Consultores — página do financeiro.
Mostra: ações fechadas sem NH, NH emitidas a aguardar fatura, faturas pendentes.
Integra geração de NH em .docx.
"""
from __future__ import annotations

import io
from datetime import date, datetime
from typing import Optional

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# IMPORTS BD + GERADOR NH
# ---------------------------------------------------------------------------

try:
    from app.db_financeiro import get_supabase, get_supabase_admin, _log_evento
    from app.gerar_nh import construir_dados_nh, gerar_nh, calcular_valor_acao
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------

_MOCK_CONSULTORES = [
    {"id": "c1", "nome": "Etapas Pioneiras, Lda",    "nif": "510391125", "iban": "PT50004513454025352458285", "email": "etapas@demo.pt"},
    {"id": "c2", "nome": "Winet Consulting, Lda",    "nif": "509812345", "iban": "PT50001234567890123456789", "email": "winet@demo.pt"},
    {"id": "c3", "nome": "FormaConsult, Unip. Lda",  "nif": "511234567", "iban": "PT50009876543210987654321", "email": "formaconsult@demo.pt"},
]

_MOCK_ACOES_FECHADAS = [
    {"id": "a1", "magna_id": "ASE:OSEMC_30.1", "nome": "Amb. Seg.: Op. Seg. Equip. Movimentação Cargas 1", "empresa_cliente": "J.A. Veiga de Macedo",    "codigo": "ASE:OSEMC_30.1", "data_inicio": "2026-03-19", "data_fim": "2026-04-17", "volume_horas": 30, "formandos_certificados": 16, "consultor_id": "c1", "projeto": "PRODUTECH", "nh_emitida": False},
    {"id": "a2", "magna_id": "ASE:OSEMC_30.2", "nome": "Amb. Seg.: Op. Seg. Equip. Movimentação Cargas 2", "empresa_cliente": "J.A. Veiga de Macedo / Z Cork", "codigo": "ASE:OSEMC_30.2", "data_inicio": "2026-03-19", "data_fim": "2026-04-16", "volume_horas": 30, "formandos_certificados": 15, "consultor_id": "c1", "projeto": "PRODUTECH", "nh_emitida": False},
    {"id": "a3", "magna_id": "GEOEMC_8",       "nome": "Gestão Eficiente de Equipamentos de Movimentação", "empresa_cliente": "Manuaço",                 "codigo": "GEOEMC_8",       "data_inicio": "2026-02-06", "data_fim": "2026-02-13", "volume_horas": 8,  "formandos_certificados": 10, "consultor_id": "c2", "projeto": "ANIET",     "nh_emitida": False},
    {"id": "a4", "magna_id": "LGE_12",         "nome": "Liderança e gestão de equipas",                    "empresa_cliente": "Fenabel, S.A",            "codigo": "LGE_12",         "data_inicio": "2026-01-05", "data_fim": "2026-01-19", "volume_horas": 12, "formandos_certificados": 14, "consultor_id": "c2", "projeto": "MENTORES",  "nh_emitida": True},
    {"id": "a5", "magna_id": "TN_16",          "nome": "Técnicas de negociação",                           "empresa_cliente": "Fenabel, S.A",            "codigo": "TN_16",          "data_inicio": "2026-03-09", "data_fim": "2026-03-30", "volume_horas": 16, "formandos_certificados": 10, "consultor_id": "c3", "projeto": "MENTORES",  "nh_emitida": False},
]

_MOCK_NH_EMITIDAS = [
    {"id": "nh1", "consultor_id": "c2", "consultor_nome": "Winet Consulting, Lda", "projeto": "MENTORES", "valor": 1646.40, "data_emissao": "2026-05-10", "estado": "aguarda_fatura", "acoes": ["LGE_12"]},
]

_MOCK_FATURAS_CONSULTORES = [
    {"id": "fc1", "consultor_id": "c1", "consultor_nome": "Etapas Pioneiras, Lda", "projeto": "PRODUTECH", "numero_fatura": "FT-EC-2026/001", "valor": 2901.60, "estado": "aguarda_aprovacao", "data_submissao": "2026-05-20", "ficheiro_url": None},
]

_MOCK_FORMADORES_ACAO = {
    "a1": [{"nome": "Ivo Daniel Carneiro Monteiro", "n_fatura": "FT2026/0142", "valor": 3200, "estado": "aprovada"}],
    "a2": [{"nome": "Ivo Daniel Carneiro Monteiro", "n_fatura": "FT2026/0138", "valor": 2800, "estado": "pendente"}],
    "a3": [{"nome": "Ana Ferreira", "n_fatura": None, "valor": 2100, "estado": "sem_fatura"}],
}

# ---------------------------------------------------------------------------
# QUERIES BD
# ---------------------------------------------------------------------------

def _get_consultores() -> list[dict]:
    if not SUPABASE_OK:
        return _MOCK_CONSULTORES
    try:
        r = get_supabase().table("profiles").select("id, nome, nif, iban, email").eq("role", "gestor_projeto").execute()
        return r.data
    except Exception:
        return _MOCK_CONSULTORES


def _get_acoes_fechadas_sem_nh(consultor_id: Optional[str] = None) -> list[dict]:
    """Ações fechadas que ainda não têm NH emitida."""
    if not SUPABASE_OK:
        dados = [a for a in _MOCK_ACOES_FECHADAS if not a["nh_emitida"]]
        if consultor_id:
            dados = [a for a in dados if a["consultor_id"] == consultor_id]
        return dados
    try:
        q = get_supabase().table("acoes").select(
            "id, magna_id, nome, empresa_cliente, codigo, data_inicio, data_fim, "
            "volume_horas, formandos_certificados, coordenador_id, "
            "profiles!coordenador_id(nome, email)"
        ).eq("estado", "fechada")
        if consultor_id:
            q = q.eq("coordenador_id", consultor_id)
        r = q.execute()
        # Filtrar as que já têm NH — verificar na tabela faturacao_consultores
        nh_r = get_supabase().table("faturacao_consultores").select("acao_id").neq("estado", "disponivel").execute()
        nh_ids = {row["acao_id"] for row in nh_r.data}
        return [a for a in r.data if a["id"] not in nh_ids]
    except Exception:
        return []


def _get_nh_emitidas(consultor_id: Optional[str] = None) -> list[dict]:
    """NH emitidas a aguardar fatura do consultor."""
    if not SUPABASE_OK:
        dados = _MOCK_NH_EMITIDAS
        if consultor_id:
            dados = [n for n in dados if n["consultor_id"] == consultor_id]
        return dados
    try:
        q = get_supabase().table("faturacao_consultores").select(
            "id, consultor_id, valor, estado, created_at, "
            "profiles!consultor_id(nome, email), acoes(nome, magna_id)"
        ).in_("estado", ["selecionada", "aguarda_confirmacao", "confirmada"])
        if consultor_id:
            q = q.eq("consultor_id", consultor_id)
        r = q.execute()
        return r.data
    except Exception:
        return []


def _get_faturas_consultores_pendentes(consultor_id: Optional[str] = None) -> list[dict]:
    """Faturas de consultores submetidas a aguardar aprovação."""
    if not SUPABASE_OK:
        dados = _MOCK_FATURAS_CONSULTORES
        if consultor_id:
            dados = [f for f in dados if f["consultor_id"] == consultor_id]
        return dados
    try:
        q = get_supabase().table("faturacao_consultores").select(
            "id, consultor_id, valor, estado, numero_fatura, created_at, ficheiro_fatura_url, "
            "profiles!consultor_id(nome, email), acoes(nome, magna_id)"
        ).eq("estado", "fatura_emitida")
        if consultor_id:
            q = q.eq("consultor_id", consultor_id)
        r = q.execute()
        return r.data
    except Exception:
        return []


def _get_formadores_acao(acao_id: str) -> list[dict]:
    """Formadores associados a uma ação e estado das suas faturas."""
    if not SUPABASE_OK:
        return _MOCK_FORMADORES_ACAO.get(acao_id, [])
    try:
        r = get_supabase().table("faturas").select(
            "numero_fatura, valor, estado, profiles!formador_id(nome)"
        ).eq("acao_id", acao_id).execute()
        return [{"nome": (row.get("profiles") or {}).get("nome") or "—",
                 "n_fatura": row.get("numero_fatura"),
                 "valor": row.get("valor") or 0,
                 "estado": row.get("estado")} for row in r.data]
    except Exception:
        return []


def _aprovar_fatura_consultor(fc_id: str, user_nome: str) -> bool:
    if not SUPABASE_OK:
        return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({
            "estado": "paga",
            "confirmada_financeiro_em": datetime.utcnow().isoformat(),
            "notas": f"Aprovado por {user_nome}",
        }).eq("id", fc_id).execute()
        _log_evento("fatura_consultor_aprovada", f"Fatura consultor {fc_id} aprovada por {user_nome}", {"fc_id": fc_id})
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False


def _rejeitar_fatura_consultor(fc_id: str, motivo: str, user_nome: str) -> bool:
    if not SUPABASE_OK:
        return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({
            "estado": "confirmada",  # volta ao estado anterior
            "notas": f"Rejeitado por {user_nome}: {motivo}",
        }).eq("id", fc_id).execute()
        _log_evento("fatura_consultor_rejeitada", f"Fatura consultor {fc_id} rejeitada: {motivo}", {"fc_id": fc_id, "motivo": motivo})
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def fmt_eur(valor) -> str:
    try:
        return f"€ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "€ —"


def secao_header(titulo: str, subtitulo: str = ""):
    st.markdown(f"### {titulo}")
    if subtitulo:
        st.caption(subtitulo)
    st.markdown(
        "<div style='height:3px;background:linear-gradient(90deg,#E5E7EB,transparent);"
        "border-radius:2px;margin-bottom:16px'></div>",
        unsafe_allow_html=True,
    )


ESTADO_COR_FC = {
    "aguarda_fatura":    ("#FEF3C7", "#92400E", "Aguarda fatura"),
    "aguarda_aprovacao": ("#FEF3C7", "#92400E", "Aguarda aprovação"),
    "fatura_emitida":    ("#DBEAFE", "#1E40AF", "Fatura emitida"),
    "confirmada":        ("#D1FAE5", "#065F46", "Confirmada"),
    "paga":              ("#D1FAE5", "#065F46", "Paga"),
}

def badge_fc(estado: str) -> str:
    bg, color, label = ESTADO_COR_FC.get(estado, ("#F3F4F6", "#374151", estado))
    return f"<span style='background:{bg};color:{color};padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500'>{label}</span>"


# ---------------------------------------------------------------------------
# RENDER PRINCIPAL DA TAB
# ---------------------------------------------------------------------------

def render_consultores(user: dict):
    user_nome = user.get("nome") or "Financeiro"

    consultores = _get_consultores()

    # Filtro por consultor
    col_f, _ = st.columns([2, 4])
    with col_f:
        opcoes = ["Todos"] + [c["nome"] for c in consultores]
        filtro_nome = st.selectbox("Filtrar por consultor", opcoes, key="filtro_consultor")

    filtro_id = None
    if filtro_nome != "Todos":
        match = [c for c in consultores if c["nome"] == filtro_nome]
        if match:
            filtro_id = match[0]["id"]

    # Métricas rápidas
    acoes_sem_nh   = _get_acoes_fechadas_sem_nh(filtro_id)
    nh_emitidas    = _get_nh_emitidas(filtro_id)
    fat_pendentes  = _get_faturas_consultores_pendentes(filtro_id)

    c1, c2, c3 = st.columns(3)
    c1.metric("📋 Ações sem NH",         len(acoes_sem_nh),   "fechadas")
    c2.metric("📄 NH emitidas",          len(nh_emitidas),    "a aguardar fatura")
    c3.metric("⏳ Faturas a aprovar",    len(fat_pendentes),  "submetidas")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- SECÇÃO 1: AÇÕES FECHADAS SEM NH ----
    secao_header(
        f"📋 Ações fechadas sem NH ({len(acoes_sem_nh)})",
        "Seleciona as ações para incluir numa nota de honorários."
    )

    if not acoes_sem_nh:
        st.success("Todas as ações fechadas já têm NH emitida.")
    else:
        # Agrupar por consultor
        consultores_com_acoes = {}
        for a in acoes_sem_nh:
            cid = a.get("consultor_id") or "—"
            if cid not in consultores_com_acoes:
                consultores_com_acoes[cid] = []
            consultores_com_acoes[cid].append(a)

        for cid, acoes in consultores_com_acoes.items():
            # Nome do consultor
            c_match = [c for c in consultores if c["id"] == cid]
            c_nome  = c_match[0]["nome"] if c_match else cid

            with st.expander(f"**{c_nome}** — {len(acoes)} ação(ões)", expanded=True):
                selecionadas = []
                for a in acoes:
                    ch        = int(a.get("volume_horas") or 0)
                    formandos = int(a.get("formandos_certificados") or 0)
                    valor     = calcular_valor_acao(ch, formandos) if SUPABASE_OK else (ch * formandos * (3.12 if formandos >= 13 else 2.50))
                    projeto   = a.get("projeto") or "—"

                    col_check, col_info, col_form, col_val = st.columns([0.5, 4, 3, 1.5])
                    sel = col_check.checkbox("", key=f"sel_{a['id']}", label_visibility="collapsed")
                    if sel:
                        selecionadas.append(a)

                    col_info.markdown(
                        f"**{a.get('codigo') or '—'}** — {a.get('nome') or '—'}<br>"
                        f"<span style='font-size:12px;color:#6B7280'>`{projeto}` · {a.get('empresa_cliente') or '—'} · "
                        f"{a.get('data_inicio') or '—'} → {a.get('data_fim') or '—'} · {ch}h · {formandos} form.</span>",
                        unsafe_allow_html=True,
                    )

                    # Formadores da ação
                    formadores = _get_formadores_acao(a["id"])
                    if formadores:
                        forms_txt = " | ".join([
                            f"{f['nome']} ({f['estado']})" for f in formadores
                        ])
                        col_form.markdown(
                            f"<span style='font-size:11px;color:#6B7280'>👤 {forms_txt}</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        col_form.markdown("<span style='font-size:11px;color:#9CA3AF'>Sem formadores</span>", unsafe_allow_html=True)

                    col_val.markdown(f"<div style='margin-top:6px;text-align:right'><strong>{fmt_eur(valor)}</strong></div>", unsafe_allow_html=True)

                # Botão gerar NH para este consultor
                acoes_sel_key = f"acoes_sel_{cid}"
                acoes_selecionadas = [a for a in acoes if st.session_state.get(f"sel_{a['id']}", False)]

                if acoes_selecionadas:
                    total_sel = sum(
                        calcular_valor_acao(int(a.get("volume_horas") or 0), int(a.get("formandos_certificados") or 0))
                        if SUPABASE_OK else
                        int(a.get("volume_horas") or 0) * int(a.get("formandos_certificados") or 0) * (3.12 if int(a.get("formandos_certificados") or 0) >= 13 else 2.50)
                        for a in acoes_selecionadas
                    )
                    st.markdown(f"**{len(acoes_selecionadas)} ação(ões) selecionada(s) · Total: {fmt_eur(total_sel)}**")

                    if st.button(f"📄 Gerar NH para {c_nome}", key=f"gerar_nh_{cid}", type="primary"):
                        try:
                            c_data = c_match[0] if c_match else {"nome": c_nome, "nif": "—", "iban": "—"}
                            # Próximo número NH (mock: contar NHs existentes + 1)
                            nh_num = len(_MOCK_NH_EMITIDAS) + 1

                            # Projeto — usar o da primeira ação
                            proj_nome = acoes_selecionadas[0].get("projeto") or "—"
                            proj_codigo = acoes_selecionadas[0].get("magna_id") or "—"

                            from app.gerar_nh import construir_dados_nh, gerar_nh
                            dados_nh = construir_dados_nh(
                                nh_numero=nh_num,
                                consultor=c_data,
                                projeto={"nome": proj_nome, "magna_id": proj_codigo},
                                acoes=acoes_selecionadas,
                            )
                            docx_bytes = gerar_nh(dados_nh)

                            nome_ficheiro = f"NH{nh_num}_{c_nome.replace(' ', '_')[:20]}.docx"
                            st.download_button(
                                f"⬇️ Download NH{nh_num}",
                                docx_bytes,
                                nome_ficheiro,
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_nh_{cid}",
                            )
                            st.success(f"NH{nh_num} gerada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao gerar NH: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- SECÇÃO 2: NH EMITIDAS A AGUARDAR FATURA ----
    secao_header(
        f"📄 NH emitidas — a aguardar fatura ({len(nh_emitidas)})",
        "NH enviadas ao consultor. A aguardar submissão da fatura na plataforma."
    )

    if not nh_emitidas:
        st.info("Nenhuma NH emitida a aguardar fatura.")
    else:
        for row in nh_emitidas:
            c_nome   = row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            projeto  = row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            valor    = row.get("valor") or 0
            estado   = row.get("estado") or "aguarda_fatura"
            data_em  = str(row.get("data_emissao") or row.get("created_at") or "—")[:10]

            with st.container(border=True):
                cc1, cc2, cc3 = st.columns([4, 2, 2])
                cc1.markdown(
                    f"**{c_nome}**<br>"
                    f"<span style='font-size:12px;color:#6B7280'>Projeto: `{projeto}` · Emitida: {data_em}</span>",
                    unsafe_allow_html=True,
                )
                cc2.markdown(f"<div style='margin-top:4px'><strong>{fmt_eur(valor)}</strong></div>", unsafe_allow_html=True)
                cc3.markdown(f"<div style='margin-top:4px'>{badge_fc(estado)}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- SECÇÃO 3: FATURAS CONSULTORES A APROVAR ----
    secao_header(
        f"⏳ Faturas de consultores a aprovar ({len(fat_pendentes)})",
        "Faturas submetidas pelos consultores após receberem a NH."
    )

    if not fat_pendentes:
        st.success("Nenhuma fatura de consultor pendente de aprovação.")
    else:
        for i, row in enumerate(fat_pendentes):
            fc_id      = row.get("id") or str(i)
            c_nome     = row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            c_email    = (row.get("profiles") or {}).get("email") or ""
            projeto    = row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            valor      = row.get("valor") or 0
            n_fatura   = row.get("numero_fatura") or "—"
            data_sub   = str(row.get("data_submissao") or row.get("created_at") or "—")[:10]
            ficheiro   = row.get("ficheiro_url") or row.get("ficheiro_fatura_url")

            with st.container(border=True):
                col_info, col_pdf, col_acao = st.columns([4, 1, 3])

                with col_info:
                    st.markdown(
                        f"**{c_nome}** &nbsp;<span style='font-size:12px;color:#6B7280'>{n_fatura}</span><br>"
                        f"<span style='font-size:13px'>`{projeto}`&nbsp;·&nbsp;{fmt_eur(valor)}</span><br>"
                        f"<span style='font-size:12px;color:#9CA3AF'>Submetida: {data_sub}</span>",
                        unsafe_allow_html=True,
                    )

                with col_pdf:
                    if ficheiro:
                        st.link_button("📄 Ver PDF", ficheiro)
                    else:
                        st.caption("Sem PDF")

                with col_acao:
                    if st.button("✅ Aprovar", key=f"apr_fc_{i}_{fc_id}", use_container_width=True):
                        if _aprovar_fatura_consultor(fc_id, user_nome):
                            st.toast(f"Fatura de {c_nome} aprovada.")
                            st.rerun()

                    motivo = st.text_input("Motivo", key=f"motivo_fc_{i}_{fc_id}",
                                           placeholder="Motivo de rejeição...", label_visibility="collapsed")
                    if st.button("❌ Rejeitar", key=f"rej_fc_{i}_{fc_id}", use_container_width=True):
                        if motivo:
                            if _rejeitar_fatura_consultor(fc_id, motivo, user_nome):
                                st.toast(f"Fatura de {c_nome} rejeitada. Notificação enviada. (A ligar Gmail API)")
                                st.rerun()
                        else:
                            st.warning("Escreve um motivo antes de rejeitar.")
