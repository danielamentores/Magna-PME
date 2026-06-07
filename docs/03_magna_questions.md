# Guia 3 — Integração com a Magna

A integração com a Magna tem **duas fases**:

1. **Agora (Excel):** exportas dados da Magna para Excel, e a app lê de lá
2. **Futuro (API):** a app fala diretamente com a API da Magna

A app já está preparada para ambos os modos via `MAGNA_MODE` no `.env`.

---

## 📊 Fase 1 — Modo Excel

### Como usar

1. Exporta as ações da Magna para Excel
2. Guarda em `data/magna_export.xlsx`
3. No `.env`: `MAGNA_MODE=excel`

### Colunas que a app procura (case-insensitive)

| Coluna | Aceita também | Obrigatório |
|---|---|---|
| ID | "Id Acao", "Codigo Magna" | ✅ |
| Nome | "Acao", "Designacao" | ✅ |
| Estado | "Situacao" | ✅ |
| Codigo | "Cod" | Não |
| Empresa | "Cliente" | Não |
| Email Formador | — | Não |
| Email Coordenador | — | Não |
| Data Inicio, Data Fim | "Inicio", "Fim" | Não |
| Volume | "Horas" | Não |
| Inscritos | "Formandos Inscritos" | Não |
| Certificados | "Formandos Certificados" | Não |
| Valor Formador, Consultor, Empresa | — | Não |

### Estados aceites

- `planeada`, `planeado`
- `a decorrer`, `em curso`
- `terminada`, `terminado`
- `fechada`, `fechado`, `encerrada`

Se os nomes das colunas no teu Excel forem diferentes, ajusta o mapeamento em
`integrations/magna.py` (variável `COLUNAS_EXCEL`).

---

## 🔌 Fase 2 — Modo API (futuro)

Quando a API da Magna estiver acessível, basta:

1. Implementar a classe `MagnaApiAdapter` em `integrations/magna.py`
2. `.env`: `MAGNA_MODE=api` + `MAGNA_API_URL` + `MAGNA_API_KEY`
3. **Nada mais muda** no resto da app ✨

### Endpoint conhecido

- `POST magna.comenius.pt/api/admins/login` → autenticação JWT
- `GET magna.comenius.pt/api/{adminId}/filteredData` → lista de cursos paginada
