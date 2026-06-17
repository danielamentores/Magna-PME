
    "APCMC": {"atribuido": 1200, "realizado": 780},
}

projeto = st.selectbox("Seleciona o projeto", PROJETOS, key="exec_projeto")

if projeto == "APCMC":
    vol = VOLUMES["APCMC"]
    atribuido = vol["atribuido"]
    realizado = vol["realizado"]
    pct = (realizado / atribuido * 100) if atribuido else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Volume atribuído", f"{atribuido}")
    c2.metric("Volume realizado", f"{realizado}")
    c3.metric("Execução", f"{pct:.0f}%")

    st.progress(min(pct / 100, 1.0))
