"""Dados e estado partilhado da faturação (fase visual).

O estado vive no st.session_state, por isso é partilhado entre o perfil
do coordenador e o da gestora dentro da mesma sessão. Quando ligares a BD,
troca estas funções por leitura/escrita reais.
"""
import streamlit as st

ACOES_FATURACAO = [
    {"id": "f1", "acao": "Ação 1 - Cibersegurança",    "empresa": "Empresa Alfa, Lda", "valor": 3000.0},
    {"id": "f2", "acao": "Ação 2 - Cloud",             "empresa": "Empresa Alfa, Lda", "valor": 2100.0},
    {"id": "f3", "acao": "Ação 3 - Marketing Digital",  "empresa": "Beta Serviços, SA", "valor": 4000.0},
    {"id": "f4", "acao": "Ação 4 - Dados",             "empresa": "Gama Comércio, Lda", "valor": 1800.0},
    {"id": "f5", "acao": "Ação 5 - Gestão de Equipas",  "empresa": "Empresa Alfa, Lda", "valor": 2500.0},
    {"id": "f6", "acao": "Ação 6 - Vendas",            "empresa": "Beta Serviços, SA", "valor": 1600.0},
]

ESTADOS_FAT_INICIAIS = {
    "f1": "Paga",
    "f2": "Faturada",
    "f3": "Aceite",
    "f4": "Fechada",
    "f5": "Em confirmação",
    "f6": "Devolvida",
}

_CHAVE = "fat_estado_partilhado"


def estados() -> dict:
    if _CHAVE not in st.session_state:
        st.session_state[_CHAVE] = dict(ESTADOS_FAT_INICIAIS)
    return st.session_state[_CHAVE]


def acoes_em(*ests) -> list:
    e = estados()
    return [a for a in ACOES_FATURACAO if e.get(a["id"]) in ests]


def definir_estado(acao_id: str, novo: str):
    estados()[acao_id] = novo


def eur(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"
