"""Tab Faturação Empresas — página do financeiro."""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
import streamlit as st
import pandas as pd
import io

try:
    from app.db_financeiro import get_supabase, get_supabase_admin, _log_evento
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

_CSS = """
<style>
.fin-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 24px}
.fin-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:130px}
.fin-kpi.a{border-top:3px solid #D97706}.fin-kpi.b{border-top:3px solid #2563EB}
.fin-kpi.g{border-top:3px solid #16A34A}.fin-kpi.r{border-top:3px solid #DC2626}
.fin-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.fin-kpi .val{font-size:23px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.fin-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}
.fin-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;
          padding:12px 14px;margin-bottom:8px}
.fin-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.fin-ptag{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px}
.fin-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.fin-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.fin-div{height:1px;background:#E4E7EF;margin:24px 0 20px}
.fin-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;
           padding:20px;text-align:center;color:#8B94A3;font-size:13px}
</style>
"""

CORES = {"MENTORES":"#2563EB","ANIET":"#16A34A","APCMC":"#D97706",
         "APIMA":"#9D174D","PRODUTECH":"#7C3AED","CALÇADO":"#0F766E"}
BGS   = {"MENTORES":"#EEF3FD","ANIET":"#F0FDF4","APCMC":"#FFFBEB",
         "APIMA":"#FDF2F8","PRODUTECH":"#F5F3FF","CALÇADO":"#F0FDFA"}

DIMENSOES = ["Micro", "Pequena", "Média"]
ESTADOS_ORDEM = ["por_faturar", "fatura_emitida", "pago"]

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_ACOES_FECHADAS = [
    {"id":"a1","magna_id":"01195000","codigo":"LIKE GARDEN.2.PCE","nome":"Escalada e desmanche de árvores",
     "empresa_cliente":"Like Garden","nif_empresa":"509408486","dimensao":"Pequena",
     "volume_horas":50,"formandos_certificados":18,"projeto":"MENTORES",
     "formandos_desf":0,"formandos_nao_desf":0},
    {"id":"a2","magna_id":"01196000","codigo":"CAMOESAS.03.PCE","nome":"Segurança nos trabalhos de construção civil",
     "empresa_cliente":"CAMOESAS, LDA","nif_empresa":"508392594","dimensao":"Pequena",
     "volume_horas":24,"formandos_certificados":16,"projeto":"ANIET",
     "formandos_desf":0,"formandos_nao_desf":0},
    {"id":"a3","magna_id":"01195000","codigo":"FENABEL.GEPSLT_16","nome":"Gestão de emergências e primeiros socorros",
     "empresa_cliente":"Fenabel, S.A","nif_empresa":"502815795","dimensao":"Média",
     "volume_horas":16,"formandos_certificados":14,"projeto":"MENTORES",
     "formandos_desf":8,"formandos_nao_desf":6},
    {"id":"a4","magna_id":"01195000","codigo":"JMS.PCE.01","nome":"Literacia digital - iniciação",
     "empresa_cliente":"J. Moreira da Silva & Filhos S.A.","nif_empresa":"","dimensao":"Média",
     "volume_horas":25,"formandos_certificados":10,"projeto":"MENTORES",
     "formandos_desf":4,"formandos_nao_desf":6},
    {"id":"a5","magna_id":"01196000","codigo":"MECANIDRAULICA.2.PCE","nome":"Operar em Segurança Equipamentos de Elevação",
     "empresa_cliente":"Mecanidráulica","nif_empresa":"510033423","dimensao":"Pequena",
     "volume_horas":32,"formandos_certificados":22,"projeto":"ANIET",
     "formandos_desf":0,"formandos_nao_desf":0},
]

