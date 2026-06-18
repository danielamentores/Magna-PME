"""Tab Projeto Comércio e Serviços."""
import streamlit as st
from app import db_coordenador as db

PROJETOS = ["APIMA"]

VOLUMES = {
    "APIMA": {"atribuido": 2000, "realizado": 890},
}

ACOES_PROJETO = {
    "APIMA": [
        {"codigo":"APIMA.01.CS","nome":"Atendimento e experiência do cliente","empresa":"Comércio Lisboa, Lda","estado":"fechada","pct":100},
        {"codigo":"APIMA.02.CS","nome":"Visual merchandising","empresa":"RetailGroup, SA","estado":"a_decorrer","pct":45},
        {"codigo":"APIMA.03.CS","nome":"Gestão de stocks e logística","empresa":"Comércio Lisboa, Lda","estado":"planeada","pct":0},
    ],
}

FORMADORES = [
    {"nome":"Sofia Rodrigues","consultor":"FormaConsult, Unip.Lda","projeto":"APIMA"},
    {"nome":"Pedro Costa",    "consultor":"FormaConsult, Unip.Lda","projeto":"APIMA"},
]

ACOES_FORMADOR = {
    "Sofia Rodrigues": [
        {"acao":"APIMA.01.CS — Atendimento ao cliente","fechada":True,"faturou":True,"fatura":"fat_sofia_001.pdf","paga":False},
        {"acao":"APIMA.02.CS — Visual merchandising",  "fechada":False,"faturou":False,"fatura":None,"paga":False},
    ],
    "Pedro Costa": [
        {"acao":"APIMA.01.CS — Atendimento ao cliente","fechada":True,"faturou":False,"fatura":None,"paga":False},
    ],
}

EMPRESAS = [
    {"nome":"Comércio Lisboa, Lda","nif":"511234567","estado":"Validada"},
    {"nome":"RetailGroup, SA",     "nif":"512345678","estado":"Execução pendente"},
]

ACOES_EMPRESA = {
    "Comércio Lisboa, Lda": [
        {"acao":"APIMA.01.CS — Atendimento","formandos":12,"certificados":11,"horas":20,
         "valor_compete":2200.0,"valor_mentores":495.0,"reembolso":True,"faturada":True,"paga":False},
    ],
}

def _eur(v):
    try: return f"€\u202f{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "€ —"

def kpi(lbl,val,sub,v=""):
    cls=f"c-kpi {v}" if v else "c-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def div(): return '<div class="c-div"></div>'

def _execucao():
    with st.expander("📈 Execução", expanded=True):
        projeto = st.selectbox("Projeto", PROJETOS, key="exec_proj_cs")
        acoes = ACOES_PROJETO.get(projeto,[])
        vol = VOLUMES.get(projeto,{"atribuido":0,"realizado":0})
        atr,real = vol["atribuido"],vol["realizado"]
        pct = round(real/atr*100) if atr else 0
        fechadas=[a for a in acoes if a["estado"]=="fechada"]
        decorrer=[a for a in acoes if a["estado"]=="a_decorrer"]
        planeadas=[a for a in acoes if a["estado"]=="planeada"]

        st.html('<div class="c-kpi-row">'+kpi("📦 Atribuído",str(atr),"horas","b")+kpi("✅ Realizado",str(real),f"{pct}%","g")+kpi("🔒 Fechadas",str(len(fechadas)),"ações","g")+kpi("🔵 A decorrer",str(len(decorrer)),"ações","b")+'</div>')
        st.progress(min(pct/100,1.0))

        if fechadas:
            st.markdown("**✅ Ações fechadas**")
            for a in fechadas:
                st.html(f'<div class="c-card" style="border-left:3px solid #16A34A"><div style="font-weight:600;font-size:13px">{a["codigo"]}</div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')
        if decorrer:
            st.markdown("**🔵 A decorrer**")
            for a in decorrer:
                st.html(f'<div class="c-card" style="border-left:3px solid #2563EB"><div style="display:flex;justify-content:space-between"><span style="font-weight:600;font-size:13px">{a["codigo"]}</span><span style="font-size:12px;color:#2563EB">{a["pct"]}%</span></div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')
                st.progress(a["pct"]/100)
        if planeadas:
            st.markdown("**📋 Planeadas**")
            for a in planeadas:
                st.html(f'<div class="c-card" style="border-left:3px solid #7C3AED"><div style="font-weight:600;font-size:13px">{a["codigo"]}</div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')

