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

def _ed(v) -> str:
    """Valor com € à direita, 2 decimais."""
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "— €"

# ---------------------------------------------------------------------------
# FÓRMULAS FINANCEIRAS
# ---------------------------------------------------------------------------
def calc_formador(formandos_cert: int, horas: int = 25) -> float:
    """Valor do formador = horas × taxa (20€/h se <13 formandos, 25€/h se >=13)."""
    taxa = 25.0 if formandos_cert >= 13 else 20.0
    return round(horas * taxa, 2)

def calc_consultor(formandos_cert: int, vol_cert: float) -> float:
    """Valor da NH do consultor = volume_certificado × taxa."""
    if not vol_cert:
        return 0.0
    taxa = 3.12 if formandos_cert >= 13 else 2.50
    return round(vol_cert * taxa, 2)

def calc_compete(projeto: str, vol_cert: float) -> float:
    """Valor que a M&T recebe do COMPETE (70% da comparticipação).
    MENTORES:  vol × 7,12 × 0,7
    Outros:    0,5 × vol × 7,12 × 0,7 + 0,5 × vol × 5,00 × 0,7
    """
    if not vol_cert:
        return 0.0
    if projeto == "MENTORES":
        return round(vol_cert * 7.12 * 0.7, 2)
    else:
        return round(0.5 * vol_cert * 7.12 * 0.7 + 0.5 * vol_cert * 5.0 * 0.7, 2)

def calc_faturado_empresa(projeto: str, vol_cert: float) -> float:
    """Valor que a M&T fatura à empresa (30% da comparticipação).
    MENTORES:  vol × 7,12 × 0,3
    Outros:    0,5 × vol × 7,12 × 0,3 + 0,5 × vol × 5,00 × 0,3
    """
    if not vol_cert:
        return 0.0
    if projeto == "MENTORES":
        return round(vol_cert * 7.12 * 0.3, 2)
    else:
        return round(0.5 * vol_cert * 7.12 * 0.3 + 0.5 * vol_cert * 5.0 * 0.3, 2)

