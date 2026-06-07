"""Pagina do formador."""
from __future__ import annotations

import mimetypes
import streamlit as st

from integrations.gemini import ler_fatura
from integrations.magna import get_magna_adapter


def render(user: dict):
    st.header(f"Bem-vinda, {user['nome']}")
    tab1, tab2, tab3 = st.tabs(["📤 Submeter fatura", "📋 As minhas faturas", "📚 As minhas acoes"])

    with tab1:
        _submeter_fatura(user)
    with tab2:
        _listar_faturas(user)
    with tab3:
        _listar_acoes(user)


def _submeter_fatura(user: dict):
    st.subheader("Submeter nova fatura")

    try:
        magna = get_magna_adapter()
        acoes = magna.listar_acoes()
    except Exception as e:
        st.warning(f"Nao consegui carregar acoes da Magna: {e}")
        acoes = []

    acao_selecionada = None
    if acoes:
        nomes = [f"{a.nome} ({a.magna_id})" for a in acoes]
        escolha = st.selectbox("Acao na Magna", ["—"] + nomes)
        if escolha != "—":
            idx = nomes.index(escolha)
            acao_selecionada = acoes[idx]
    else:
        st.text_input("Nome da acao na Magna")

    ficheiro = st.file_uploader(
        "Carrega a tua fatura (PDF ou imagem)",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    if ficheiro is None:
        st.info("Carrega um ficheiro para continuar.")
        return

    if st.button("🔍 Ler fatura com IA", type="primary"):
        with st.spinner("A ler a fatura..."):
            mime = ficheiro.type or mimetypes.guess_type(ficheiro.name)[0] or "application/pdf"
            try:
                dados = ler_fatura(ficheiro.getvalue(), mime_type=mime)
            except Exception as e:
                st.error(f"Erro ao chamar Gemini: {e}")
                return

        st.success("Leitura concluida!")
        st.metric("Confianca da IA", f"{dados.confianca * 100:.0f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Numero:**", dados.numero_fatura or "—")
            st.write("**Data:**", dados.data_fatura or "—")
            st.write("**Valor:**", f"{dados.valor_total} €" if dados.valor_total else "—")
        with col2:
            st.write("**NIF emitente:**", dados.nif_emitente or "—")
            st.write("**NIF destinatario:**", dados.nif_destinatario or "—")
            st.write("**Descricao:**", dados.descricao or "—")

        if dados.erros:
            st.warning("Avisos da IA:")
            for e in dados.erros:
                st.caption(f"• {e}")

        if acao_selecionada and acao_selecionada.estado.value != "fechada":
            st.error(
                f"⚠️ Esta acao ainda esta '{acao_selecionada.estado.value}' na Magna. "
                f"Para o pagamento ser processado, tens de a fechar."
            )

        st.info("👉 Proximo passo: gravar na BD (Supabase).")


def _listar_faturas(user: dict):
    st.subheader("Historico de faturas")
    st.caption("🚧 Sera ligado ao Supabase quando a BD estiver configurada.")


def _listar_acoes(user: dict):
    st.subheader("As minhas acoes na Magna")
    try:
        magna = get_magna_adapter()
        acoes = magna.listar_acoes()
        if not acoes:
            st.info("Sem acoes. Coloca o Excel da Magna em data/magna_export.xlsx")
            return
        st.dataframe([
            {
                "ID Magna": a.magna_id, "Nome": a.nome, "Estado": a.estado.value,
                "Inicio": a.data_inicio, "Fim": a.data_fim, "Volume (h)": a.volume_horas,
            }
            for a in acoes
        ])
    except Exception as e:
        st.error(f"Erro: {e}")
