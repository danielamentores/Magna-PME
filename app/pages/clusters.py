"""Tab Projetos Clusters."""
import streamlit as st
from app import db_coordenador as db

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
PROJETOS = ["APCMC", "ANIET", "MENTORES"]

VOLUMES = {
    "APCMC":    {"atribuido": 1200, "realizado": 780},
    "ANIET":    {"atribuido": 2400, "realizado": 1640},
    "MENTORES": {"atribuido": 3200, "realizado": 2100},
}

ACOES_PROJETO = {
    "APCMC": [
        {"codigo":"APCMC.01.PCE","nome":"Escalada e desmanche de árvores","empresa":"Like Garden","estado":"fechada","pct":100},
        {"codigo":"APCMC.02.PCE","nome":"Segurança na construção civil","empresa":"CAMOESAS, Lda","estado":"a_decorrer","pct":65},
        {"codigo":"APCMC.03.PCE","nome":"Gestão de emergências","empresa":"Fenabel, S.A","estado":"a_decorrer","pct":30},
        {"codigo":"APCMC.04.PCE","nome":"Literacia digital","empresa":"J. Moreira da Silva","estado":"fechada","pct":100},
    ],
    "ANIET": [
        {"codigo":"ANIET.01.PCE","nome":"Operar equipamentos de elevação","empresa":"Mecanidráulica","estado":"fechada","pct":100},
        {"codigo":"ANIET.02.PCE","nome":"Operações florestais com motosserra","empresa":"Forestcorte","estado":"a_decorrer","pct":50},
    ],
    "MENTORES": [
        {"codigo":"MENT.01.PCE","nome":"Liderança e gestão de equipas","empresa":"Fenabel, S.A","estado":"fechada","pct":100},
        {"codigo":"MENT.02.PCE","nome":"Técnicas de negociação","empresa":"Fenabel, S.A","estado":"a_decorrer","pct":75},
        {"codigo":"MENT.03.PCE","nome":"Excel avançado","empresa":"Empresa Alfa, Lda","estado":"planeada","pct":0},
    ],
}

FORMADORES = [
    {"nome":"Ana Silva",    "consultor":"Etapas Pioneiras, Lda", "projeto":"APCMC"},
    {"nome":"Bruno Costa",  "consultor":"Etapas Pioneiras, Lda", "projeto":"APCMC"},
    {"nome":"Carla Dias",   "consultor":"Winet Consulting, Lda",  "projeto":"ANIET"},
    {"nome":"Fátima Sorte", "consultor":"Winet Consulting, Lda",  "projeto":"MENTORES"},
]

ACOES_FORMADOR = {
    "Ana Silva": [
        {"acao":"APCMC.01.PCE — Escalada e desmanche","fechada":True, "faturou":True, "fatura":"fat_ana_001.pdf","paga":True},
        {"acao":"APCMC.02.PCE — Segurança construção", "fechada":True, "faturou":True, "fatura":"fat_ana_002.pdf","paga":False},
        {"acao":"APCMC.03.PCE — Gestão emergências",   "fechada":False,"faturou":False,"fatura":None,           "paga":False},
    ],
    "Bruno Costa": [
        {"acao":"APCMC.01.PCE — Escalada e desmanche","fechada":True, "faturou":False,"fatura":None,"paga":False},
    ],
    "Carla Dias": [
        {"acao":"ANIET.01.PCE — Equipamentos elevação","fechada":True, "faturou":True, "fatura":"fat_carla_001.pdf","paga":True},
    ],
    "Fátima Sorte": [
        {"acao":"MENT.01.PCE — Liderança e gestão",   "fechada":True, "faturou":True, "fatura":"fat_fatima_001.pdf","paga":False},
        {"acao":"MENT.02.PCE — Técnicas negociação",  "fechada":False,"faturou":False,"fatura":None,               "paga":False},
    ],
}

EMPRESAS = [
    {"nome":"Like Garden",         "nif":"509408486","estado":"Validada"},
    {"nome":"CAMOESAS, Lda",       "nif":"508392594","estado":"Validada"},
    {"nome":"Fenabel, S.A",        "nif":"502815795","estado":"Validada"},
    {"nome":"J. Moreira da Silva", "nif":"",         "estado":"Execução pendente"},
    {"nome":"Mecanidráulica",      "nif":"510033423","estado":"Validada"},
]

