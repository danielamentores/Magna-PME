"""Tab Ações — mapa financeiro completo por ação."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import (
    eur, eur2, ptag, bdg, kpi_h, sec, div,
    CORES, BGS, ORDEM, _formador, _projeto,
)

try:
    from app.db_financeiro import get_supabase
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ---------------------------------------------------------------------------
# FÓRMULAS FINANCEIRAS
# ---------------------------------------------------------------------------
def calc_consultor(formandos_cert: int, vol_cert: float) -> float:
    """Valor da NH do consultor = volume_certificado × taxa."""
    if not vol_cert:
        return 0.0
    taxa = 3.12 if formandos_cert >= 13 else 2.50
    return round(vol_cert * taxa, 2)

def calc_compete(projeto: str, vol_cert: float) -> float:
    """Valor que a MENTORES recebe do COMPETE.
    MENTORES: vol_cert × 7,12
    Outros:   0,5 × vol_cert × 7,12 + 0,5 × vol_cert × 5,00
    """
    if not vol_cert:
        return 0.0
    if projeto == "MENTORES":
        return round(vol_cert * 7.12, 2)
    else:
        return round(0.5 * vol_cert * 7.12 + 0.5 * vol_cert * 5.0, 2)

def calc_empresa_recebe(dimensao: str, vol_cert: float,
                        form_desf: int = 0, form_nao_desf: int = 0) -> float:
    """Valor que a empresa recebe do COMPETE (70%)."""
    if not dimensao or not vol_cert:
        return 0.0
    if dimensao in ("Pequena", "Micro"):
        return round(0.7 * 7.50 * vol_cert, 2)
    elif dimensao == "Média":
        return round((0.7 * 7.50 * form_desf) + (0.6 * 7.50 * form_nao_desf), 2)
    return 0.0

def calc_faturado_empresa(dimensao: str, vol_cert: float,
                          form_desf: int = 0, form_nao_desf: int = 0) -> float:
    """Valor faturado à empresa pelos 30%."""
    if not dimensao or not vol_cert:
        return 0.0
    if dimensao in ("Pequena", "Micro"):
        return round(0.3 * 7.50 * vol_cert, 2)
    elif dimensao == "Média":
        return round((0.3 * 7.50 * form_desf) + (0.4 * 7.50 * form_nao_desf), 2)
    return 0.0

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_ACOES = [
    # volume_cert = volume_horas * formandos_certificados
    {
        "id": "a1", "codigo": "LIKE GARDEN.2.PCE",
        "nome": "Escalada e desmanche de árvores com motosserra",
        "empresa_cliente": "Like Garden", "projeto": "MENTORES",
        "consultor_nome": "Etapas Pioneiras, Lda",
        "formador_nome": "Ana Silva", "valor_fatura_formador": 1800.0,
        "dimensao": "Pequena", "volume_horas": 50,
        "formandos_certificados": 18, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a2", "codigo": "CAMOESAS.03.PCE",
        "nome": "Segurança nos trabalhos de construção civil",
        "empresa_cliente": "CAMOESAS, LDA", "projeto": "ANIET",
        "consultor_nome": "Etapas Pioneiras, Lda",
        "formador_nome": "Bruno Costa", "valor_fatura_formador": None,
        "dimensao": "Pequena", "volume_horas": 24,
        "formandos_certificados": 16, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a3", "codigo": "FENABEL.GEPSLT_16",
        "nome": "Gestão de emergências e primeiros socorros",
        "empresa_cliente": "Fenabel, S.A", "projeto": "MENTORES",
        "consultor_nome": "Winet Consulting, Lda",
        "formador_nome": "Fátima Sorte", "valor_fatura_formador": 1646.40,
        "dimensao": "Média", "volume_horas": 16,
        "formandos_certificados": 14, "formandos_desf": 8, "formandos_nao_desf": 6,
        "estado": "fechada",
    },
    {
        "id": "a4", "codigo": "PROD.01.FA",
        "nome": "Op. Seg. Equip. Movimentação Cargas 1",
        "empresa_cliente": "J.A. Veiga de Macedo", "projeto": "PRODUTECH",
        "consultor_nome": "Etapas Pioneiras, Lda",
        "formador_nome": "Ivo Daniel Monteiro", "valor_fatura_formador": 3200.0,
        "dimensao": "Pequena", "volume_horas": 30,
        "formandos_certificados": 16, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a5", "codigo": "APIMA.01.CS",
        "nome": "Atendimento e experiência do cliente",
        "empresa_cliente": "Comércio Lisboa, Lda", "projeto": "APIMA",
        "consultor_nome": "FormaConsult, Unip. Lda",
        "formador_nome": "Sofia Rodrigues", "valor_fatura_formador": 1375.0,
        "dimensao": "Pequena", "volume_horas": 20,
        "formandos_certificados": 11, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "a_decorrer",
    },
]

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_acoes() -> list[dict]:
    if not SUPABASE_OK:
        return _MOCK_ACOES
    try:
        r = get_supabase().table("acoes").select(
            "id,codigo,nome,empresa_cliente,estado,dimensao,"
            "volume_horas,formandos_certificados,formandos_desf,formandos_nao_desf,"
            "profiles!consultor_id(nome),"
            "faturas(valor,estado,profiles!formador_id(nome))"
        ).order("created_at", desc=True).execute()
        acoes = []
        for a in r.data:
            cons = (a.get("profiles") or {}).get("nome") or "—"
            fats = a.get("faturas") or []
            fat  = fats[0] if fats else {}
            a["consultor_nome"]         = cons
            a["formador_nome"]          = (fat.get("profiles") or {}).get("nome") or "—"
            a["valor_fatura_formador"]  = fat.get("valor")
            acoes.append(a)
        return acoes if acoes else _MOCK_ACOES
    except:
        return _MOCK_ACOES

# ---------------------------------------------------------------------------
# HELPERS VISUAIS
# ---------------------------------------------------------------------------
def _val_cell(v: float | None, placeholder: str = "—") -> str:
    if v is None or v == 0:
        return f'<span style="color:#8B94A3">{placeholder}</span>'
    return f'<span style="font-weight:600">{eur2(v)}</span>'

def _margem(compete, consultor, formador) -> tuple[float, str]:
    """Margem bruta M&T = COMPETE - consultor - formador."""
    if not compete:
        return 0.0, "—"
    c = consultor or 0.0
    f = formador  or 0.0
    m = compete - c - f
    cor = "#16A34A" if m >= 0 else "#DC2626"
    return m, cor

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render_acoes(user: dict):
    acoes = _get_acoes()

    # ── Filtros ──
    col_p, col_e, col_s = st.columns([2, 2, 2])
    with col_p:
        projs = ["Todos"] + sorted({a.get("projeto","") for a in acoes if a.get("projeto")})
        filtro_proj = st.selectbox("Projeto", projs, key="ac_fin_proj")
    with col_e:
        estados = ["Todos", "fechada", "a_decorrer", "planeada"]
        filtro_est = st.selectbox("Estado", estados, key="ac_fin_est",
                                  format_func=lambda x: {
                                      "Todos":"Todos","fechada":"✅ Fechada",
                                      "a_decorrer":"🔵 A decorrer","planeada":"📋 Planeada"
                                  }.get(x, x))
    with col_s:
        pesq = st.text_input("", placeholder="Pesquisar código ou empresa…",
                             key="ac_fin_pesq", label_visibility="collapsed")

    if filtro_proj != "Todos":
        acoes = [a for a in acoes if a.get("projeto") == filtro_proj]
    if filtro_est != "Todos":
        acoes = [a for a in acoes if a.get("estado") == filtro_est]
    if pesq:
        p = pesq.lower()
        acoes = [a for a in acoes if p in (a.get("codigo","")).lower()
                 or p in (a.get("empresa_cliente","")).lower()
                 or p in (a.get("nome","")).lower()]

    # ── KPIs globais ──
    def _vol(a): return int(a.get("volume_horas") or 0) * int(a.get("formandos_certificados") or 0)
    total_compete   = sum(calc_compete(a.get("projeto",""), _vol(a)) for a in acoes)
    total_consultor = sum(calc_consultor(a.get("formandos_certificados",0), _vol(a)) for a in acoes)
    total_formador  = sum(a.get("valor_fatura_formador") or 0 for a in acoes)
    total_fat_emp   = sum(calc_faturado_empresa(
        a.get("dimensao",""), _vol(a),
        a.get("formandos_desf",0), a.get("formandos_nao_desf",0)) for a in acoes)
    margem_total   = total_compete - total_consultor - total_formador

    st.html(
        '<div class="fin-kpi-row">'
        + kpi_h("💶 COMPETE recebido",   eur(total_compete),   f"{len(acoes)} ações", "g")
        + kpi_h("🤝 Total consultores",  eur(total_consultor), "NH emitidas",         "b")
        + kpi_h("👤 Total formadores",   eur(total_formador),  "faturas",             "b")
        + kpi_h("🏢 Faturado empresas",  eur(total_fat_emp),   "30% M&T",             "a")
        + kpi_h("📊 Margem bruta M&T",   eur(margem_total),
                "COMPETE − consultores − formadores",
                "g" if margem_total >= 0 else "r")
        + '</div>'
    )

    st.html(div())
    st.markdown(sec(f"Ações ({len(acoes)})",
                    "Mapa financeiro completo. COMPETE recebido − consultores − formadores = margem M&T."),
                unsafe_allow_html=True)

    if not acoes:
        st.html('<div class="fin-empty">Nenhuma ação encontrada para este filtro.</div>')
        return

    for a in acoes:
        codigo   = a.get("codigo") or "—"
        nome     = a.get("nome") or "—"
        empresa  = a.get("empresa_cliente") or "—"
        proj     = a.get("projeto") or "—"
        dim      = a.get("dimensao") or ""
        est      = a.get("estado") or "—"
        fc       = int(a.get("formandos_certificados") or 0)
        fd       = int(a.get("formandos_desf") or 0)
        fnd      = int(a.get("formandos_nao_desf") or 0)
        ch       = int(a.get("volume_horas") or 0)
        vol      = ch * fc  # volume certificado = carga_horária × formandos_certificados
        consultor= a.get("consultor_nome") or "—"
        formador = a.get("formador_nome") or "—"
        val_form = a.get("valor_fatura_formador")

        v_cons   = calc_consultor(fc, vol)
        v_comp   = calc_compete(proj, vol)
        v_emp_r  = calc_empresa_recebe(dim, vol, fd, fnd)
        v_fat_e  = calc_faturado_empresa(dim, vol, fd, fnd)
        margem, m_cor = _margem(v_comp, v_cons, val_form)

        with st.container(border=True):
            # Cabeçalho
            col_head, col_est = st.columns([5, 2])
            with col_head:
                st.html(
                    f'<div style="margin-bottom:8px">'
                    f'<span style="font-weight:700;font-size:14px">{codigo}</span>'
                    f'&nbsp;&nbsp;{ptag(proj)}'
                    f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">'
                    f'{nome[:60]} · {empresa}'
                    f'</div>'
                    f'</div>'
                )
            with col_est:
                st.html(f'<div style="text-align:right;padding-top:4px">{bdg(est)}'
                        f'<div style="font-size:11px;color:#8B94A3;margin-top:3px">'
                        f'{fc} formandos cert. · {dim or "—"}'
                        f'</div></div>')

            st.html('<div style="height:1px;background:#F0F2F5;margin:8px 0"></div>')

            # Tabela financeira
            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Consultor</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">{consultor}</div>'
                f'<div style="font-weight:700;font-size:14px;color:#2563EB">{eur2(v_cons)}</div>'
            )
            c2.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Formador</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">{formador}</div>'
                f'<div style="font-weight:700;font-size:14px;color:#2563EB">'
                f'{_val_cell(val_form,"Aguarda fatura")}</div>'
            )
            c3.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">'
                f'COMPETE recebido</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">M&T recebe</div>'
                f'<div style="font-weight:700;font-size:14px;color:#16A34A">'
                f'{_val_cell(v_comp)}</div>'
            )
            c4.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">'
                f'Faturado empresa</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">30% M&T</div>'
                f'<div style="font-weight:700;font-size:14px;color:#D97706">'
                f'{_val_cell(v_fat_e)}</div>'
            )
            c5.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">'
                f'Empresa recebe</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">70% COMPETE</div>'
                f'<div style="font-weight:700;font-size:14px;color:#8B94A3">'
                f'{_val_cell(v_emp_r)}</div>'
            )
            c6.html(
                f'<div style="font-size:11px;color:#8B94A3;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">'
                f'Margem M&T</div>'
                f'<div style="font-size:12px;color:#4B5263;margin-bottom:4px">'
                f'COMPETE − cons. − form.</div>'
                f'<div style="font-weight:700;font-size:15px;color:{m_cor}">'
                f'{eur2(margem) if v_comp else "—"}</div>'
            )
