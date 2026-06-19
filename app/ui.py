"""Componentes visuais partilhados — design system Magna PME."""
from __future__ import annotations

CORES = {
    "MENTORES":  "#2563EB", "ANIET":     "#16A34A",
    "APCMC":     "#D97706", "APIMA":     "#9D174D",
    "PRODUTECH": "#7C3AED", "CALÇADO":   "#0F766E",
}
BGS = {
    "MENTORES":  "#EEF3FD", "ANIET":     "#F0FDF4",
    "APCMC":     "#FFFBEB", "APIMA":     "#FDF2F8",
    "PRODUTECH": "#F5F3FF", "CALÇADO":   "#F0FDFA",
}

CSS = """
<style>
.mt-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px}
.mt-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:120px}
.mt-kpi.r{border-top:3px solid #DC2626}.mt-kpi.a{border-top:3px solid #D97706}
.mt-kpi.b{border-top:3px solid #2563EB}.mt-kpi.g{border-top:3px solid #16A34A}
.mt-kpi.p{border-top:3px solid #7C3AED}
.mt-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 4px}
.mt-kpi .val{font-size:22px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.mt-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}
.mt-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:12px 14px;margin-bottom:8px}
.mt-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.mt-ptag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}
.mt-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.mt-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.mt-div{height:1px;background:#E4E7EF;margin:20px 0 18px}
.mt-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px}
.mt-warn{background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;border-radius:8px;padding:9px 14px;font-size:13px;color:#92400E;margin-bottom:12px}
.mt-ok{background:#F0FDF4;border:1px solid #BBF7D0;border-left:3px solid #16A34A;border-radius:8px;padding:9px 14px;font-size:13px;color:#166534;margin-bottom:12px}
</style>
"""

def eur(v: float | None) -> str:
    try: return f"€\u202f{float(v):,.0f}".replace(",", ".")
    except: return "€ —"

def eur2(v: float | None) -> str:
    """Com decimais."""
    try: return f"€\u202f{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "€ —"

def ptag(p: str) -> str:
    c = CORES.get(p, "#6B7280"); b = BGS.get(p, "#F3F4F6")
    return f'<span class="mt-ptag" style="background:{b};color:{c}">{p}</span>'

def badge(estado: str) -> str:
    M = {
        "submetida":           ("#FFFBEB","#D97706","Submetida"),
        "leitura_falhada":     ("#FEF2F2","#DC2626","Leitura falhada"),
        "acao_nao_fechada":    ("#FEF2F2","#DC2626","Ação não fechada"),
        "aprovada":            ("#F0FDF4","#16A34A","Aprovada"),
        "paga":                ("#F0FDF4","#16A34A","Paga"),
        "rejeitada":           ("#F3F4F6","#6B7280","Rejeitada"),
        "por_faturar":         ("#F3F4F6","#6B7280","Por faturar"),
        "fatura_emitida":      ("#EEF3FD","#2563EB","Fatura emitida"),
        "aguarda_fatura":      ("#FFFBEB","#D97706","Aguarda fatura"),
        "nh_paga":             ("#F0FDF4","#16A34A","NH Paga"),
        "nh_pendente":         ("#FFFBEB","#D97706","NH Pendente"),
        "sem_fatura":          ("#F3F4F6","#6B7280","Sem fatura"),
        "fechada":             ("#F0FDF4","#16A34A","✅ Fechada"),
        "a_decorrer":          ("#EEF3FD","#2563EB","🔵 A decorrer"),
        "planeada":            ("#F5F3FF","#7C3AED","📋 Planeada"),
        "terminada_sem_fecho": ("#FFFBEB","#D97706","⚠️ Por fechar"),
    }
    bg, c, l = M.get(estado, ("#F3F4F6","#6B7280", estado))
    return f'<span class="mt-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi(lbl: str, val: str, sub: str, cor: str = "") -> str:
    cls = f"mt-kpi {cor}" if cor else "mt-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def kpi_row(*items: str) -> str:
    return f'<div class="mt-kpi-row">{"".join(items)}</div>'

def sec(titulo: str, sub: str = "") -> str:
    s = f'<p class="mt-secs">{sub}</p>' if sub else ""
    return f'<p class="mt-sec">{titulo}</p>{s}'

def div() -> str:
    return '<div class="mt-div"></div>'

def empty(msg: str = "Sem dados.") -> str:
    return f'<div class="mt-empty">{msg}</div>'

def warn(msg: str) -> str:
    return f'<div class="mt-warn">{msg}</div>'

def ok(msg: str) -> str:
    return f'<div class="mt-ok">{msg}</div>'

def card(conteudo: str, cor_esq: str = "") -> str:
    estilo = f"border-left:3px solid {cor_esq}" if cor_esq else ""
    return f'<div class="mt-card" style="{estilo}">{conteudo}</div>'