ACOES_EMPRESA = {
    "Fenabel, S.A": [
        {"acao":"MENT.01.PCE — Liderança","formandos":14,"certificados":14,"horas":12,
         "valor_compete":3780.0,"valor_mentores":1646.40,"reembolso":True,"faturada":True,"paga":False},
        {"acao":"MENT.02.PCE — Negociação","formandos":10,"certificados":8,"horas":16,
         "valor_compete":2700.0,"valor_mentores":810.0,"reembolso":False,"faturada":False,"paga":False},
    ],
    "Like Garden": [
        {"acao":"APCMC.01.PCE — Escalada","formandos":18,"certificados":18,"horas":50,
         "valor_compete":6750.0,"valor_mentores":2025.0,"reembolso":True,"faturada":True,"paga":True},
    ],
}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _eur(v):
    try: return f"€\u202f{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "€ —"

def _bdg_acao(estado):
    M={"fechada":("#F0FDF4","#16A34A","✅ Fechada"),
       "a_decorrer":("#EEF3FD","#2563EB","🔵 A decorrer"),
       "planeada":("#F5F3FF","#7C3AED","📋 Planeada"),
       "terminada_sem_fecho":("#FFFBEB","#D97706","⚠️ Por fechar")}
    bg,c,l=M.get(estado,("#F3F4F6","#6B7280",estado))
    return f'<span style="display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;background:{bg};color:{c}">{l}</span>'

def _bdg_fat(estado):
    M={"Paga":("#F0FDF4","#16A34A"),"Faturada":("#EEF3FD","#2563EB"),
       "Aceite":("#F0FDF4","#16A34A"),"Em confirmação":("#FFFBEB","#D97706"),
       "Fechada":("#F5F3FF","#7C3AED"),"Devolvida":("#FEF2F2","#DC2626")}
    bg,c=M.get(estado,("#F3F4F6","#6B7280"))
    return f'<span style="display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;background:{bg};color:{c}">{estado}</span>'

def kpi(lbl,val,sub,v=""):
    cls=f"c-kpi {v}" if v else "c-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def div(): return '<div class="c-div"></div>'

# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------
def _execucao():
    with st.expander("📈 Execução", expanded=True):
        projeto = st.selectbox("Projeto", PROJETOS, key="exec_proj_cl")
        acoes = ACOES_PROJETO.get(projeto, [])
        vol = VOLUMES.get(projeto, {"atribuido":0,"realizado":0})
        atr, real = vol["atribuido"], vol["realizado"]
        pct = round(real/atr*100) if atr else 0
        fechadas = [a for a in acoes if a["estado"]=="fechada"]
        decorrer = [a for a in acoes if a["estado"]=="a_decorrer"]
        planeadas= [a for a in acoes if a["estado"]=="planeada"]

        st.html(
            '<div class="c-kpi-row">'
            +kpi("📦 Volume atribuído", str(atr),"horas","b")
            +kpi("✅ Volume realizado",  str(real),f"{pct}% executado","g")
            +kpi("🔒 Ações fechadas",   str(len(fechadas)),"concluídas","g")
            +kpi("🔵 A decorrer",        str(len(decorrer)),"em curso","b")
            +(kpi("📋 Planeadas",         str(len(planeadas)),"futuras","p") if planeadas else "")
            +'</div>'
        )
        st.progress(min(pct/100, 1.0))

        st.html(div())

        if fechadas:
            st.markdown("**✅ Ações fechadas**")
            for a in fechadas:
                st.html(f'<div class="c-card" style="border-left:3px solid #16A34A"><div style="font-weight:600;font-size:13px">{a["codigo"]}</div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')

        if decorrer:
            st.markdown("**🔵 Ações a decorrer**")
            for a in decorrer:
                st.html(f'<div class="c-card" style="border-left:3px solid #2563EB"><div style="display:flex;justify-content:space-between"><span style="font-weight:600;font-size:13px">{a["codigo"]}</span><span style="font-size:12px;color:#2563EB">{a["pct"]}%</span></div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')
                st.progress(a["pct"]/100)

        if planeadas:
            st.markdown("**📋 Ações planeadas**")
            for a in planeadas:
                st.html(f'<div class="c-card" style="border-left:3px solid #7C3AED"><div style="font-weight:600;font-size:13px">{a["codigo"]}</div><div style="font-size:12px;color:#8B94A3">{a["nome"]} · {a["empresa"]}</div></div>')