def calc_empresa_recebe(projeto: str, vol_cert: float) -> float:
    """Valor que a empresa recebe diretamente do COMPETE2030 (informativo).
    = comparticipação total − o que M&T recebe − o que M&T fatura
    Simplificado: igual ao faturado_empresa (os 30% que a empresa paga à M&T
    são financiados pelo COMPETE, portanto a empresa recebe 100% da comparticipação
    mas paga 30% à M&T).
    Para apresentação: vol × taxa_total (sem desconto).
    MENTORES: vol × 7,12
    Outros:   0,5 × vol × 7,12 + 0,5 × vol × 5,00
    """
    if not vol_cert:
        return 0.0
    if projeto == "MENTORES":
        return round(vol_cert * 7.12, 2)
    else:
        return round(0.5 * vol_cert * 7.12 + 0.5 * vol_cert * 5.0, 2)

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_ACOES = [
    # volume_cert = volume_horas * formandos_certificados
    # valor_fatura_formador = horas * taxa (25€ se >=13 form, 20€ se <13)
    {
        "id": "a1", "codigo": "LIKE GARDEN.2.PCE",
        "nome": "Escalada e desmanche de árvores com motosserra",
        "empresa_cliente": "Like Garden", "projeto": "MENTORES",
        "consultor_nome": "Consultor 1",
        "formador_nome": "Formador 1", "valor_fatura_formador": 625.0,  # 25h * 25€
        "dimensao": "Pequena", "volume_horas": 25,
        "formandos_certificados": 18, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a2", "codigo": "CAMOESAS.03.PCE",
        "nome": "Segurança nos trabalhos de construção civil",
        "empresa_cliente": "CAMOESAS, LDA", "projeto": "ANIET",
        "consultor_nome": "Consultor 1",
        "formador_nome": "Formador 2", "valor_fatura_formador": None,  # ainda não faturou
        "dimensao": "Pequena", "volume_horas": 25,
        "formandos_certificados": 16, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a3", "codigo": "FENABEL.GEPSLT_16",
        "nome": "Gestão de emergências e primeiros socorros",
        "empresa_cliente": "Fenabel, S.A", "projeto": "MENTORES",
        "consultor_nome": "Consultor 2",
        "formador_nome": "Formador 3", "valor_fatura_formador": 400.0,  # 16h * 25€
        "dimensao": "Média", "volume_horas": 16,
        "formandos_certificados": 14, "formandos_desf": 8, "formandos_nao_desf": 6,
        "estado": "fechada",
    },
    {
        "id": "a4", "codigo": "PROD.01.FA",
        "nome": "Op. Seg. Equip. Movimentação Cargas 1",
        "empresa_cliente": "J.A. Veiga de Macedo", "projeto": "PRODUTECH",
        "consultor_nome": "Consultor 1",
        "formador_nome": "Formador 4", "valor_fatura_formador": 625.0,  # 25h * 25€
        "dimensao": "Pequena", "volume_horas": 25,
        "formandos_certificados": 16, "formandos_desf": 0, "formandos_nao_desf": 0,
        "estado": "fechada",
    },
    {
        "id": "a5", "codigo": "APIMA.01.CS",
        "nome": "Atendimento e experiência do cliente",
        "empresa_cliente": "Comércio Lisboa, Lda", "projeto": "APIMA",
        "consultor_nome": "Consultor 3",
        "formador_nome": "Formador 5", "valor_fatura_formador": 500.0,  # 25h * 20€ (<13)
        "dimensao": "Pequena", "volume_horas": 25,
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
    return f'<span style="font-weight:600">{_ed(v)}</span>'

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
    total_formador  = sum(a.get("valor_fatura_formador") or calc_formador(a.get("formandos_certificados",0), a.get("volume_horas",25)) for a in acoes)
    total_fat_emp   = sum(calc_faturado_empresa(a.get("projeto",""), _vol(a)) for a in acoes)
    total_margem    = sum((calc_compete(a.get("projeto",""), _vol(a)) + calc_faturado_empresa(a.get("projeto",""), _vol(a)))
                         - (calc_consultor(a.get("formandos_certificados",0), _vol(a))
                            + (a.get("valor_fatura_formador") or calc_formador(a.get("formandos_certificados",0), a.get("volume_horas",25))))
                         for a in acoes)
    margem_total   = total_compete - total_consultor - total_formador

    st.html(
        '<div class="fin-kpi-row">'
        + kpi_h("💶 M&T Recebe do COMPETE2030",        _ed(total_compete),   f"{len(acoes)} ações", "g")
        + kpi_h("🏢 M&T Fatura às Empresas",_ed(total_fat_emp),   "a cobrar",            "a")
        + kpi_h("🤝 Custo Consultores",       _ed(total_consultor), "NH total",            "b")
        + kpi_h("👤 Custo Formadores",        _ed(total_formador),  "faturas",             "b")
        + kpi_h("📊 Margem Bruta M&T",  _ed(total_margem),
                "COMPETE+Empresa − (cons.+form.)",
                "g" if total_margem >= 0 else "r")
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
        val_form_contrato = calc_formador(fc, ch if ch else 25)
        val_form = a.get("valor_fatura_formador") or val_form_contrato

        v_cons   = calc_consultor(fc, vol)
        v_comp   = calc_compete(proj, vol)
        v_fat_e  = calc_faturado_empresa(proj, vol)
        v_emp_r  = calc_empresa_recebe(proj, vol)
        receita_total = v_comp + v_fat_e
        custo_total   = v_cons + (val_form or val_form_contrato)
        margem        = round(receita_total - custo_total, 2)
        m_cor         = "#16A34A" if margem >= 0 else "#DC2626"

        vol_display = f"{ch}h × {fc} = {vol}" if ch and fc else "—"
        form_real  = a.get("valor_fatura_formador")
        form_label = _ed(form_real) if form_real else f"Contrato: {_ed(val_form_contrato)}"
        form_cor   = "#2563EB" if form_real else "#8B94A3"
        mg_bg      = "#F0FDF4" if margem >= 0 else "#FEF2F2"

        st.html(
            '<div style="background:#fff;border:1px solid #E4E7EF;border-radius:12px;margin-bottom:12px;overflow:hidden">' +

            # ── Cabeçalho ──
            '<div style="padding:12px 18px;border-bottom:1px solid #F0F2F5;display:flex;align-items:center;justify-content:space-between">' +
            f'<div style="flex:1"><div style="display:flex;align-items:center;gap:8px;margin-bottom:3px"><span style="font-weight:700;font-size:14px;color:#1A1F2E">{codigo}</span>{ptag(proj)}{bdg(est)}</div><div style="font-size:12px;color:#4B5263">{nome[:65]} · <span style="color:#8B94A3">{empresa}</span></div></div>' +
            f'<div style="text-align:right;font-size:12px;color:#8B94A3;flex-shrink:0;margin-left:16px"><span style="color:#2A7A8C;font-weight:600">Volume certificado: {vol}h ({ch}h × {fc} formandos certificados)</span> · Dimensão: {dim or "—"}</div>' +
            '</div>' +

            # ── Grid 6 colunas: consultor | formador | M&T recebe | M&T fatura | Empresa recebe | Margem ──
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr 1.2fr;border-top:1px solid #F0F2F5">' +

            # Consultor
            f'<div style="padding:12px 14px;border-right:1px solid #F0F2F5"><div style="font-size:10px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Consultor</div><div style="font-size:12px;color:#4B5263;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{consultor}</div><div style="font-size:15px;font-weight:700;color:#2563EB">{_ed(v_cons)}</div></div>' +

            # Formador
            f'<div style="padding:12px 14px;border-right:1px solid #F0F2F5"><div style="font-size:10px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Formador</div><div style="font-size:12px;color:#4B5263;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{formador}</div><div style="font-size:15px;font-weight:700;color:{form_cor}">{form_label}</div></div>' +

            # M&T recebe
            f'<div style="padding:12px 14px;border-right:1px solid #F0F2F5;background:#FAFFFE"><div style="font-size:10px;color:#16A34A;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">M&T recebe</div><div style="font-size:11px;color:#8B94A3;margin-bottom:4px">COMPETE2030</div><div style="font-size:15px;font-weight:700;color:#16A34A">{_ed(v_comp) if v_comp else "—"}</div></div>' +

            # M&T fatura
            f'<div style="padding:12px 14px;border-right:1px solid #F0F2F5;background:#FFFDF5"><div style="font-size:10px;color:#D97706;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">M&T fatura</div><div style="font-size:11px;color:#8B94A3;margin-bottom:4px">Empresa</div><div style="font-size:15px;font-weight:700;color:#D97706">{_ed(v_fat_e) if v_fat_e else "—"}</div></div>' +

            # Empresa recebe
            f'<div style="padding:12px 14px;border-right:1px solid #F0F2F5"><div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Empresa recebe</div><div style="font-size:11px;color:#8B94A3;margin-bottom:4px">COMPETE2030</div><div style="font-size:15px;font-weight:700;color:#6B7280">{_ed(v_emp_r) if v_emp_r else "—"}</div></div>' +

            # Margem
            f'<div style="padding:12px 14px;background:{mg_bg}"><div style="font-size:10px;color:{m_cor};font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Margem M&T</div><div style="font-size:11px;color:#8B94A3;margin-bottom:4px">COMPETE+Emp.−(cons.+form.)</div><div style="font-size:16px;font-weight:700;color:{m_cor}">{_ed(margem) if v_comp else "—"}</div></div>' +

            '</div></div>'
        )
