"""Tab Projeto Formação Ação."""
import streamlit as st
from app import db_coordenador as db

PROJETOS = ["Multisetorial", "CAP"]

VOLUMES = {
    "Projeto Multisetorial": {"atribuido": 1800, "realizado": 1200},
    "Projeto CAP":   {"atribuido": 1400, "realizado": 620},
}

ACOES_PROJETO = {
    "Projeto Multisetorial": [
        {"codigo":"PROD.01.FA","nome":"Op. Seg. Equip. Movimentação Cargas 1","empresa":"J.A. Veiga de Macedo","estado":"fechada","pct":100},
        {"codigo":"PROD.02.FA","nome":"Op. Seg. Equip. Movimentação Cargas 2","empresa":"J.A. Veiga de Macedo","estado":"fechada","pct":100},
        {"codigo":"PROD.03.FA","nome":"Gestão eficiente de equipamentos","empresa":"Manuaço","estado":"a_decorrer","pct":55},
    ],
    "Projeto CAP": [
        {"codigo":"CALC.01.FA","nome":"Técnicas de costura industrial","empresa":"Norte, Lda","estado":"fechada","pct":100},
        {"codigo":"CALC.02.FA","nome":"Controlo de qualidade no calçado","empresa":"Norte, Lda","estado":"a_decorrer","pct":40},
    ],
}

FORMADORES = [
    {"nome":"Ivo Daniel Monteiro","consultor":"Etapas Pioneiras, Lda","projeto":"Projeto Multisetorial"},
    {"nome":"Carla Neves",        "consultor":"Winet Consulting, Lda", "projeto":"Projeto Multisetorial"},
    {"nome":"Rui Mendes",         "consultor":"FormaConsult, Unip.Lda","projeto":"Projeto CAP"},
]

ACOES_FORMADOR = {
    "Ivo Daniel Monteiro": [
        {"acao":"PROD.01.FA — Movimentação Cargas 1","fechada":True, "faturou":True, "fatura":"fat_ivo_001.pdf","paga":False},
        {"acao":"PROD.02.FA — Movimentação Cargas 2","fechada":True, "faturou":True, "fatura":"fat_ivo_002.pdf","paga":False},
    ],
    "Rui Mendes": [
        {"acao":"CALC.01.FA — Costura industrial","fechada":True,"faturou":False,"fatura":None,"paga":False},
    ],
}

EMPRESAS = [
    {"nome":"J.A. Veiga de Macedo","nif":"509012345","estado":"Validada"},
    {"nome":"Manuaço",             "nif":"510234567","estado":"Validada"},
    {"nome":"Calçado Norte, Lda",  "nif":"508765432","estado":"Execução pendente"},
]