# ---------------------------------------------------------------------------
# FORMADORES
# ---------------------------------------------------------------------------
def _formadores():
    with st.expander("👤 Formadores", expanded=False):
        col_f, col_p = st.columns([3,1])
        with col_f:
            termo = st.text_input("", placeholder="Pesquisar formador...",
                                  key="form_pesq_cl", label_visibility="collapsed")
        with col_p:
            if st.button("🔍 Pesquisar", key="form_btn_cl", use_container_width=True):
                st.session_state["form_pesquisou_cl"] = True

        if not st.session_state.get("form_pesquisou_cl") and not termo:
            # Mostrar todos por defeito
            encontrados = FORMADORES
        else:
            encontrados = [f for f in FORMADORES if not termo or termo.lower() in f["nome"].lower()]

        if not encontrados:
            st.html('<div class="c-empty">Nenhum formador encontrado.</div>')
            return

        nome_sel = st.selectbox("Formador", [f["nome"] for f in encontrados], key="form_sel_cl")
        formador = next(f for f in encontrados if f["nome"] == nome_sel)

        st.html(
            f'<div style="font-size:12px;color:#8B94A3;margin-bottom:12px">'
            f'Consultor: <strong style="color:#1A1F2E">{formador["consultor"]}</strong>'
            f'&nbsp;·&nbsp;Projeto: <strong style="color:#1A1F2E">{formador["projeto"]}</strong>'
            f'</div>'
        )

        acoes = ACOES_FORMADOR.get(nome_sel, [])
        if not acoes:
            st.html('<div class="c-empty">Sem ações registadas.</div>')
            return

        for i, a in enumerate(acoes):
            f_ico  = "✅" if a["fechada"]  else "⏳"
            fat_ico= "✅" if a["faturou"]  else "❌"
            pg_ico = "💳" if a["paga"]     else "❌"

            col_info, col_dl = st.columns([5,1])
            with col_info:
                st.html(
                    f'<div class="c-card" style="border-left:3px solid {"#16A34A" if a["paga"] else "#2563EB" if a["faturou"] else "#E4E7EF"}">'
                    f'<div style="font-weight:600;font-size:13px;margin-bottom:6px">{a["acao"]}</div>'
                    f'<div style="display:flex;gap:16px;font-size:12px;color:#4B5263">'
                    f'<span>{f_ico} Fechada na Magna</span>'
                    f'<span>{fat_ico} Faturou</span>'
                    f'<span>{pg_ico} Paga</span>'
                    f'</div>'
                    f'</div>'
                )
            with col_dl:
                if a["faturou"] and a["fatura"]:
                    st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
                    st.download_button("📄", data=b"Fatura placeholder",
                                       file_name=a["fatura"], key=f"dl_cl_{nome_sel}_{i}",
                                       help="Download fatura")
                    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# EMPRESAS
# ---------------------------------------------------------------------------
def _empresas():
    with st.expander("🏢 Empresas", expanded=False):
        vista = st.radio("Vista", ["Validadas","Execução pendente"],
                         horizontal=True, key="emp_vista_cl", label_visibility="collapsed")

        estado_fil = "Validada" if vista=="Validadas" else "Execução pendente"
        lista = [e for e in EMPRESAS if e["estado"]==estado_fil]

        pesq = st.text_input("", placeholder="Pesquisar empresa...",
                             key="emp_pesq_cl", label_visibility="collapsed")
        if pesq:
            lista = [e for e in lista if pesq.lower() in e["nome"].lower()]

        if not lista:
            st.html('<div class="c-empty">Sem empresas para mostrar.</div>')
            return

        nome_sel = st.selectbox("Empresa", [e["nome"] for e in lista], key="emp_sel_cl")
        emp = next(e for e in lista if e["nome"]==nome_sel)

        if emp.get("nif"):
            st.html(f'<div style="font-size:12px;color:#8B94A3;margin-bottom:12px">NIF: <strong style="color:#1A1F2E">{emp["nif"]}</strong></div>')

        acoes = ACOES_EMPRESA.get(nome_sel, [])
        if not acoes:
            st.html('<div class="c-empty">Sem ações de formação registadas.</div>')
            return

        t_compete = t_mentores = 0.0
        for a in acoes:
            r_ico = "✅" if a["reembolso"] else "⏳"
            f_ico = "✅" if a["faturada"]  else "❌"
            p_ico = "💳" if a["paga"]      else "❌"
            t_compete  += a["valor_compete"]
            t_mentores += a["valor_mentores"]

            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Certificados", f"{a['certificados']}/{a['formandos']}")
                c2.metric("Horas", f"{a['horas']}h")
                c3.metric("A Receber do COMPETE2030", _eur(a["valor_compete"]))
                c4.metric("A Pagar à M&T (30%)", _eur(a["valor_mentores"]))
                st.html(
                    f'<div style="display:flex;gap:20px;font-size:12px;color:#4B5263;margin-top:4px">'
                    f'<span>{r_ico} Reembolso COMPETE</span>'
                    f'<span>{f_ico} Faturada à empresa</span>'
                    f'<span>{p_ico} Paga à M&T</span>'
                    f'</div>'
                )

        st.html(div())
        col_t1, col_t2 = st.columns(2)
        col_t1.metric("Total a Receber pelo COMPETE2030 (empresa recebe)", _eur(t_compete))
        col_t2.metric("Total a Pagar à M&T", _eur(t_mentores))