def _formadores():
    with st.expander("👤 Formadores", expanded=False):
        termo = st.text_input("",placeholder="Pesquisar formador...",key="form_pesq_cs",label_visibility="collapsed")
        encontrados=[f for f in FORMADORES if not termo or termo.lower() in f["nome"].lower()]
        if not encontrados:
            st.html('<div class="c-empty">Nenhum formador encontrado.</div>'); return
        nome_sel=st.selectbox("Formador",[f["nome"] for f in encontrados],key="form_sel_cs")
        formador=next(f for f in encontrados if f["nome"]==nome_sel)
        st.html(f'<div style="font-size:12px;color:#8B94A3;margin-bottom:12px">Consultor: <strong style="color:#1A1F2E">{formador["consultor"]}</strong></div>')
        acoes=ACOES_FORMADOR.get(nome_sel,[])
        if not acoes:
            st.html('<div class="c-empty">Sem ações registadas.</div>'); return
        for i,a in enumerate(acoes):
            col_i,col_d=st.columns([5,1])
            with col_i:
                st.html(f'<div class="c-card" style="border-left:3px solid {"#16A34A" if a["paga"] else "#2563EB" if a["faturou"] else "#E4E7EF"}"><div style="font-weight:600;font-size:13px;margin-bottom:6px">{a["acao"]}</div><div style="display:flex;gap:16px;font-size:12px;color:#4B5263"><span>{"✅" if a["fechada"] else "⏳"} Fechada</span><span>{"✅" if a["faturou"] else "❌"} Faturou</span><span>{"💳" if a["paga"] else "❌"} Paga</span></div></div>')
            with col_d:
                if a["faturou"] and a["fatura"]:
                    st.markdown("<div style='margin-top:8px'>",unsafe_allow_html=True)
                    st.download_button("📄",data=b"placeholder",file_name=a["fatura"],key=f"dl_cs_{nome_sel}_{i}")
                    st.markdown("</div>",unsafe_allow_html=True)

def _empresas():
    with st.expander("🏢 Empresas", expanded=False):
        lista=EMPRESAS
        pesq=st.text_input("",placeholder="Pesquisar empresa...",key="emp_pesq_cs",label_visibility="collapsed")
        if pesq: lista=[e for e in lista if pesq.lower() in e["nome"].lower()]
        if not lista:
            st.html('<div class="c-empty">Sem empresas.</div>'); return
        nome_sel=st.selectbox("Empresa",[e["nome"] for e in lista],key="emp_sel_cs")
        acoes=ACOES_EMPRESA.get(nome_sel,[])
        if not acoes:
            st.html('<div class="c-empty">Sem ações registadas.</div>'); return
        t_c=t_m=0.0
        for a in acoes:
            t_c+=a["valor_compete"]; t_m+=a["valor_mentores"]
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Certificados",f"{a['certificados']}/{a['formandos']}")
                c2.metric("Horas",f"{a['horas']}h")
                c3.metric("Valor COMPETE",_eur(a["valor_compete"]))
                c4.metric("Valor M&T",_eur(a["valor_mentores"]))
                st.html(f'<div style="display:flex;gap:20px;font-size:12px;color:#4B5263;margin-top:4px"><span>{"✅" if a["reembolso"] else "⏳"} Reembolso</span><span>{"✅" if a["faturada"] else "❌"} Faturada</span><span>{"💳" if a["paga"] else "❌"} Paga</span></div>')
        st.html(div())
        c1,c2=st.columns(2)
        c1.metric("Total COMPETE",_eur(t_c)); c2.metric("Total M&T",_eur(t_m))

def _faturacao():
    with st.expander("💶 Faturação", expanded=False):
        total_fat=sum(a["valor"] for a in db.acoes_em("Faturada","Paga"))
        total_pago=sum(a["valor"] for a in db.acoes_em("Paga"))
        st.html('<div class="c-kpi-row">'+kpi("🧾 Total faturado",_eur(total_fat),"acumulado","b")+kpi("💳 Total recebido",_eur(total_pago),"pago","g")+'</div>')
        st.html(div())

        fechadas=db.acoes_em("Fechada","Devolvida")
        st.markdown("**Ações fechadas — enviar à gestora**")
        if not fechadas:
            st.html('<div class="c-empty">Sem ações por enviar.</div>')
        else:
            sels=[]
            for a in fechadas:
                if st.checkbox(f"{a['acao']} — {a['empresa']} — {_eur(a['valor'])}",key=f"fat_cs_{a['id']}"):
                    sels.append(a)
            if st.button("📧 Enviar à gestora",key="fat_enviar_cs",type="primary"):
                if sels:
                    for a in sels: db.definir_estado(a["id"],"Em confirmação")
                    st.success(f"{len(sels)} ação(ões) enviada(s)."); st.rerun()
                else: st.warning("Seleciona pelo menos uma ação.")

        aceites=db.acoes_em("Aceite")
        if aceites:
            st.html(div()); st.markdown("**Aceites — submeter fatura ao financeiro**")
            for a in aceites:
                st.html(f'<div class="c-card" style="border-left:3px solid #16A34A">✅ {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}</div>')
            st.metric("Total a faturar",_eur(sum(a["valor"] for a in aceites)))
            fich=st.file_uploader("Fatura (PDF)",type=["pdf"],key="fat_upload_cs")
            if st.button("📤 Submeter ao financeiro",key="fat_sub_cs",type="primary"):
                if fich:
                    for a in aceites: db.definir_estado(a["id"],"Faturada")
                    st.success("Fatura submetida."); st.rerun()
                else: st.warning("Carrega o PDF primeiro.")

def render():
    _execucao()
    _formadores()
    _empresas()
    _faturacao()
