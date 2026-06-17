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

_CSS = """
<style>
.fin-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 24px}
.fin-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:130px}
.fin-kpi.a{border-top:3px solid #D97706}.fin-kpi.b{border-top:3px solid #2563EB}.fin-kpi.p{border-top:3px solid #7C3AED}
.fin-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.fin-kpi .val{font-size:23px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.fin-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}
.fin-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:10px}
.fin-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.fin-ptag{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px}
.fin-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.fin-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.fin-div{height:1px;background:#E4E7EF;margin:24px 0 20px}
.fin-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px}
.fin-aprov{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:14px;margin-bottom:10px}
.fin-aprov .err{font-size:12px;color:#DC2626;margin-top:3px}
.fin-aprov .ds{font-size:11px;color:#8B94A3;margin-top:2px}
</style>
"""

CORES={"MENTORES":"#2563EB","ANIET":"#16A34A","APCMC":"#D97706","APIMA":"#9D174D","PRODUTECH":"#7C3AED","CALÇADO":"#0F766E"}
BGS={"MENTORES":"#EEF3FD","ANIET":"#F0FDF4","APCMC":"#FFFBEB","APIMA":"#FDF2F8","PRODUTECH":"#F5F3FF","CALÇADO":"#F0FDFA"}

def eur(v):
    try: return f"€\u202f{float(v):,.0f}".replace(",",".")
    except: return "€ —"

def ptag(p):
    c=CORES.get(p,"#6B7280"); b=BGS.get(p,"#F3F4F6")
    return f'<span class="fin-ptag" style="background:{b};color:{c}">{p}</span>'

def bdg(estado):
    M={"aguarda_fatura":("#FFFBEB","#D97706","Aguarda fatura"),
       "aguarda_aprovacao":("#FFFBEB","#D97706","Aguarda aprovação"),
       "fatura_emitida":("#EEF3FD","#2563EB","Fatura emitida"),
       "confirmada":("#F0FDF4","#16A34A","Confirmada"),
       "paga":("#F0FDF4","#16A34A","Paga"),
       "aprovada":("#F0FDF4","#16A34A","Aprovada"),
       "submetida":("#FFFBEB","#D97706","Submetida"),
       "sem_fatura":("#F3F4F6","#6B7280","Sem fatura"),}
    bg,c,l=M.get(estado,("#F3F4F6","#6B7280",estado))
    return f'<span class="fin-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi_h(lbl,val,sub,v=""):
    cls=f"fin-kpi {v}" if v else "fin-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def sec(t,s=""):
    sub=f'<p class="fin-secs">{s}</p>' if s else ""
    return f'<p class="fin-sec">{t}</p>{sub}'