# ---------------------------------------------------------------------------
# FATURAÇÃO
# ---------------------------------------------------------------------------
def _faturacao():
    with st.expander("💶 Faturação", expanded=False):
        total_fat = sum(a["valor"] for a in db.acoes_em("Faturada","Paga"))
        total_pago= sum(a["valor"] for a in db.acoes_em("Paga"))
        n_conf    = len(db.acoes_em("Em confirmação"))

        st.html(
            '<div class="c-kpi-row">'
            +kpi("🧾 Total faturado",  _eur(total_fat), "acumulado","b")
            +kpi("💳 Total recebido",  _eur(total_pago),"pago","g")
            +(kpi("⏳ Em confirmação", str(n_conf),      "aguarda gestora","a") if n_conf else "")
            +'</div>'
        )
        st.html(div())

        # ---- 1. Fechadas — enviar à gestora ----
        st.markdown("**1. Ações fechadas — enviar à gestora para confirmação**")
        fechadas = db.acoes_em("Fechada","Devolvida")
        if not fechadas:
            st.html('<div class="c-empty">Sem ações por enviar.</div>')
        else:
            selecionadas = []
            for a in fechadas:
                est = db.estados()[a["id"]]
                lbl = f"{a['acao']} — {a['empresa']} — {_eur(a['valor'])}"
                if est=="Devolvida":
                    lbl += "  ↩️ devolvida"
                if st.checkbox(lbl, key=f"fat_chk_{a['id']}"):
                    selecionadas.append(a)

            if st.button("📧 Enviar à gestora", key="fat_enviar", type="primary"):
                if selecionadas:
                    for a in selecionadas: db.definir_estado(a["id"],"Em confirmação")
                    st.success(f"{len(selecionadas)} ação(ões) enviada(s). Prazo: 15 dias.")
                    st.rerun()
                else:
                    st.warning("Seleciona pelo menos uma ação.")

        # ---- 2. Em confirmação ----
        em_conf = db.acoes_em("Em confirmação")
        if em_conf:
            st.html(div())
            st.markdown("**2. A aguardar confirmação da gestora**")
            for a in em_conf:
                st.html(
                    f'<div class="c-card" style="border-left:3px solid #D97706">'
                    f'⏳ {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}'
                    f'</div>'
                )

        # ---- 3. Devolvidas ----
        devolvidas = db.acoes_em("Devolvida")
        if devolvidas:
            st.html(div())
            st.markdown("**Devolvidas pela gestora**")
            for a in devolvidas:
                com = db.comentario(a["id"])
                st.html(
                    f'<div class="c-card" style="border-left:3px solid #DC2626;background:#FEF2F2">'
                    f'↩️ <strong>{a["acao"]}</strong> — {a["empresa"]} — {_eur(a["valor"])}'
                    f'{"<br><span style=\\'font-size:12px;color:#DC2626\\'>💬 " + com + "</span>" if com else ""}'
                    f'</div>'
                )

        # ---- 4. Aceites ----
        aceites = db.acoes_em("Aceite")
        if aceites:
            st.html(div())
            st.markdown("**3. Aceites pela gestora — submeter fatura ao financeiro**")
            for a in aceites:
                st.html(
                    f'<div class="c-card" style="border-left:3px solid #16A34A">'
                    f'✅ {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}'
                    f'</div>'
                )
            total_aceite = sum(a["valor"] for a in aceites)
            st.metric("Valor a faturar ao financeiro", _eur(total_aceite))
            ficheiro = st.file_uploader("Fatura (PDF)", type=["pdf"], key="fat_upload")
            if st.button("📤 Submeter ao financeiro", key="fat_submeter", type="primary"):
                if ficheiro:
                    for a in aceites: db.definir_estado(a["id"],"Faturada")
                    st.success("Fatura submetida ao financeiro. Aguarda pagamento.")
                    st.rerun()
                else:
                    st.warning("Carrega o PDF primeiro.")

        # ---- 5. Faturadas e pagas ----
        fp = db.acoes_em("Faturada","Paga")
        if fp:
            st.html(div())
            st.markdown("**Faturadas e pagas**")
            for a in fp:
                est = db.estados()[a["id"]]
                ico = "💳 Paga" if est=="Paga" else "🧾 Aguarda pagamento"
                cls = "border-left:3px solid #16A34A" if est=="Paga" else "border-left:3px solid #2563EB"
                st.html(
                    f'<div class="c-card" style="{cls}">'
                    f'{ico} — {a["acao"]} — {a["empresa"]} — {_eur(a["valor"])}'
                    f'</div>'
                )

# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render():
    _execucao()
    _formadores()
    _empresas()
    _faturacao()
