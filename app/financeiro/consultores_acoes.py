"""Tab Consultores & Ações — financeiro."""
from __future__ import annotations
import streamlit as st
from app.financeiro.consultores import render_consultores_financeiro
from app.financeiro.acoes import render_acoes

def render_consultores_acoes(user: dict):
    subtab1, subtab2 = st.tabs(["🤝 Consultores", "📋 Ações"])
    with subtab1:
        render_consultores_financeiro(user)
    with subtab2:
        render_acoes(user)