ACOES_EMPRESA = {
    "J.A. Veiga de Macedo": [
        {"acao":"PROD.01.FA — Movimentação 1","formandos":16,"certificados":16,"horas":30,
         "valor_compete":3600.0,"valor_mentores":1080.0,"reembolso":True,"faturada":False,"paga":False},
        {"acao":"PROD.02.FA — Movimentação 2","formandos":15,"certificados":14,"horas":30,
         "valor_compete":3150.0,"valor_mentores":945.0,"reembolso":False,"faturada":False,"paga":False},
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
        projeto = st.selectbox("Projeto", PROJETOS, key="exec_proj_fa")
        acoes = ACOES_PROJETO.get(projeto, [])
        vol = VOLUMES.get(projeto, {"atribuido":0,"realizado":0})
        atr, real = vol["atribuido"], vol["realizado"]
        pct = round(real/atr*100) if atr else 0
        fechadas = [a for a in acoes if a["estado"]=="fechada"]
        decorrer = [a for a in acoes if a["estado"]=="a_decorrer"]

        st.html(
            '<div class="c-kpi-row">'
            +kpi("📦 Atribuído", str(atr),"horas","b")
            +kpi("✅ Realizado",  str(real),f"{pct}%","g")
            +kpi("🔒 Fechadas",  str(len(fechadas)),"ações","g")
            +kpi("🔵 A decorrer",str(len(decorrer)),"ações","b")
            +'</div>'
        )
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

def _formadores():
    with st.expander("👤 Formadores", expanded=False):
        termo = st.text_input("", placeholder="Pesquisar formador...", key="form_pesq_fa", label_visibility="collapsed")
        encontrados = [f for f in FORMADORES if not termo or termo.lower() in f["nome"].lower()]
        if not encontrados:
            st.html('<div class="c-empty">Nenhum formador encontrado.</div>')
            return
        nome_sel = st.selectbox("Formador", [f["nome"] for f in encontrados], key="form_sel_fa")
        formador = next(f for f in encontrados if f["nome"]==nome_sel)
        st.html(f'<div style="font-size:12px;color:#8B94A3;margin-bottom:12px">Consultor: <strong style="color:#1A1F2E">{formador["consultor"]}</strong></div>')
        acoes = ACOES_FORMADOR.get(nome_sel,[])
        if not acoes:
            st.html('<div class="c-empty">Sem ações registadas.</div>')
            return
        for i,a in enumerate(acoes):
            col_i,col_d = st.columns([5,1])
            with col_i:
                st.html(
                    f'<div class="c-card" style="border-left:3px solid {"#16A34A" if a["paga"] else "#2563EB" if a["faturou"] else "#E4E7EF"}">'
                    f'<div style="font-weight:600;font-size:13px;margin-bottom:6px">{a["acao"]}</div>'
                    f'<div style="display:flex;gap:16px;font-size:12px;color:#4B5263">'
                    f'<span>{"✅" if a["fechada"] else "⏳"} Fechada</span>'
                    f'<span>{"✅" if a["faturou"] else "❌"} Faturou</span>'
                    f'<span>{"💳" if a["paga"] else "❌"} Paga</span>'
                    f'</div></div>'
                )
            with col_d:
                if a["faturou"] and a["fatura"]:
                    st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
                    st.download_button("📄", data=b"placeholder", file_name=a["fatura"], key=f"dl_fa_{nome_sel}_{i}")
                    st.markdown("</div>", unsafe_allow_html=True)

def _empresas():
    with st.expander("🏢 Empresas", expanded=False):
        lista = EMPRESAS
        pesq = st.text_input("", placeholder="Pesquisar empresa...", key="emp_pesq_fa", label_visibility="collapsed")
        if pesq: lista = [e for e in lista if pesq.lower() in e["nome"].lower()]
        if not lista:
            st.html('<div class="c-empty">Sem empresas.</div>')
            return
        nome_sel = st.selectbox("Empresa", [e["nome"] for e in lista], key="emp_sel_fa")
        acoes = ACOES_EMPRESA.get(nome_sel,[])
        if not acoes:
            st.html('<div class="c-empty">Sem ações registadas.</div>')
            return
        t_c = t_m = 0.0
        for a in acoes:
            t_c += a["valor_compete"]; t_m += a["valor_mentores"]
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Certificados",f"{a['certificados']}/{a['formandos']}")
                c2.metric("Horas",f"{a['horas']}h")
                c3.metric("A Receber do COMPETE2030",_eur(a["valor_compete"]))
                c4.metric("A Pagar à M&T (30%)",_eur(a["valor_mentores"]))
                st.html(f'<div style="display:flex;gap:20px;font-size:12px;color:#4B5263;margin-top:4px"><span>{"✅" if a["reembolso"] else "⏳"} Reembolso</span><span>{"✅" if a["faturada"] else "❌"} Faturada</span><span>{"💳" if a["paga"] else "❌"} Paga</span></div>')
        st.html(div())
        c1,c2 = st.columns(2)
        c1.metric("Total a Receber pelo COMPETE2030",_eur(t_c)); c2.metric("Total a Pagar à M&T",_eur(t_m))

def _faturacao():
    with st.expander("💶 Faturação", expanded=False):
        total_fat  = sum(a["valor"] for a in db.acoes_em("Faturada","Paga"))
        total_pago = sum(a["valor"] for a in db.acoes_em("Paga"))
        st.html('<div class="c-kpi-row">'+kpi("🧾 Total faturado",_eur(total_fat),"acumulado","b")+kpi("💳 Total recebido",_eur(total_pago),"pago","g")+'</div>')
        st.html(div())

        fechadas = db.acoes_em("Fechada","Devolvida")
        st.markdown("**Ações fechadas — enviar à gestora**")
        if not fechadas:
            st.html('<div class="c-empty">Sem ações por enviar.</div>')
        else:
            sels = []
            for a in fechadas:
                if st.checkbox(f"{a['acao']} — {a['empresa']} — {_eur(a['valor'])}", key=f"fat_fa_{a['id']}"):
                    sels.append(a)
            if st.button("📧 Enviar à gestora", key="fat_enviar_fa", type="primary"):
                if sels:
                    for a in sels: db.definir_estado(a["id"],"Em confirmação")
                    st.success(f"{len(sels)} ação(ões) enviada(s)."); st.rerun()
                else: st.warning("Seleciona pelo menos uma ação.")

        em_conf = db.acoes_em("Em confirmação")
        if em_conf:
            st.html(div()); st.markdown("**A aguardar confirmação**")
            for a in em_conf:
                st.html(f'<div class="c-card" style="border-left:3px solid #D97706">⏳ {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}</div>')

        aceites = db.acoes_em("Aceite")
        if aceites:
            st.html(div()); st.markdown("**Aceites — submeter fatura ao financeiro**")
            for a in aceites:
                st.html(f'<div class="c-card" style="border-left:3px solid #16A34A">✅ {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}</div>')
            st.metric("Total a faturar",_eur(sum(a["valor"] for a in aceites)))
            fich = st.file_uploader("Fatura (PDF)", type=["pdf"], key="fat_upload_fa")
            if st.button("📤 Submeter ao financeiro", key="fat_sub_fa", type="primary"):
                if fich:
                    for a in aceites: db.definir_estado(a["id"],"Faturada")
                    st.success("Fatura submetida."); st.rerun()
                else: st.warning("Carrega o PDF primeiro.")

def render():
    _execucao()
    _formadores()
    _empresas()
    _faturacao()
