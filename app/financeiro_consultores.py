"""Tab Consultores — página do financeiro."""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
import streamlit as st

try:
    from app.db_financeiro import get_supabase, get_supabase_admin, _log_evento
    from app.gerar_nh import construir_dados_nh, gerar_nh, calcular_valor_acao
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False
    def calcular_valor_acao(ch,f): return ch*f*(3.12 if f>=13 else 2.50)

try:
    from app.design_financeiro import DESIGN_CSS, proj_tag, badge, fmt_eur, kpi, sec_header, CORES_PROJETO
except Exception:
    DESIGN_CSS=""
    def proj_tag(p): return f"`{p}`"
    def badge(e): return e
    def fmt_eur(v):
        try: return f"€ {float(v):,.0f}".replace(",",".")
        except: return "€ —"
    def kpi(l,v,s,var=""): return f"**{l}**: {v}"
    def sec_header(t,s=""): return t
    CORES_PROJETO={}

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_CONSULTORES=[
    {"id":"c1","nome":"Etapas Pioneiras, Lda",   "nif":"510391125","iban":"PT50004513454025352458285","email":"etapas@demo.pt"},
    {"id":"c2","nome":"Winet Consulting, Lda",   "nif":"509812345","iban":"PT50001234567890123456789","email":"winet@demo.pt"},
    {"id":"c3","nome":"FormaConsult, Unip. Lda", "nif":"511234567","iban":"PT50009876543210987654321","email":"formaconsult@demo.pt"},
]
_MOCK_ACOES=[
    {"id":"a1","magna_id":"ASE:OSEMC_30.1","nome":"Op. Seg. Equip. Movimentação Cargas 1","empresa_cliente":"J.A. Veiga de Macedo","codigo":"ASE:OSEMC_30.1","data_inicio":"2026-03-19","data_fim":"2026-04-17","volume_horas":30,"formandos_certificados":16,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a2","magna_id":"ASE:OSEMC_30.2","nome":"Op. Seg. Equip. Movimentação Cargas 2","empresa_cliente":"J.A. Veiga de Macedo / Z Cork","codigo":"ASE:OSEMC_30.2","data_inicio":"2026-03-19","data_fim":"2026-04-16","volume_horas":30,"formandos_certificados":15,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a3","magna_id":"GEOEMC_8","nome":"Gestão Eficiente de Equipamentos de Movimentação","empresa_cliente":"Manuaço","codigo":"GEOEMC_8","data_inicio":"2026-02-06","data_fim":"2026-02-13","volume_horas":8,"formandos_certificados":10,"consultor_id":"c2","projeto":"ANIET","nh_emitida":False},
    {"id":"a4","magna_id":"LGE_12","nome":"Liderança e gestão de equipas","empresa_cliente":"Fenabel, S.A","codigo":"LGE_12","data_inicio":"2026-01-05","data_fim":"2026-01-19","volume_horas":12,"formandos_certificados":14,"consultor_id":"c2","projeto":"MENTORES","nh_emitida":True},
    {"id":"a5","magna_id":"TN_16","nome":"Técnicas de negociação","empresa_cliente":"Fenabel, S.A","codigo":"TN_16","data_inicio":"2026-03-09","data_fim":"2026-03-30","volume_horas":16,"formandos_certificados":10,"consultor_id":"c3","projeto":"MENTORES","nh_emitida":False},
]
_MOCK_NH=[
    {"id":"nh1","consultor_id":"c2","consultor_nome":"Winet Consulting, Lda","projeto":"MENTORES","valor":1646.40,"data_emissao":"2026-05-10","estado":"aguarda_fatura","acoes":["LGE_12"]},
]
_MOCK_FAT_CONS=[
    {"id":"fc1","consultor_id":"c1","consultor_nome":"Etapas Pioneiras, Lda","projeto":"PRODUTECH","numero_fatura":"FT-EC-2026/001","valor":2901.60,"estado":"aguarda_aprovacao","data_submissao":"2026-05-20","ficheiro_url":None},
]
_MOCK_FORM_ACAO={
    "a1":[{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0142","valor":3200,"estado":"aprovada"}],
    "a2":[{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0138","valor":2800,"estado":"submetida"}],
    "a3":[{"nome":"Ana Ferreira","n_fatura":None,"valor":2100,"estado":"sem_fatura"}],
}

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_consultores():
    if not SUPABASE_OK: return _MOCK_CONSULTORES
    try:
        r=get_supabase().table("profiles").select("id,nome,nif,iban,email").eq("role","gestor_projeto").execute()
        return r.data
    except: return _MOCK_CONSULTORES

def _get_acoes_sem_nh(cid=None):
    if not SUPABASE_OK:
        d=[a for a in _MOCK_ACOES if not a["nh_emitida"]]
        return [a for a in d if a["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("acoes").select("id,magna_id,nome,empresa_cliente,codigo,data_inicio,data_fim,volume_horas,formandos_certificados,coordenador_id,profiles!coordenador_id(nome,email)").eq("estado","fechada")
        if cid: q=q.eq("coordenador_id",cid)
        r=q.execute()
        nh_r=get_supabase().table("faturacao_consultores").select("acao_id").neq("estado","disponivel").execute()
        nh_ids={row["acao_id"] for row in nh_r.data}
        return [a for a in r.data if a["id"] not in nh_ids]
    except: return []

def _get_nh_emitidas(cid=None):
    if not SUPABASE_OK:
        d=_MOCK_NH
        return [n for n in d if n["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("faturacao_consultores").select("id,consultor_id,valor,estado,created_at,profiles!consultor_id(nome,email),acoes(nome,magna_id)").in_("estado",["selecionada","aguarda_confirmacao","confirmada"])
        if cid: q=q.eq("consultor_id",cid)
        return q.execute().data
    except: return []

def _get_faturas_consultores_pendentes(cid=None):
    if not SUPABASE_OK:
        d=_MOCK_FAT_CONS
        return [f for f in d if f["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("faturacao_consultores").select("id,consultor_id,valor,estado,numero_fatura,created_at,ficheiro_fatura_url,profiles!consultor_id(nome,email),acoes(nome,magna_id)").eq("estado","fatura_emitida")
        if cid: q=q.eq("consultor_id",cid)
        return q.execute().data
    except: return []

def _get_formadores_acao(acao_id):
    if not SUPABASE_OK: return _MOCK_FORM_ACAO.get(acao_id,[])
    try:
        r=get_supabase().table("faturas").select("numero_fatura,valor,estado,profiles!formador_id(nome)").eq("acao_id",acao_id).execute()
        return [{"nome":(row.get("profiles") or {}).get("nome") or "—","n_fatura":row.get("numero_fatura"),"valor":row.get("valor") or 0,"estado":row.get("estado")} for row in r.data]
    except: return []

def _aprovar_fc(fc_id,user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({"estado":"paga","confirmada_financeiro_em":datetime.utcnow().isoformat(),"notas":f"Aprovado por {user_nome}"}).eq("id",fc_id).execute()
        _log_evento("fatura_consultor_aprovada",f"{fc_id} aprovada por {user_nome}",{"fc_id":fc_id})
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def _rejeitar_fc(fc_id,motivo,user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({"estado":"confirmada","notas":f"Rejeitado por {user_nome}: {motivo}"}).eq("id",fc_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render_consultores(user: dict):
    st.markdown(DESIGN_CSS, unsafe_allow_html=True)
    user_nome=user.get("nome") or "Financeiro"
    consultores=_get_consultores()

    col_f,_=st.columns([2,4])
    with col_f:
        opcoes=["Todos"]+[c["nome"] for c in consultores]
        filtro_nome=st.selectbox("Filtrar por consultor",opcoes,key="fil_cons")

    filtro_id=None
    if filtro_nome!="Todos":
        m=[c for c in consultores if c["nome"]==filtro_nome]
        if m: filtro_id=m[0]["id"]

    acoes_sem_nh=_get_acoes_sem_nh(filtro_id)
    nh_emitidas=_get_nh_emitidas(filtro_id)
    fat_pend=_get_faturas_consultores_pendentes(filtro_id)

    st.markdown(
        '<div class="kpi-row">'
        + kpi("📋 Ações sem NH",     str(len(acoes_sem_nh)), "fechadas",          "amber")
        + kpi("📄 NH emitidas",      str(len(nh_emitidas)),  "a aguardar fatura", "blue")
        + kpi("⏳ Faturas a aprovar", str(len(fat_pend)),     "submetidas",        "purple")
        + '</div>', unsafe_allow_html=True
    )

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- AÇÕES SEM NH ----
    st.markdown(sec_header(f"📋 Ações fechadas sem NH ({len(acoes_sem_nh)})","Seleciona as ações para gerar uma nota de honorários."),unsafe_allow_html=True)

    if not acoes_sem_nh:
        st.markdown('<div class="empty-state">✅ Todas as ações fechadas já têm NH emitida.</div>',unsafe_allow_html=True)
    else:
        # Agrupar por consultor
        grupos={}
        for a in acoes_sem_nh:
            cid=a.get("consultor_id") or "—"
            grupos.setdefault(cid,[]).append(a)

        for cid,acoes in grupos.items():
            c_match=[c for c in consultores if c["id"]==cid]
            c_nome=c_match[0]["nome"] if c_match else cid

            with st.expander(f"**{c_nome}** — {len(acoes)} ação(ões)", expanded=True):
                acoes_sel=[]
                for a in acoes:
                    ch=int(a.get("volume_horas") or 0)
                    form=int(a.get("formandos_certificados") or 0)
                    valor=calcular_valor_acao(ch,form)
                    proj=a.get("projeto") or "—"

                    col_chk,col_info,col_form,col_val=st.columns([0.5,4,3,1.5])
                    sel=col_chk.checkbox("",key=f"sel_{a['id']}",label_visibility="collapsed")
                    if sel: acoes_sel.append(a)

                    col_info.markdown(
                        f'<div style="padding:4px 0">'
                        f'<span style="font-weight:600;font-size:13px">{a.get("codigo") or "—"}</span>'
                        f'&nbsp;{proj_tag(proj)}<br>'
                        f'<span style="font-size:12px;color:#8B94A3">{a.get("empresa_cliente") or "—"} · {a.get("data_inicio") or "—"} → {a.get("data_fim") or "—"} · {ch}h · {form} form.</span>'
                        f'</div>', unsafe_allow_html=True
                    )

                    formadores=_get_formadores_acao(a["id"])
                    if formadores:
                        forms_txt=" · ".join([f"{f['nome']} {badge(f['estado'])}" for f in formadores])
                        col_form.markdown(f"<div style='font-size:11px;color:#6B7280;padding-top:6px'>{forms_txt}</div>",unsafe_allow_html=True)

                    col_val.markdown(f"<div style='text-align:right;padding-top:6px;font-weight:700;font-size:14px'>{fmt_eur(valor)}</div>",unsafe_allow_html=True)

                acoes_selecionadas=[a for a in acoes if st.session_state.get(f"sel_{a['id']}",False)]
                if acoes_selecionadas:
                    total_sel=sum(calcular_valor_acao(int(a.get("volume_horas") or 0),int(a.get("formandos_certificados") or 0)) for a in acoes_selecionadas)
                    st.markdown(f"<div style='font-size:13px;color:#4B5263;margin:8px 0'><strong>{len(acoes_selecionadas)} selecionada(s)</strong> · Total: <strong>{fmt_eur(total_sel)}</strong></div>",unsafe_allow_html=True)

                    if st.button(f"📄 Gerar NH — {c_nome}",key=f"gerar_{cid}",type="primary"):
                        try:
                            c_data=c_match[0] if c_match else {"nome":c_nome,"nif":"—","iban":"—"}
                            nh_num=len(_MOCK_NH)+1
                            proj_nome=acoes_selecionadas[0].get("projeto") or "—"
                            proj_cod=acoes_selecionadas[0].get("magna_id") or "—"
                            from app.gerar_nh import construir_dados_nh,gerar_nh
                            dados_nh=construir_dados_nh(nh_num,c_data,{"nome":proj_nome,"magna_id":proj_cod},acoes_selecionadas)
                            docx_bytes=gerar_nh(dados_nh)
                            nome_f=f"NH{nh_num}_{c_nome.replace(' ','_')[:20]}.docx"
                            st.download_button(f"⬇️ Download NH{nh_num}",docx_bytes,nome_f,"application/vnd.openxmlformats-officedocument.wordprocessingml.document",key=f"dl_{cid}")
                            st.success(f"NH{nh_num} gerada!")
                        except Exception as e:
                            st.error(f"Erro ao gerar NH: {e}")

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- NH EMITIDAS ----
    st.markdown(sec_header(f"📄 NH emitidas ({len(nh_emitidas)})","Aguardam que o consultor submeta a fatura."),unsafe_allow_html=True)
    if not nh_emitidas:
        st.markdown('<div class="empty-state">Nenhuma NH emitida a aguardar fatura.</div>',unsafe_allow_html=True)
    else:
        for row in nh_emitidas:
            c_nome=row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            proj=row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            valor=row.get("valor") or 0
            estado=row.get("estado") or "aguarda_fatura"
            data_em=str(row.get("data_emissao") or row.get("created_at") or "—")[:10]
            st.markdown(
                f'<div class="fatura-card" style="margin-bottom:8px">'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:14px">{c_nome}</div>'
                f'<div style="font-size:12px;color:#8B94A3">{proj_tag(proj)} · Emitida: {data_em}</div>'
                f'</div>'
                f'<div style="text-align:right;margin-right:12px">'
                f'<div style="font-weight:700;font-size:15px">{fmt_eur(valor)}</div>'
                f'</div>'
                f'{badge(estado)}'
                f'</div>', unsafe_allow_html=True
            )

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- FATURAS A APROVAR ----
    st.markdown(sec_header(f"⏳ Faturas a aprovar ({len(fat_pend)})","Faturas submetidas pelos consultores após receberem a NH."),unsafe_allow_html=True)
    if not fat_pend:
        st.markdown('<div class="empty-state">✅ Nenhuma fatura de consultor pendente.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(fat_pend):
            fc_id=row.get("id") or str(i)
            c_nome=row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            proj=row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            valor=row.get("valor") or 0
            n_fat=row.get("numero_fatura") or "—"
            data_sub=str(row.get("data_submissao") or row.get("created_at") or "—")[:10]
            ficheiro=row.get("ficheiro_url") or row.get("ficheiro_fatura_url")

            col_info,col_pdf,col_acao=st.columns([4,1,3])
            with col_info:
                st.markdown(
                    f'<div class="aprov-card">'
                    f'<div style="font-weight:700;font-size:14px">{c_nome} &nbsp;<span style="font-size:12px;font-weight:400;color:#8B94A3">{n_fat}</span></div>'
                    f'<div style="font-size:13px;color:#4B5263">{proj_tag(proj)} &nbsp;·&nbsp; {fmt_eur(valor)}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">Submetida: {data_sub}</div>'
                    f'</div>', unsafe_allow_html=True
                )
            with col_pdf:
                st.markdown("<div style='margin-top:12px'>",unsafe_allow_html=True)
                if ficheiro: st.link_button("📄",ficheiro)
                else: st.caption("—")
                st.markdown("</div>",unsafe_allow_html=True)
            with col_acao:
                st.markdown("<div style='margin-top:12px'>",unsafe_allow_html=True)
                if st.button("✅ Aprovar",key=f"apr_fc_{i}_{fc_id}",use_container_width=True):
                    if _aprovar_fc(fc_id,user_nome):
                        st.toast(f"Fatura de {c_nome} aprovada."); st.rerun()
                motivo=st.text_input("",key=f"mot_fc_{i}_{fc_id}",placeholder="Motivo de rejeição…",label_visibility="collapsed")
                if st.button("❌ Rejeitar",key=f"rej_fc_{i}_{fc_id}",use_container_width=True):
                    if motivo:
                        if _rejeitar_fc(fc_id,motivo,user_nome):
                            st.toast(f"Fatura de {c_nome} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo.")
                st.markdown("</div>",unsafe_allow_html=True)