def div(): return '<div class="fin-div"></div>'

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_CONS=[
    {"id":"c1","nome":"Etapas Pioneiras, Lda",  "nif":"510391125","iban":"PT50004513454025352458285","email":"etapas@demo.pt"},
    {"id":"c2","nome":"Winet Consulting, Lda",  "nif":"509812345","iban":"PT50001234567890123456789","email":"winet@demo.pt"},
    {"id":"c3","nome":"FormaConsult, Unip. Lda","nif":"511234567","iban":"PT50009876543210987654321","email":"formaconsult@demo.pt"},
]
_MOCK_ACOES=[
    {"id":"a1","magna_id":"ASE:OSEMC_30.1","nome":"Op. Seg. Equip. Movimentação Cargas 1","empresa_cliente":"J.A. Veiga de Macedo","codigo":"ASE:OSEMC_30.1","data_inicio":"2026-03-19","data_fim":"2026-04-17","volume_horas":30,"formandos_certificados":16,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a2","magna_id":"ASE:OSEMC_30.2","nome":"Op. Seg. Equip. Movimentação Cargas 2","empresa_cliente":"J.A. Veiga de Macedo/Z Cork","codigo":"ASE:OSEMC_30.2","data_inicio":"2026-03-19","data_fim":"2026-04-16","volume_horas":30,"formandos_certificados":15,"consultor_id":"c1","projeto":"PRODUTECH","nh_emitida":False},
    {"id":"a3","magna_id":"GEOEMC_8","nome":"Gestão Eficiente de Equipamentos","empresa_cliente":"Manuaço","codigo":"GEOEMC_8","data_inicio":"2026-02-06","data_fim":"2026-02-13","volume_horas":8,"formandos_certificados":10,"consultor_id":"c2","projeto":"ANIET","nh_emitida":False},
    {"id":"a4","magna_id":"LGE_12","nome":"Liderança e gestão de equipas","empresa_cliente":"Fenabel, S.A","codigo":"LGE_12","data_inicio":"2026-01-05","data_fim":"2026-01-19","volume_horas":12,"formandos_certificados":14,"consultor_id":"c2","projeto":"MENTORES","nh_emitida":True},
    {"id":"a5","magna_id":"TN_16","nome":"Técnicas de negociação","empresa_cliente":"Fenabel, S.A","codigo":"TN_16","data_inicio":"2026-03-09","data_fim":"2026-03-30","volume_horas":16,"formandos_certificados":10,"consultor_id":"c3","projeto":"MENTORES","nh_emitida":False},
]
_MOCK_NH=[{"id":"nh1","consultor_id":"c2","consultor_nome":"Winet Consulting, Lda","projeto":"MENTORES","valor":1646.40,"data_emissao":"2026-05-10","estado":"aguarda_fatura"}]
_MOCK_FC=[{"id":"fc1","consultor_id":"c1","consultor_nome":"Etapas Pioneiras, Lda","projeto":"PRODUTECH","numero_fatura":"FT-EC-2026/001","valor":2901.60,"estado":"aguarda_aprovacao","data_submissao":"2026-05-20","ficheiro_url":None}]
_MOCK_FORM={"a1":[{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0142","valor":3200,"estado":"aprovada"}],"a2":[{"nome":"Ivo Daniel Carneiro Monteiro","n_fatura":"FT2026/0138","valor":2800,"estado":"submetida"}],"a3":[{"nome":"Ana Ferreira","n_fatura":None,"valor":2100,"estado":"sem_fatura"}]}

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_cons():
    if not SUPABASE_OK: return _MOCK_CONS
    try: return get_supabase().table("profiles").select("id,nome,nif,iban,email").eq("role","gestor_projeto").execute().data
    except: return _MOCK_CONS

def _get_acoes_sem_nh(cid=None):
    if not SUPABASE_OK:
        d=[a for a in _MOCK_ACOES if not a["nh_emitida"]]
        return [a for a in d if a["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("acoes").select("id,magna_id,nome,empresa_cliente,codigo,data_inicio,data_fim,volume_horas,formandos_certificados,coordenador_id").eq("estado","fechada")
        if cid: q=q.eq("coordenador_id",cid)
        r=q.execute()
        nh_ids={x["acao_id"] for x in get_supabase().table("faturacao_consultores").select("acao_id").neq("estado","disponivel").execute().data}
        return [a for a in r.data if a["id"] not in nh_ids]
    except: return []

def _get_nh(cid=None):
    if not SUPABASE_OK:
        d=_MOCK_NH
        return [n for n in d if n["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("faturacao_consultores").select("id,consultor_id,valor,estado,created_at,profiles!consultor_id(nome),acoes(nome)").in_("estado",["selecionada","aguarda_confirmacao","confirmada"])
        if cid: q=q.eq("consultor_id",cid)
        return q.execute().data
    except: return []

def _get_faturas_consultores_pendentes(cid=None):
    if not SUPABASE_OK:
        d=_MOCK_FC
        return [f for f in d if f["consultor_id"]==cid] if cid else d
    try:
        q=get_supabase().table("faturacao_consultores").select("id,consultor_id,valor,estado,numero_fatura,created_at,ficheiro_fatura_url,profiles!consultor_id(nome,email),acoes(nome)").eq("estado","fatura_emitida")
        if cid: q=q.eq("consultor_id",cid)
        return q.execute().data
    except: return []

def _get_form_acao(aid):
    if not SUPABASE_OK: return _MOCK_FORM.get(aid,[])
    try:
        r=get_supabase().table("faturas").select("numero_fatura,valor,estado,profiles!formador_id(nome)").eq("acao_id",aid).execute()
        return [{"nome":(x.get("profiles") or {}).get("nome") or "—","n_fatura":x.get("numero_fatura"),"valor":x.get("valor") or 0,"estado":x.get("estado")} for x in r.data]
    except: return []

def _aprovar_fc(fc_id,user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({"estado":"paga","confirmada_financeiro_em":datetime.utcnow().isoformat()}).eq("id",fc_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def _rejeitar_fc(fc_id,motivo,user_nome):
    if not SUPABASE_OK: return True
    try:
        get_supabase_admin().table("faturacao_consultores").update({"estado":"confirmada","notas":f"Rejeitado: {motivo}"}).eq("id",fc_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render_consultores(user: dict):
    st.html(_CSS)
    user_nome=user.get("nome") or "Financeiro"
    consultores=_get_cons()

    col_f,_=st.columns([2,4])
    with col_f:
        opcoes=["Todos"]+[c["nome"] for c in consultores]
        filtro=st.selectbox("Filtrar por consultor",opcoes,key="fil_cons")

    cid=None
    if filtro!="Todos":
        m=[c for c in consultores if c["nome"]==filtro]
        if m: cid=m[0]["id"]

    sem_nh=_get_acoes_sem_nh(cid)
    nh_em=_get_nh(cid)
    fat_p=_get_faturas_consultores_pendentes(cid)

    st.html(
        '<div class="fin-kpi-row">'
        +kpi_h("📋 Ações sem NH",    str(len(sem_nh)), "fechadas",          "a")
        +kpi_h("📄 NH emitidas",     str(len(nh_em)),  "a aguardar fatura", "b")
        +kpi_h("⏳ Faturas a aprovar",str(len(fat_p)),  "submetidas",        "p")
        +'</div>'
    )

    st.html(div())

    # ---- AÇÕES SEM NH ----
    st.markdown(sec(f"📋 Ações fechadas sem NH ({len(sem_nh)})","Seleciona as ações para gerar uma nota de honorários."),unsafe_allow_html=True)

    if not sem_nh:
        st.html('<div class="fin-empty">✅ Todas as ações fechadas já têm NH emitida.</div>')
    else:
        grupos={}
        for a in sem_nh:
            grupos.setdefault(a.get("consultor_id") or "—",[]).append(a)

        for gid,acoes in grupos.items():
            cm=[c for c in consultores if c["id"]==gid]
            c_nome=cm[0]["nome"] if cm else gid

            with st.expander(f"**{c_nome}** — {len(acoes)} ação(ões)",expanded=True):
                for a in acoes:
                    ch=int(a.get("volume_horas") or 0)
                    fm=int(a.get("formandos_certificados") or 0)
                    v=calcular_valor_acao(ch,fm)
                    pr=a.get("projeto") or "—"

                    cc,ci,cf_,cv=st.columns([0.5,4,3,1.5])
                    sel=cc.checkbox("",key=f"sel_{a['id']}",label_visibility="collapsed")
                    ci.markdown(
                        f'<div style="padding:3px 0">'
                        f'<span style="font-weight:600;font-size:13px">{a.get("codigo") or "—"}</span>&nbsp;{ptag(pr)}<br>'
                        f'<span style="font-size:11px;color:#8B94A3">{a.get("empresa_cliente") or "—"} · {a.get("data_inicio") or "—"} → {a.get("data_fim") or "—"} · {ch}h · {fm} form.</span>'
                        f'</div>',unsafe_allow_html=True
                    )
                    forms=_get_form_acao(a["id"])
                    if forms:
                        fh=" · ".join([f"{f['nome']}&nbsp;{bdg(f['estado'])}" for f in forms])
                        cf_.markdown(f"<div style='font-size:11px;color:#6B7280;padding-top:5px'>{fh}</div>",unsafe_allow_html=True)
                    cv.markdown(f"<div style='text-align:right;padding-top:5px;font-weight:700;font-size:14px'>{eur(v)}</div>",unsafe_allow_html=True)

                sel_acoes=[a for a in acoes if st.session_state.get(f"sel_{a['id']}",False)]
                if sel_acoes:
                    total=sum(calcular_valor_acao(int(a.get("volume_horas") or 0),int(a.get("formandos_certificados") or 0)) for a in sel_acoes)
                    st.markdown(f"<div style='font-size:13px;color:#4B5263;margin:6px 0'><strong>{len(sel_acoes)} selecionada(s)</strong> · Total: <strong>{eur(total)}</strong></div>",unsafe_allow_html=True)
                    if st.button(f"📄 Gerar NH — {c_nome}",key=f"gnh_{gid}",type="primary"):
                        try:
                            c_data=cm[0] if cm else {"nome":c_nome,"nif":"—","iban":"—"}
                            nh_num=len(_MOCK_NH)+1
                            pr_nome=sel_acoes[0].get("projeto") or "—"
                            pr_cod=sel_acoes[0].get("magna_id") or "—"
                            from app.gerar_nh import construir_dados_nh,gerar_nh
                            dados_nh=construir_dados_nh(nh_num,c_data,{"nome":pr_nome,"magna_id":pr_cod},sel_acoes)
                            docx=gerar_nh(dados_nh)
                            st.download_button(f"⬇️ Download NH{nh_num}",docx,f"NH{nh_num}_{c_nome[:20].replace(' ','_')}.docx","application/vnd.openxmlformats-officedocument.wordprocessingml.document",key=f"dl_{gid}")
                            st.success(f"NH{nh_num} gerada!")
                        except Exception as e: st.error(f"Erro: {e}")

    st.html(div())

    # ---- NH EMITIDAS ----
    st.markdown(sec(f"📄 NH emitidas ({len(nh_em)})","Aguardam que o consultor submeta a fatura."),unsafe_allow_html=True)
    if not nh_em:
        st.html('<div class="fin-empty">Nenhuma NH emitida a aguardar fatura.</div>')
    else:
        h=""
        for row in nh_em:
            cn=row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            pr=row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            v=row.get("valor") or 0; est=row.get("estado") or "aguarda_fatura"
            de=str(row.get("data_emissao") or row.get("created_at") or "—")[:10]
            h+=f'<div class="fin-card"><div style="flex:1"><div style="font-weight:600;font-size:14px">{cn}</div><div style="font-size:12px;color:#8B94A3">{ptag(pr)} · Emitida: {de}</div></div><div style="text-align:right;margin-right:10px"><div style="font-weight:700;font-size:15px">{eur(v)}</div></div>{bdg(est)}</div>'
        st.html(h)

    st.html(div())

    # ---- FATURAS A APROVAR ----
    st.markdown(sec(f"⏳ Faturas a aprovar ({len(fat_p)})","Faturas submetidas pelos consultores após receberem a NH."),unsafe_allow_html=True)
    if not fat_p:
        st.html('<div class="fin-empty">✅ Nenhuma fatura de consultor pendente.</div>')
    else:
        for i,row in enumerate(fat_p):
            fid=row.get("id") or str(i)
            cn=row.get("consultor_nome") or (row.get("profiles") or {}).get("nome") or "—"
            pr=row.get("projeto") or (row.get("acoes") or {}).get("nome") or "—"
            v=row.get("valor") or 0; nf=row.get("numero_fatura") or "—"
            ds=str(row.get("data_submissao") or row.get("created_at") or "—")[:10]
            fich=row.get("ficheiro_url") or row.get("ficheiro_fatura_url")

            ci,cpdf,ca=st.columns([4,1,3])
            with ci:
                st.html(
                    f'<div class="fin-aprov">'
                    f'<div style="font-weight:700;font-size:14px">{cn} <span style="font-size:12px;font-weight:400;color:#8B94A3">{nf}</span></div>'
                    f'<div style="font-size:13px;color:#4B5263">{ptag(pr)} · {eur(v)}</div>'
                    f'<div class="ds">Submetida: {ds}</div>'
                    f'</div>'
                )
            with cpdf:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if fich: st.link_button("📄",fich)
                else: st.caption("—")
                st.markdown("</div>",unsafe_allow_html=True)
            with ca:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if st.button("✅ Aprovar",key=f"afc_{i}_{fid}",use_container_width=True):
                    if _aprovar_fc(fid,user_nome): st.toast(f"Fatura de {cn} aprovada."); st.rerun()
                mot=st.text_input("",key=f"mfc_{i}_{fid}",placeholder="Motivo de rejeição…",label_visibility="collapsed")
                if st.button("❌ Rejeitar",key=f"rfc_{i}_{fid}",use_container_width=True):
                    if mot:
                        if _rejeitar_fc(fid,mot,user_nome): st.toast(f"Fatura de {cn} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo.")
                st.markdown("</div>",unsafe_allow_html=True)