_MOCK_FAT_EMPRESAS = [
    {"id":"fe1","acao_id":"a1","empresa":"Like Garden","nif_empresa":"509408486",
     "dimensao":"Pequena","volume":900.0,"formandos_desf":0,"formandos_nao_desf":0,
     "valor_30pct":2025.00,"estado":"pago","numero_fatura":"FT2026/E001",
     "data_fatura":"2026-04-15","data_pagamento":"2026-05-10","valor_recebido":2025.00,
     "notas":"","projeto":"MENTORES","codigo":"LIKE GARDEN.2.PCE"},
    {"id":"fe2","acao_id":"a2","empresa":"CAMOESAS, LDA","nif_empresa":"508392594",
     "dimensao":"Pequena","volume":384.0,"formandos_desf":0,"formandos_nao_desf":0,
     "valor_30pct":864.00,"estado":"fatura_emitida","numero_fatura":"FT2026/E002",
     "data_fatura":"2026-05-02","data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"ANIET","codigo":"CAMOESAS.03.PCE"},
    {"id":"fe3","acao_id":"a3","empresa":"Fenabel, S.A","nif_empresa":"502815795",
     "dimensao":"Média","volume":224.0,"formandos_desf":8,"formandos_nao_desf":6,
     "valor_30pct":453.00,"estado":"fatura_emitida","numero_fatura":"FT2026/E003",
     "data_fatura":"2026-05-15","data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"MENTORES","codigo":"FENABEL.GEPSLT_16"},
    {"id":"fe4","acao_id":"a4","empresa":"J. Moreira da Silva & Filhos S.A.","nif_empresa":"",
     "dimensao":"Média","volume":250.0,"formandos_desf":4,"formandos_nao_desf":6,
     "valor_30pct":315.00,"estado":"por_faturar","numero_fatura":None,
     "data_fatura":None,"data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"MENTORES","codigo":"JMS.PCE.01"},
    {"id":"fe5","acao_id":"a5","empresa":"Mecanidráulica","nif_empresa":"510033423",
     "dimensao":"Pequena","volume":704.0,"formandos_desf":0,"formandos_nao_desf":0,
     "valor_30pct":1584.00,"estado":"por_faturar","numero_fatura":None,
     "data_fatura":None,"data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"ANIET","codigo":"MECANIDRAULICA.2.PCE"},
    {"id":"fe6","acao_id":"a1","empresa":"Horto da Circunvalação","nif_empresa":"510575617",
     "dimensao":"Pequena","volume":144.0,"formandos_desf":0,"formandos_nao_desf":0,
     "valor_30pct":324.00,"estado":"por_faturar","numero_fatura":None,
     "data_fatura":None,"data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"MENTORES","codigo":"TALT_16"},
    {"id":"fe7","acao_id":"a2","empresa":"Forestcorte Portugal Exploração Florestal","nif_empresa":"505765667",
     "dimensao":"Média","volume":200.0,"formandos_desf":3,"formandos_nao_desf":5,
     "valor_30pct":225.00,"estado":"pago","numero_fatura":"FT2026/E004",
     "data_fatura":"2026-03-20","data_pagamento":"2026-04-18","valor_recebido":225.00,
     "notas":"","projeto":"ANIET","codigo":"FORESTCORTE.2.PCE"},
    {"id":"fe8","acao_id":"a3","empresa":"ISTSTONE e TOPÁZIO FAVORITO","nif_empresa":"510731422",
     "dimensao":"Média","volume":168.0,"formandos_desf":5,"formandos_nao_desf":16,
     "valor_30pct":594.00,"estado":"fatura_emitida","numero_fatura":"FT2026/E005",
     "data_fatura":"2026-05-28","data_pagamento":None,"valor_recebido":None,
     "notas":"","projeto":"ANIET","codigo":"GEOEMC_1"},
]

# ---------------------------------------------------------------------------
# FÓRMULA 30%
# ---------------------------------------------------------------------------
def calcular_30pct(dimensao: str, volume: float, form_desf: int = 0, form_nao_desf: int = 0) -> float:
    """
    Micro/Pequena: 0,3 × 7,5 × volume
    Média: (0,3 × 7,5 × form_desf) + (0,4 × 7,5 × form_nao_desf)
           onde volume = ch × formandos_certificados
    """
    if dimensao in ("Micro", "Pequena"):
        return round(0.3 * 7.5 * volume, 2)
    elif dimensao == "Média":
        return round((0.3 * 7.5 * form_desf) + (0.4 * 7.5 * form_nao_desf), 2)
    return 0.0

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def eur(v):
    try: return f"€\u202f{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "€ —"

def ptag(p):
    c = CORES.get(p, "#6B7280"); b = BGS.get(p, "#F3F4F6")
    return f'<span class="fin-ptag" style="background:{b};color:{c}">{p}</span>'

def bdg_estado(estado):
    M = {
        "por_faturar":    ("#F3F4F6","#6B7280","Por faturar"),
        "fatura_emitida": ("#EEF3FD","#2563EB","Fatura emitida"),
        "pago":           ("#F0FDF4","#16A34A","Pago"),
    }
    bg, c, l = M.get(estado, ("#F3F4F6","#6B7280", estado))
    return f'<span class="fin-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi_h(lbl, val, sub, v=""):
    cls = f"fin-kpi {v}" if v else "fin-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def sec(t, s=""):
    sub = f'<p class="fin-secs">{s}</p>' if s else ""
    return f'<p class="fin-sec">{t}</p>{sub}'

def div(): return '<div class="fin-div"></div>'

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_acoes_faturar():
    """Ações fechadas para criar registos de faturação."""
    if not SUPABASE_OK: return _MOCK_ACOES_FECHADAS
    try:
        r = get_supabase().table("acoes").select(
            "id,magna_id,codigo,nome,empresa_cliente,estado"
        ).eq("estado","fechada").execute()
        return r.data
    except: return []

def _get_fat_empresas(filtro_estado=None, filtro_proj=None):
    if not SUPABASE_OK:
        d = list(_MOCK_FAT_EMPRESAS)
        if filtro_estado and filtro_estado != "Todos": d = [x for x in d if x["estado"]==filtro_estado]
        if filtro_proj and filtro_proj != "Todos":     d = [x for x in d if x.get("projeto")==filtro_proj]
        return d
    try:
        q = get_supabase().table("faturacao_empresas").select(
            "id,acao_id,empresa,nif_empresa,dimensao,volume,formandos_desf,formandos_nao_desf,"
            "valor_30pct,estado,numero_fatura,data_fatura,data_pagamento,valor_recebido,notas,"
            "acoes(codigo,nome,magnitude_id)"
        ).order("created_at", desc=True)
        if filtro_estado and filtro_estado != "Todos": q = q.eq("estado", filtro_estado)
        r = q.execute()
        return r.data
    except: return []

def _criar_fat_empresa(dados: dict) -> bool:
    if not SUPABASE_OK:
        novo = {**dados, "id": f"fe{len(_MOCK_FAT_EMPRESAS)+1}"}
        _MOCK_FAT_EMPRESAS.append(novo)
        return True
    try:
        get_supabase_admin().table("faturacao_empresas").insert(dados).execute()
        _log_evento("fat_empresa_criada", f"Faturação empresa criada: {dados.get('empresa')}", dados)
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def _atualizar_fat_empresa(fe_id: str, updates: dict) -> bool:
    if not SUPABASE_OK:
        for i, x in enumerate(st.session_state.mock_fe):
            if x["id"] == fe_id:
                st.session_state.mock_fe[i].update(updates)
        return True
    try:
        get_supabase_admin().table("faturacao_empresas").update(updates).eq("id", fe_id).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render_faturacao_empresas(user: dict):
    st.html(_CSS)

    if not SUPABASE_OK and "mock_fe" not in st.session_state:
        st.session_state.mock_fe = list(_MOCK_FAT_EMPRESAS)

    def get_fe(f_est=None, f_proj=None):
        if not SUPABASE_OK: return _get_fat_empresas(f_est, f_proj)
        return _get_fat_empresas(f_est, f_proj)

    # ---- MÉTRICAS ----
    todos = get_fe()
    n_pf  = len([x for x in todos if x["estado"]=="por_faturar"])
    n_fi  = len([x for x in todos if x["estado"]=="fatura_emitida"])
    n_pg  = len([x for x in todos if x["estado"]=="pago"])
    t_pf  = sum(x.get("valor_30pct") or 0 for x in todos if x["estado"]=="por_faturar")
    t_fi  = sum(x.get("valor_30pct") or 0 for x in todos if x["estado"]=="fatura_emitida")
    t_pg  = sum(x.get("valor_recebido") or x.get("valor_30pct") or 0 for x in todos if x["estado"]=="pago")

    st.html(
        '<div class="fin-kpi-row">'
        + kpi_h("📋 Por faturar",    eur(t_pf), f"{n_pf} ações", "a")
        + kpi_h("📄 Fatura emitida", eur(t_fi), f"{n_fi} ações", "b")
        + kpi_h("✅ Pago",           eur(t_pg), f"{n_pg} ações", "g")
        + kpi_h("💰 Total a receber", eur(t_pf+t_fi), f"{n_pf+n_fi} por cobrar", "r")
        + '</div>'
    )

    st.html(div())

    # ---- FILTROS ----
    col_f, col_e, col_p = st.columns([2, 2, 2])
    with col_f:
        filtro_est  = st.selectbox("Estado", ["Todos","Por faturar","Fatura emitida","Pago"],
                                   key="fe_est",
                                   format_func=lambda x: {"Todos":"Todos","Por faturar":"📋 Por faturar",
                                                           "Fatura emitida":"📄 Fatura emitida","Pago":"✅ Pago"}.get(x,x))
    with col_e:
        filtro_proj = st.selectbox("Projeto", ["Todos","MENTORES","ANIET","APCMC","APIMA","PRODUTECH","CALÇADO"], key="fe_proj")
    with col_p:
        pesquisa    = st.text_input("Pesquisar empresa / código", key="fe_pesq", placeholder="Ex: Fenabel, LIKE GARDEN...")

    est_map = {"Por faturar":"por_faturar","Fatura emitida":"fatura_emitida","Pago":"pago","Todos":"Todos"}
    fat_list = get_fe(est_map.get(filtro_est,"Todos"), filtro_proj)

    if pesquisa:
        p = pesquisa.lower()
        fat_list = [x for x in fat_list if p in (x.get("empresa") or "").lower() or p in (x.get("codigo") or "").lower()]

    st.html(div())

    # ---- NOVA FATURAÇÃO ----
    with st.expander("➕ Registar nova faturação de empresa", expanded=False):
        acoes_disp = _get_acoes_faturar()
        if not acoes_disp:
            st.info("Nenhuma ação fechada disponível para faturar.")
        else:
            st.markdown("**Seleciona a ação e preenche os dados:**")
            opcoes_acao = {f"{a.get('codigo') or a.get('magna_id')} — {a.get('empresa_cliente') or '—'}": a for a in acoes_disp}
            sel = st.selectbox("Ação", list(opcoes_acao.keys()), key="fe_acao_sel")
            acao = opcoes_acao[sel]

            col1, col2, col3 = st.columns(3)
            with col1:
                dim = st.selectbox("Dimensão da empresa", DIMENSOES, key="fe_dim",
                                   index=DIMENSOES.index(acao.get("dimensao","Pequena")) if acao.get("dimensao") in DIMENSOES else 1)
                nif = st.text_input("NIF da empresa", value=acao.get("nif_empresa") or "", key="fe_nif")
            with col2:
                ch         = st.number_input("Carga horária", min_value=0, value=int(acao.get("volume_horas") or 0), key="fe_ch")
                form_cert  = st.number_input("Formandos certificados", min_value=0, value=int(acao.get("formandos_certificados") or 0), key="fe_fc")
            with col3:
                form_desf     = st.number_input("Formandos desfavorecidos", min_value=0, value=int(acao.get("formandos_desf") or 0), key="fe_fd",
                                                 disabled=(dim != "Média"), help="Só para empresas Média")
                form_nao_desf = st.number_input("Formandos não desf.", min_value=0, value=int(acao.get("formandos_nao_desf") or 0), key="fe_fnd",
                                                 disabled=(dim != "Média"), help="Só para empresas Média")

            volume = ch * form_cert
            valor  = calcular_30pct(dim, volume, form_desf, form_nao_desf)

            st.markdown(
                f"**Volume:** {volume} horas · **Valor 30% a faturar:** <span style='font-size:18px;font-weight:700;color:#1A1F2E'>{eur(valor)}</span>",
                unsafe_allow_html=True
            )

            notas = st.text_area("Notas", key="fe_notas", placeholder="Observações opcionais...", height=70)

            if st.button("💾 Registar faturação", key="fe_save", type="primary"):
                proj = next((p["nome"] for p in [{"nome":"MENTORES","code":"01195000"},{"nome":"ANIET","code":"01196000"},
                              {"nome":"APCMC","code":"01195400"},{"nome":"APIMA","code":"01194800"},
                              {"nome":"PRODUTECH","code":"02982000"},{"nome":"CALÇADO","code":"02981900"}]
                              if p["code"] in (acao.get("magna_id") or "")), "—")
                dados = {
                    "acao_id":         acao["id"],
                    "empresa":         acao.get("empresa_cliente") or "—",
                    "nif_empresa":     nif,
                    "dimensao":        dim,
                    "volume":          float(volume),
                    "formandos_desf":  form_desf,
                    "formandos_nao_desf": form_nao_desf,
                    "valor_30pct":     valor,
                    "estado":          "por_faturar",
                    "notas":           notas,
                    "projeto":         proj,
                    "codigo":          acao.get("codigo") or acao.get("magna_id") or "—",
                }
                if _criar_fat_empresa(dados):
                    st.toast(f"Faturação registada para {acao.get('empresa_cliente')}!")
                    st.rerun()

    st.html(div())

    # ---- LISTA DE FATURAÇÕES ----
    st.markdown(sec(f"Faturações ({len(fat_list)})", "Clica numa linha para atualizar o estado."), unsafe_allow_html=True)

    if not fat_list:
        st.html('<div class="fin-empty">Nenhuma faturação encontrada para este filtro.</div>')
    else:
        for row in fat_list:
            fe_id   = row.get("id") or "—"
            empresa = row.get("empresa") or "—"
            codigo  = row.get("codigo") or (row.get("acoes") or {}).get("codigo") or "—"
            proj    = row.get("projeto") or "—"
            dim     = row.get("dimensao") or "—"
            valor   = row.get("valor_30pct") or 0
            estado  = row.get("estado") or "por_faturar"
            n_fat   = row.get("numero_fatura") or "—"
            d_fat   = str(row.get("data_fatura") or "—")[:10]
            d_pag   = str(row.get("data_pagamento") or "—")[:10]
            val_rec = row.get("valor_recebido")

            with st.container(border=True):
                col_info, col_val, col_acao = st.columns([5, 2, 3])

                with col_info:
                    st.markdown(
                        f'<div style="padding:4px 0">'
                        f'<div style="font-weight:700;font-size:14px">{empresa}</div>'
                        f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">'
                        f'{ptag(proj)}&nbsp;·&nbsp;{codigo}&nbsp;·&nbsp;{dim}'
                        f'</div>'
                        f'{"<div style=\\'font-size:12px;color:#8B94A3\\'>Fatura: " + n_fat + " · " + d_fat + "</div>" if n_fat != "—" else ""}'
                        f'{"<div style=\\'font-size:12px;color:#16A34A\\'>Pago em: " + d_pag + " · " + eur(val_rec) + "</div>" if d_pag != "—" else ""}'
                        f'</div>', unsafe_allow_html=True
                    )

                with col_val:
                    st.markdown(
                        f'<div style="text-align:right;padding-top:6px">'
                        f'<div style="font-weight:700;font-size:16px">{eur(valor)}</div>'
                        f'{bdg_estado(estado)}'
                        f'</div>', unsafe_allow_html=True
                    )

                with col_acao:
                    if estado == "por_faturar":
                        n_fat_inp = st.text_input("Nº Fatura emitida", key=f"nf_{fe_id}", placeholder="FT2026/E...")
                        d_fat_inp = st.date_input("Data fatura", key=f"df_{fe_id}", value=None, format="DD/MM/YYYY")
                        if st.button("📄 Marcar fatura emitida", key=f"fi_{fe_id}", use_container_width=True):
                            if n_fat_inp:
                                upd = {"estado":"fatura_emitida","numero_fatura":n_fat_inp,
                                       "data_fatura":str(d_fat_inp) if d_fat_inp else None}
                                if _atualizar_fat_empresa(fe_id, upd):
                                    st.toast(f"Fatura registada para {empresa}!"); st.rerun()
                            else: st.warning("Introduz o número da fatura.")

                    elif estado == "fatura_emitida":
                        d_pag_inp  = st.date_input("Data pagamento", key=f"dp_{fe_id}", value=None, format="DD/MM/YYYY")
                        val_rec_inp = st.number_input("Valor recebido (€)", key=f"vr_{fe_id}", min_value=0.0,
                                                       value=float(valor), step=0.01, format="%.2f")
                        if st.button("✅ Marcar como pago", key=f"pg_{fe_id}", use_container_width=True):
                            upd = {"estado":"pago","data_pagamento":str(d_pag_inp) if d_pag_inp else None,
                                   "valor_recebido":float(val_rec_inp)}
                            if _atualizar_fat_empresa(fe_id, upd):
                                st.toast(f"Pagamento registado para {empresa}!"); st.rerun()

                    elif estado == "pago":
                        st.markdown("<div style='padding-top:12px;text-align:center;font-size:13px;color:#16A34A'>✅ Liquidado</div>", unsafe_allow_html=True)

    st.html(div())

    # ---- EXPORT ----
    if fat_list:
        rows = [{
            "Empresa":          x.get("empresa") or "—",
            "Código":           x.get("codigo") or "—",
            "Projeto":          x.get("projeto") or "—",
            "Dimensão":         x.get("dimensao") or "—",
            "Volume":           x.get("volume") or 0,
            "Valor 30% (€)":    x.get("valor_30pct") or 0,
            "Estado":           x.get("estado") or "—",
            "Nº Fatura":        x.get("numero_fatura") or "—",
            "Data Fatura":      str(x.get("data_fatura") or "—")[:10],
            "Data Pagamento":   str(x.get("data_pagamento") or "—")[:10],
            "Valor Recebido":   x.get("valor_recebido") or "",
        } for x in fat_list]
        buf = io.BytesIO()
        pd.DataFrame(rows).to_excel(buf, index=False, engine="openpyxl")
        st.download_button("⬇️ Exportar Excel", buf.getvalue(),
                           "faturacao_empresas.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
