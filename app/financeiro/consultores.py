"""Tab Consultores — página do financeiro."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import (
    eur, ptag, bdg, kpi_h, sec, div, CORES, BGS,
    ordenar, fil_proj, fil_datas, excel_bytes, extrair_pdf,
    guardar_comprovativo, notificar_rejeicao, reg_hist,
    _formador, _projeto, _email, ORDEM, PLOTLY_CFG,
)

from datetime import datetime

try:
    from app.db_financeiro import get_supabase, get_supabase_admin, _log_evento
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False



try:
    from app.db_financeiro import get_supabase, get_supabase_admin, _log_evento
    from app.gerar_nh import construir_dados_nh, gerar_nh, calcular_valor_acao
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False
    def calcular_valor_acao(ch, f): return ch * f * (3.12 if f >= 13 else 2.50)

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_CONS = [
    {"id":"c1","nome":"Etapas Pioneiras, Lda",   "nif":"510391125","iban":"PT50004513454025352458285","email":"etapas@demo.pt"},
    {"id":"c2","nome":"Winet Consulting, Lda",   "nif":"509812345","iban":"PT50001234567890123456789","email":"winet@demo.pt"},
    {"id":"c3","nome":"FormaConsult, Unip. Lda", "nif":"511234567","iban":"PT50009876543210987654321","email":"formaconsult@demo.pt"},
]
_MOCK_ACOES = [
    {"id":"a1","magna_id":"ASE:OSEMC_30.1","nome":"Op. Seg. Equip. Movimentação Cargas 1","empresa_cliente":"J.A. Veiga de Macedo","codigo":"ASE:OSEMC_30.1","data_inicio":"2026-03-19","data_fim":"2026-04-17","volume_horas":30,"formandos_certificados":16,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a2","magna_id":"ASE:OSEMC_30.2","nome":"Op. Seg. Equip. Movimentação Cargas 2","empresa_cliente":"J.A. Veiga de Macedo/Z Cork","codigo":"ASE:OSEMC_30.2","data_inicio":"2026-03-19","data_fim":"2026-04-16","volume_horas":30,"formandos_certificados":15,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a3","magna_id":"GEOEMC_8","nome":"Gestão Eficiente de Equipamentos","empresa_cliente":"Manuaço","codigo":"GEOEMC_8","data_inicio":"2026-02-06","data_fim":"2026-02-13","volume_horas":8,"formandos_certificados":10,"consultor_id":"c2","projeto":"ANIET","nh_emitida":False},
    {"id":"a4","magna_id":"LGE_12","nome":"Liderança e gestão de equipas","empresa_cliente":"Fenabel, S.A","codigo":"LGE_12","data_inicio":"2026-01-05","data_fim":"2026-01-19","volume_horas":12,"formandos_certificados":14,"consultor_id":"c2","projeto":"MENTORES","nh_emitida":True},
    {"id":"a5","magna_id":"TN_16","nome":"Técnicas de negociação","empresa_cliente":"Fenabel, S.A","codigo":"TN_16","data_inicio":"2026-03-09","data_fim":"2026-03-30","volume_horas":16,"formandos_certificados":10,"consultor_id":"c3","projeto":"MENTORES","nh_emitida":False},
]
_MOCK_NH = [
    {"id":"nh1","consultor_id":"c2","consultor_nome":"Winet Consulting, Lda","projeto":"MENTORES","valor":1646.40,"data_emissao":"2026-05-10","estado":"aguarda_fatura","nh_paga":False,"paga_em":None,"paga_por":None},
    {"id":"nh2","consultor_id":"c1","consultor_nome":"Etapas Pioneiras, Lda","projeto":"PRODUTECH","valor":2901.60,"data_emissao":"2026-04-20","estado":"paga","nh_paga":True,"paga_em":"2026-05-01","paga_por":"Financeiro"},
]
_MOCK_FC = [
    {"id":"fc1","consultor_id":"c1","consultor_nome":"Etapas Pioneiras, Lda","projeto":"PRODUTECH","numero_fatura":"FT-EC-2026/001","valor":2901.60,"estado":"aguarda_aprovacao","data_submissao":"2026-05-20","ficheiro_url":None},
]
# Formadores por ação (acao_id -> lista de formadores)
_MOCK_FORM_ACAO = {
    "a1": [{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0142","valor":3200,"estado":"aprovada","projeto":"PRODUTECH"}],
    "a2": [{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0138","valor":2800,"estado":"submetida","projeto":"PRODUTECH"}],
    "a3": [{"nome":"Ana Ferreira",                "n_fatura":None,         "valor":2100,"estado":"sem_fatura","projeto":"ANIET"}],
    "a4": [{"nome":"Fátima Sorte",                "n_fatura":"FT2026/0131","valor":4100,"estado":"paga",      "projeto":"MENTORES"}],
    "a5": [{"nome":"Fátima Sorte",                "n_fatura":"FT2026/0125","valor":1900,"estado":"submetida", "projeto":"MENTORES"}],
}

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_cons():
    if not SUPABASE_OK: return _MOCK_CONS
    try:
        return get_supabase().table("profiles").select("id,nome,nif,iban,email").eq("role","gestor_projeto").execute().data
    except: return _MOCK_CONS

def _get_acoes_por_consultor(cid=None):
    """Todas as ações (fechadas ou não) de um consultor."""
    if not SUPABASE_OK:
        return [a for a in _MOCK_ACOES if a["consultor_id"]==cid] if cid else _MOCK_ACOES
    try:
        q = get_supabase().table("acoes").select(
            "id,magna_id,nome,empresa_cliente,codigo,data_inicio,data_fim,"
            "volume_horas,formandos_certificados,estado,coordenador_id"
        )
        if cid: q = q.eq("coordenador_id", cid)
        return q.execute().data
    except: return []

def _get_acoes_sem_nh(cid=None):
    if not SUPABASE_OK:
        d = [a for a in _MOCK_ACOES if not a["nh_emitida"]]
        return [a for a in d if a["consultor_id"]==cid] if cid else d
    try:
        q = get_supabase().table("acoes").select(
            "id,magna_id,nome,empresa_cliente,codigo,data_inicio,data_fim,volume_horas,formandos_certificados,coordenador_id"
        ).eq("estado","fechada")
        if cid: q = q.eq("coordenador_id", cid)
        r = q.execute()
        nh_ids = {x["acao_id"] for x in get_supabase().table("faturacao_consultores").select("acao_id").neq("estado","disponivel").execute().data}
        return [a for a in r.data if a["id"] not in nh_ids]
    except: return []

def _get_nh(cid=None):
    if not SUPABASE_OK:
        d = _MOCK_NH
        return [n for n in d if n["consultor_id"]==cid] if cid else d
    try:
        q = get_supabase().table("faturacao_consultores").select(
            "id,consultor_id,valor,estado,created_at,notas,profiles!consultor_id(nome),acoes(nome)"
        ).in_("estado",["selecionada","aguarda_confirmacao","confirmada","paga"])
        if cid: q = q.eq("consultor_id", cid)
        return q.execute().data
    except: return []

def _get_faturas_consultores_pendentes(cid=None):
    if not SUPABASE_OK:
        d = _MOCK_FC
        return [f for f in d if f["consultor_id"]==cid] if cid else d
    try:
        q = get_supabase().table("faturacao_consultores").select(
            "id,consultor_id,valor,estado,numero_fatura,created_at,ficheiro_fatura_url,profiles!consultor_id(nome,email),acoes(nome)"
        ).eq("estado","fatura_emitida")
        if cid: q = q.eq("consultor_id", cid)
        return q.execute().data
    except: return []

def _get_form_acao(aid):
    if not SUPABASE_OK: return _MOCK_FORM_ACAO.get(aid, [])
    try:
        r = get_supabase().table("faturas").select(
            "numero_fatura,valor,estado,profiles!formador_id(nome),acoes(nome)"
        ).eq("acao_id", aid).execute()
        return [{"nome":(x.get("profiles") or {}).get("nome") or "—",
                 "n_fatura":x.get("numero_fatura"),"valor":x.get("valor") or 0,
                 "estado":x.get("estado"),"projeto":(x.get("acoes") or {}).get("nome") or "—"} for x in r.data]
    except: return []

def _marcar_nh_paga(nh_id, user_nome):
    if not SUPABASE_OK:
        for n in st.session_state.mock_nh:
            if n["id"] == nh_id:
                n["nh_paga"] = True
                n["estado"] = "paga"
                n["paga_em"] = datetime.now().strftime("%Y-%m-%d")
                n["paga_por"] = user_nome
        return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({
            "estado": "paga",
            "paga_em": datetime.utcnow().isoformat(),
            "notas": f"NH paga por {user_nome}",
        }).eq("id", nh_id).execute()
        _log_evento("nh_paga", f"NH {nh_id} marcada como paga por {user_nome}", {"nh_id": nh_id})
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def _aprovar_fc(fc_id, user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({
            "estado":"paga","confirmada_financeiro_em":datetime.utcnow().isoformat()
        }).eq("id",fc_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def _rejeitar_fc(fc_id, motivo, user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({
            "estado":"confirmada","notas":f"Rejeitado: {motivo}"
        }).eq("id",fc_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render_consultores(user: dict):
    user_nome = user.get("nome") or "Financeiro"

    # Init mock state
    if not SUPABASE_OK and "mock_nh" not in st.session_state:
        st.session_state.mock_nh = list(_MOCK_NH)

    consultores = _get_cons()

    col_f, _ = st.columns([2, 4])
    with col_f:
        filtro = st.selectbox("Filtrar por consultor", ["Todos"] + [c["nome"] for c in consultores], key="fil_cons")

    cid = None
    if filtro != "Todos":
        m = [c for c in consultores if c["nome"] == filtro]
        if m: cid = m[0]["id"]

    sem_nh = _get_acoes_sem_nh(cid)
    nh_em  = st.session_state.mock_nh if not SUPABASE_OK else _get_nh(cid)
    if cid and not SUPABASE_OK:
        nh_em = [n for n in nh_em if n["consultor_id"] == cid]
    fat_p  = _get_faturas_consultores_pendentes(cid)
    nh_pagas   = len([n for n in nh_em if n.get("nh_paga") or n.get("estado") == "paga"])
    nh_pend    = len([n for n in nh_em if not n.get("nh_paga") and n.get("estado") != "paga"])

    st.html(
        '<div class="fin-kpi-row">'
        + kpi_h("📋 Ações sem NH",      str(len(sem_nh)), "fechadas",           "a")
        + kpi_h("📄 NH pendentes",       str(nh_pend),     "por pagar",          "b")
        + kpi_h("✅ NH pagas",            str(nh_pagas),    "liquidadas",         "g")
        + kpi_h("⏳ Faturas a aprovar",   str(len(fat_p)),  "submetidas",         "p")
        + '</div>'
    )

    st.html(div())

    # ================================================================
    # SECÇÃO 1 — AÇÕES SEM NH
    # ================================================================
    st.markdown(sec(f"📋 Ações fechadas sem NH ({len(sem_nh)})", "Seleciona as ações para gerar uma nota de honorários."), unsafe_allow_html=True)

    if not sem_nh:
        st.html('<div class="fin-empty">✅ Todas as ações fechadas já têm NH emitida.</div>')
    else:
        grupos = {}
        for a in sem_nh:
            grupos.setdefault(a.get("consultor_id") or "—", []).append(a)

        for gid, acoes in grupos.items():
            cm = [c for c in consultores if c["id"] == gid]
            c_nome = cm[0]["nome"] if cm else gid

            with st.expander(f"**{c_nome}** — {len(acoes)} ação(ões)", expanded=True):
                for a in acoes:
                    ch = int(a.get("volume_horas") or 0)
                    fm = int(a.get("formandos_certificados") or 0)
                    v  = calcular_valor_acao(ch, fm)
                    pr = a.get("projeto") or "—"

                    cc, ci, cf_, cv = st.columns([0.5, 4, 3, 1.5])
                    cc.checkbox("", key=f"sel_{a['id']}", label_visibility="collapsed")
                    ci.markdown(
                        f'<div style="padding:3px 0">'
                        f'<span style="font-weight:600;font-size:13px">{a.get("codigo") or "—"}</span>&nbsp;{ptag(pr)}<br>'
                        f'<span style="font-size:11px;color:#8B94A3">{a.get("empresa_cliente") or "—"} · {a.get("data_inicio") or "—"} → {a.get("data_fim") or "—"} · {ch}h · {fm} form.</span>'
                        f'</div>', unsafe_allow_html=True
                    )
                    forms = _get_form_acao(a["id"])
                    if forms:
                        fh = " · ".join([f"{f['nome']}&nbsp;{bdg(f['estado'])}" for f in forms])
                        cf_.markdown(f"<div style='font-size:11px;color:#6B7280;padding-top:5px'>{fh}</div>", unsafe_allow_html=True)
                    cv.markdown(f"<div style='text-align:right;padding-top:5px;font-weight:700;font-size:14px'>{eur(v)}</div>", unsafe_allow_html=True)

                sel_acoes = [a for a in acoes if st.session_state.get(f"sel_{a['id']}", False)]
                if sel_acoes:
                    total = sum(calcular_valor_acao(int(a.get("volume_horas") or 0), int(a.get("formandos_certificados") or 0)) for a in sel_acoes)
                    st.markdown(f"<div style='font-size:13px;color:#4B5263;margin:6px 0'><strong>{len(sel_acoes)} selecionada(s)</strong> · Total: <strong>{eur(total)}</strong></div>", unsafe_allow_html=True)
                    if st.button(f"📄 Gerar NH — {c_nome}", key=f"gnh_{gid}", type="primary"):
                        try:
                            c_data = cm[0] if cm else {"nome":c_nome,"nif":"—","iban":"—"}
                            nh_num = len(st.session_state.mock_nh if not SUPABASE_OK else _MOCK_NH) + 1
                            pr_nome = sel_acoes[0].get("projeto") or "—"
                            pr_cod  = sel_acoes[0].get("magna_id") or "—"
                            from app.gerar_nh import construir_dados_nh, gerar_nh
                            dados_nh = construir_dados_nh(nh_num, c_data, {"nome":pr_nome,"magna_id":pr_cod}, sel_acoes)
                            docx = gerar_nh(dados_nh)
                            st.download_button(f"⬇️ Download NH{nh_num}", docx, f"NH{nh_num}_{c_nome[:20].replace(' ','_')}.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_{gid}")
                            st.success(f"NH{nh_num} gerada!")
                        except Exception as e: st.error(f"Erro: {e}")

    st.html(div())

    # ================================================================
    # SECÇÃO 2 — NH EMITIDAS (com estado de pagamento)
    # ================================================================
    st.markdown(sec(f"📄 Notas de Honorários ({len(nh_em)})", "Estado de pagamento das NH emitidas aos consultores."), unsafe_allow_html=True)

    if not nh_em:
        st.html('<div class="fin-empty">Nenhuma NH emitida.</div>')
    else:
        for i, row in enumerate(nh_em):
            nh_id   = row.get("id") or str(i)
            cn      = row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            pr      = row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            v       = row.get("valor") or 0
            de      = str(row.get("data_emissao") or row.get("created_at") or "—")[:10]
            paga    = row.get("nh_paga") or row.get("estado") == "paga"
            paga_em = row.get("paga_em") or ""
            paga_por= row.get("paga_por") or ""

            col_info, col_acao = st.columns([5, 2])
            with col_info:
                cls_card = "nh-row nh-paga" if paga else "nh-row nh-pendente"
                paga_txt = f'&nbsp;·&nbsp;<span style="font-size:11px;color:#16A34A">Paga em {paga_em[:10]} por {paga_por}</span>' if paga and paga_em else ""
                st.html(
                    f'<div class="{cls_card}">'
                    f'<div style="flex:1">'
                    f'<div style="font-weight:600;font-size:14px">{cn}</div>'
                    f'<div style="font-size:12px;color:#8B94A3">{ptag(pr)} · Emitida: {de}{paga_txt}</div>'
                    f'</div>'
                    f'<div style="text-align:right;margin-right:10px">'
                    f'<div style="font-weight:700;font-size:15px">{eur(v)}</div>'
                    f'</div>'
                    f'{bdg("nh_paga" if paga else "nh_pendente")}'
                    f'</div>'
                )
            with col_acao:
                if not paga:
                    if st.button("💳 Marcar NH como paga", key=f"pnh_{i}_{nh_id}", use_container_width=True):
                        if _marcar_nh_paga(nh_id, user_nome):
                            st.toast(f"NH de {cn} marcada como paga.")
                            st.rerun()
                else:
                    st.markdown("<div style='padding-top:8px;font-size:12px;color:#16A34A;text-align:center'>✅ NH liquidada</div>", unsafe_allow_html=True)

    st.html(div())

    # ================================================================
    # SECÇÃO 3 — FATURAS A APROVAR
    # ================================================================
    st.markdown(sec(f"⏳ Faturas a aprovar ({len(fat_p)})", "Faturas submetidas pelos consultores após receberem a NH."), unsafe_allow_html=True)

    if not fat_p:
        st.html('<div class="fin-empty">✅ Nenhuma fatura de consultor pendente.</div>')
    else:
        for i, row in enumerate(fat_p):
            fid  = row.get("id") or str(i)
            cn   = row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            pr   = row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            v    = row.get("valor") or 0
            nf   = row.get("numero_fatura") or "—"
            ds   = str(row.get("data_submissao") or row.get("created_at") or "—")[:10]
            fich = row.get("ficheiro_url") or row.get("ficheiro_fatura_url")

            ci, cpdf, ca = st.columns([4, 1, 3])
            with ci:
                st.html(
                    f'<div class="fin-aprov">'
                    f'<div style="font-weight:700;font-size:14px">{cn} <span style="font-size:12px;font-weight:400;color:#8B94A3">{nf}</span></div>'
                    f'<div style="font-size:13px;color:#4B5263">{ptag(pr)} · {eur(v)}</div>'
                    f'<div class="ds">Submetida: {ds}</div>'
                    f'</div>'
                )
            with cpdf:
                st.markdown("<div style='margin-top:10px'>", unsafe_allow_html=True)
                if fich: st.link_button("📄", fich)
                else: st.caption("—")
                st.markdown("</div>", unsafe_allow_html=True)
            with ca:
                st.markdown("<div style='margin-top:10px'>", unsafe_allow_html=True)
                if st.button("✅ Aprovar", key=f"afc_{i}_{fid}", use_container_width=True):
                    if _aprovar_fc(fid, user_nome):
                        st.toast(f"Fatura de {cn} aprovada."); st.rerun()
                mot = st.text_input("", key=f"mfc_{i}_{fid}", placeholder="Motivo de rejeição…", label_visibility="collapsed")
                if st.button("❌ Rejeitar", key=f"rfc_{i}_{fid}", use_container_width=True):
                    if mot:
                        if _rejeitar_fc(fid, mot, user_nome):
                            st.toast(f"Fatura de {cn} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo.")
                st.markdown("</div>", unsafe_allow_html=True)

    st.html(div())

    # ================================================================
    # SECÇÃO 4 — FORMADORES POR CONSULTOR
    # ================================================================
    st.markdown(sec("👤 Formadores por consultor", "Todos os formadores das ações de cada consultor e estado das suas faturas."), unsafe_allow_html=True)

    cons_a_mostrar = [c for c in consultores if not cid or c["id"] == cid]

    for cons in cons_a_mostrar:
        acoes_cons = _get_acoes_por_consultor(cons["id"])
        if not acoes_cons:
            continue

        # Agregar formadores de todas as ações deste consultor
        formadores_map = {}  # nome -> lista de {acao, fatura, estado, valor, projeto}
        for a in acoes_cons:
            forms = _get_form_acao(a["id"])
            for f in forms:
                nome = f.get("nome") or "—"
                if nome not in formadores_map:
                    formadores_map[nome] = []
                formadores_map[nome].append({
                    "acao":    a.get("codigo") or a.get("magna_id") or "—",
                    "empresa": a.get("empresa_cliente") or "—",
                    "projeto": f.get("projeto") or a.get("projeto") or "—",
                    "n_fatura":f.get("n_fatura"),
                    "valor":   f.get("valor") or 0,
                    "estado":  f.get("estado") or "sem_fatura",
                })

        if not formadores_map:
            continue

        with st.expander(f"**{cons['nome']}** — {len(formadores_map)} formador(es), {len(acoes_cons)} ação(ões)", expanded=False):
            for nome_form, registos in formadores_map.items():
                total_form = sum(r["valor"] for r in registos)
                # Header do formador
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;'
                    f'padding:10px 0 6px;border-bottom:1px solid #E4E7EF;margin-bottom:6px">'
                    f'<span style="font-weight:700;font-size:14px;flex:1">{nome_form}</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#4B5263">{eur(total_form)}</span>'
                    f'</div>', unsafe_allow_html=True
                )
                # Linhas por ação
                rows_html = ""
                for r in registos:
                    nf_txt = r["n_fatura"] if r["n_fatura"] else "—"
                    rows_html += (
                        f'<div class="form-row">'
                        f'<div class="form-name">{r["acao"]}'
                        f'&nbsp;&nbsp;<span class="form-fat">{r["empresa"]}</span>'
                        f'</div>'
                        f'{ptag(r["projeto"])}'
                        f'&nbsp;&nbsp;<span style="font-size:12px;color:#8B94A3">{nf_txt}</span>'
                        f'&nbsp;&nbsp;<span style="font-weight:600;font-size:13px">{eur(r["valor"])}</span>'
                        f'&nbsp;&nbsp;{bdg(r["estado"])}'
                        f'</div>'
                    )
                st.html(f'<div style="margin-bottom:12px">{rows_html}</div>')

# ---------------------------------------------------------------------------
# TAB CONSULTORES — sem emissão de NH, só aprovação de faturas
# ---------------------------------------------------------------------------
def render_consultores_financeiro(user):
    """Visão do financeiro sobre consultores: recebe faturas com NH associada e aprova."""
    user_nome = user.get("nome") or "Financeiro"

    try:
        from app.financeiro_consultores import (
            _get_cons, _get_nh, _get_faturas_consultores_pendentes,
            _aprovar_fc, _rejeitar_fc, _get_form_acao, _get_acoes_por_consultor,
        )
        consultores    = _get_cons()
        fat_pendentes  = _get_faturas_consultores_pendentes()
        nh_emitidas    = _get_nh()
    except Exception as e:
        st.error(f"Erro ao carregar dados de consultores: {e}")
        return

    # Filtro por consultor
    col_f,_ = st.columns([2,4])
    with col_f:
        filtro = st.selectbox("Filtrar por consultor", ["Todos"]+[c["nome"] for c in consultores], key="fil_cons_fin")

    cid = None
    if filtro != "Todos":
        m = [c for c in consultores if c["nome"]==filtro]
        if m: cid = m[0]["id"]

    if cid:
        fat_pendentes = [f for f in fat_pendentes if f.get("consultor_id")==cid]
        nh_emitidas   = [n for n in nh_emitidas   if n.get("consultor_id")==cid]

    n_pend = len(fat_pendentes)
    n_nh   = len(nh_emitidas)

    st.html(
        '<div class="fin-kpi-row">'
        +kpi_h("⏳ Faturas a aprovar", str(n_pend), "submetidas pelos consultores","a")
        +kpi_h("📄 NH emitidas",       str(n_nh),   "pela gestora","b")
        +'</div>'
    )
    st.html(div())

    # ---- FATURAS A APROVAR ----
    st.markdown(sec(f"⏳ Faturas de consultores a aprovar ({n_pend})",
        "Faturas submetidas após emissão de NH pela gestora."), unsafe_allow_html=True)

    if not fat_pendentes:
        st.html('<div class="fin-empty">✅ Nenhuma fatura de consultor pendente.</div>')
    else:
        for i,row in enumerate(fat_pendentes):
            fid  = row.get("id") or str(i)
            cn   = row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            pr   = row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            v    = row.get("valor") or 0
            nf   = row.get("numero_fatura") or "—"
            ds   = str(row.get("data_submissao") or row.get("created_at") or "—")[:10]
            fich = row.get("ficheiro_url") or row.get("ficheiro_fatura_url")
            # NH associada
            nh_assoc = next((n for n in nh_emitidas if n.get("consultor_id")==row.get("consultor_id")),"—")
            nh_txt = ""
            if isinstance(nh_assoc,dict):
                nh_txt = f'<div style="font-size:12px;color:#2563EB;margin-top:3px">📄 NH associada: {nh_assoc.get("valor","—")} € — emitida pela gestora em {str(nh_assoc.get("data_emissao") or nh_assoc.get("created_at","—"))[:10]}</div>'

            ci,cpdf,ca = st.columns([4,1,3])
            with ci:
                st.html(
                    f'<div class="fin-aprov">'
                    f'<div style="font-weight:700;font-size:14px">{cn} <span style="font-size:12px;font-weight:400;color:#8B94A3">{nf}</span></div>'
                    f'<div style="font-size:13px;color:#4B5263">{ptag(pr)} · {eur(v)}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">Submetida: {ds}</div>'
                    f'{nh_txt}'
                    f'</div>'
                )
            with cpdf:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if fich: st.link_button("📄",fich)
                else: st.caption("—")
                st.markdown("</div>",unsafe_allow_html=True)
            with ca:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                comp_fc=st.file_uploader("",type=["pdf"],key=f"comp_fc_{i}_{fid}",
                                        label_visibility="collapsed",help="Comprovativo (PDF)")
                if st.button("✅ Aprovar",key=f"afc_{i}_{fid}",use_container_width=True):
                    if not comp_fc:
                        st.warning("Carrega o comprovativo.")
                    else:
                        guardar_comprovativo(fid, comp_fc.getvalue(), comp_fc.name, user_nome)
                        if _aprovar_fc(fid,user_nome):
                            st.toast(f"Fatura de {cn} aprovada. Comprovativo guardado.")
                            st.rerun()
                mot = st.text_input("",key=f"mfc_{i}_{fid}",placeholder="Motivo de rejeição…",label_visibility="collapsed")
                if st.button("❌ Rejeitar",key=f"rfc_{i}_{fid}",use_container_width=True):
                    if mot:
                        if _rejeitar_fc(fid,mot,user_nome): st.toast(f"Fatura de {cn} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo.")
                st.markdown("</div>",unsafe_allow_html=True)

    st.html(div())

    # ---- FORMADORES POR CONSULTOR ----
    st.markdown(sec("👤 Formadores por consultor",
        "Formadores associados às ações de cada consultor e estado das suas faturas."),
        unsafe_allow_html=True)

    cons_mostrar = [c for c in consultores if not cid or c["id"]==cid]
    for cons in cons_mostrar:
        try:
            acoes_cons = _get_acoes_por_consultor(cons["id"])
        except: acoes_cons = []
        if not acoes_cons: continue

        formadores_map = {}
        for a in acoes_cons:
            try: forms = _get_form_acao(a["id"])
            except: forms = []
            for f in forms:
                nome = f.get("nome") or "—"
                if nome not in formadores_map: formadores_map[nome] = []
                formadores_map[nome].append({
                    "acao":    a.get("codigo") or a.get("magna_id") or "—",
                    "empresa": a.get("empresa_cliente") or "—",
                    "projeto": f.get("projeto") or a.get("projeto") or "—",
                    "n_fatura":f.get("n_fatura"),
                    "valor":   f.get("valor") or 0,
                    "estado":  f.get("estado") or "sem_fatura",
                })

        if not formadores_map: continue

        with st.expander(f"**{cons['nome']}** — {len(formadores_map)} formador(es)", expanded=False):
            for nome_form, registos in formadores_map.items():
                total_form = sum(r["valor"] for r in registos)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;padding:8px 0 6px;'
                    f'border-bottom:1px solid #E4E7EF;margin-bottom:6px">'
                    f'<span style="font-weight:700;font-size:14px;flex:1">{nome_form}</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#4B5263">{eur(total_form)}</span>'
                    f'</div>', unsafe_allow_html=True
                )
                rows_html = ""
                for r in registos:
                    from app.financeiro_consultores import bdg as cons_bdg, ptag as cons_ptag
                    nf_txt = r["n_fatura"] if r["n_fatura"] else "—"
                    rows_html += (
                        f'<div style="display:flex;align-items:center;gap:8px;padding:7px 0;'
                        f'border-bottom:1px solid #F0F2F5;font-size:13px">'
                        f'<div style="flex:1;color:#1A1F2E">{r["acao"]}'
                        f'<span style="font-size:12px;color:#8B94A3;margin-left:6px">{r["empresa"]}</span>'
                        f'</div>'
                        f'{cons_ptag(r["projeto"])}'
                        f'<span style="font-size:12px;color:#8B94A3;margin-left:6px">{nf_txt}</span>'
                        f'<span style="font-weight:600;font-size:13px;margin-left:6px">{eur(r["valor"])}</span>'
                        f'<span style="margin-left:6px">{cons_bdg(r["estado"])}</span>'
                        f'</div>'
                    )
                st.html(f'<div style="margin-bottom:14px">{rows_html}</div>')
