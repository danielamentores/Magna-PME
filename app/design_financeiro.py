"""
CSS e helpers de design partilhados entre todas as tabs do financeiro.
Coloca em app/design_financeiro.py
"""

DESIGN_CSS = """
<style>
:root {
  --c-ink:        #1A1F2E;
  --c-ink-soft:   #4B5263;
  --c-ink-muted:  #8B94A3;
  --c-bg:         #F7F8FC;
  --c-surface:    #FFFFFF;
  --c-border:     #E4E7EF;
  --c-blue:       #2563EB;
  --c-blue-soft:  #EEF3FD;
  --c-green:      #16A34A;
  --c-green-soft: #F0FDF4;
  --c-amber:      #D97706;
  --c-amber-soft: #FFFBEB;
  --c-red:        #DC2626;
  --c-red-soft:   #FEF2F2;
  --c-purple:     #7C3AED;
  --c-purple-soft:#F5F3FF;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}
.kpi-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px; }
.kpi { background:var(--c-surface); border:1px solid var(--c-border);
       border-radius:var(--radius-lg); padding:16px 20px; flex:1; min-width:140px; }
.kpi-label { font-size:11px; font-weight:600; color:var(--c-ink-muted);
             text-transform:uppercase; letter-spacing:.06em; margin:0 0 6px; }
.kpi-value { font-size:24px; font-weight:700; color:var(--c-ink); margin:0; line-height:1.1; }
.kpi-sub   { font-size:12px; color:var(--c-ink-muted); margin:4px 0 0; }
.kpi.kpi-red    { border-top:3px solid var(--c-red);    }
.kpi.kpi-amber  { border-top:3px solid var(--c-amber);  }
.kpi.kpi-blue   { border-top:3px solid var(--c-blue);   }
.kpi.kpi-green  { border-top:3px solid var(--c-green);  }
.kpi.kpi-purple { border-top:3px solid var(--c-purple); }

.fatura-card { background:var(--c-surface); border:1px solid var(--c-border);
               border-radius:var(--radius-lg); padding:14px 16px; margin-bottom:8px; }
.fatura-card.vencida  { border-left:3px solid var(--c-red);   background:var(--c-red-soft); }
.fatura-card.a-vencer { border-left:3px solid var(--c-amber); }
.fatura-title  { font-weight:600; font-size:14px; color:var(--c-ink); }
.fatura-meta   { font-size:12px; color:var(--c-ink-muted); margin-top:2px; }
.fatura-datas  { font-size:11px; color:var(--c-ink-muted); margin-top:3px; }
.fatura-valor  { font-weight:700; font-size:16px; color:var(--c-ink); }
.fatura-dias-r { font-size:12px; color:var(--c-red);   margin-top:2px; }
.fatura-dias-a { font-size:12px; color:var(--c-amber); margin-top:2px; }

.sec-title { font-size:14px; font-weight:700; color:var(--c-ink-soft);
             text-transform:uppercase; letter-spacing:.06em;
             margin:0 0 4px; display:flex; align-items:center; gap:8px; }
.sec-sub   { font-size:13px; color:var(--c-ink-muted); margin:0 0 14px; }
.sec-divider { height:1px; background:var(--c-border); margin:28px 0 20px; }

.badge { display:inline-block; font-size:11px; font-weight:600;
         padding:2px 9px; border-radius:20px; white-space:nowrap; }
.badge-submetida  { background:var(--c-amber-soft); color:var(--c-amber); }
.badge-aprovada   { background:var(--c-green-soft); color:var(--c-green); }
.badge-paga       { background:var(--c-blue-soft);  color:var(--c-blue);  }
.badge-vencida    { background:var(--c-red-soft);   color:var(--c-red);   }
.badge-rejeitada  { background:#F3F4F6; color:#6B7280; }

.empty-state { background:var(--c-bg); border:1px dashed var(--c-border);
               border-radius:var(--radius-lg); padding:24px 16px;
               text-align:center; color:var(--c-ink-muted); font-size:13px; }
.alert-warn { background:var(--c-amber-soft); border:1px solid #FCD34D;
              border-left:3px solid var(--c-amber);
              border-radius:var(--radius-md); padding:10px 16px;
              font-size:13px; color:#92400E; margin-bottom:16px; }
.aprov-card { background:var(--c-surface); border:1px solid var(--c-border);
              border-radius:var(--radius-lg); padding:16px; margin-bottom:10px; }
</style>
"""

CORES_PROJETO = {
    "MENTORES":  "#2563EB",
    "ANIET":     "#16A34A",
    "APCMC":     "#D97706",
    "APIMA":     "#9D174D",
    "PRODUTECH": "#7C3AED",
    "CALÇADO":   "#0F766E",
}
BG_PROJETO = {
    "MENTORES":  "#EEF3FD",
    "ANIET":     "#F0FDF4",
    "APCMC":     "#FFFBEB",
    "APIMA":     "#FDF2F8",
    "PRODUTECH": "#F5F3FF",
    "CALÇADO":   "#F0FDFA",
}

def proj_tag(projeto: str) -> str:
    cor = CORES_PROJETO.get(projeto, "#6B7280")
    bg  = BG_PROJETO.get(projeto, "#F3F4F6")
    return (f"<span style='background:{bg};color:{cor};font-size:11px;"
            f"font-weight:700;padding:2px 8px;border-radius:4px'>{projeto}</span>")

def badge(estado: str) -> str:
    m = {
        "submetida":        ("#FFFBEB","#D97706","Submetida"),
        "leitura_falhada":  ("#FEF2F2","#DC2626","Leitura falhada"),
        "acao_nao_fechada": ("#FEF2F2","#DC2626","Ação não fechada"),
        "aprovada":         ("#F0FDF4","#16A34A","Aprovada"),
        "paga":             ("#EEF3FD","#2563EB","Paga"),
        "rejeitada":        ("#F3F4F6","#6B7280","Rejeitada"),
        "Pendente":         ("#FFFBEB","#D97706","Pendente"),
        "Aprovado":         ("#F0FDF4","#16A34A","Aprovado"),
        "Pago":             ("#EEF3FD","#2563EB","Pago"),
        "aguarda_fatura":   ("#FFFBEB","#D97706","Aguarda fatura"),
        "aguarda_aprovacao":("#FFFBEB","#D97706","Aguarda aprovação"),
        "fatura_emitida":   ("#EEF3FD","#2563EB","Fatura emitida"),
        "confirmada":       ("#F0FDF4","#16A34A","Confirmada"),
    }
    bg, cor, label = m.get(estado, ("#F3F4F6","#6B7280", estado))
    return (f"<span style='background:{bg};color:{cor};font-size:11px;"
            f"font-weight:600;padding:2px 9px;border-radius:20px'>{label}</span>")

def fmt_eur(valor) -> str:
    try:
        return f"€\u202f{float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "€ —"

def kpi(label: str, valor: str, sub: str, variante: str = "") -> str:
    cls = f"kpi kpi-{variante}" if variante else "kpi"
    return (f"<div class='{cls}'>"
            f"<p class='kpi-label'>{label}</p>"
            f"<p class='kpi-value'>{valor}</p>"
            f"<p class='kpi-sub'>{sub}</p></div>")

def sec_header(titulo: str, subtitulo: str = "") -> str:
    sub = f'<p class="sec-sub">{subtitulo}</p>' if subtitulo else ""
    return f'<p class="sec-title">{titulo}</p>{sub}'
