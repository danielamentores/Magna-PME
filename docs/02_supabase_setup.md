# Guia 2 — Setup do Supabase

Tempo estimado: **10 minutos**.

## Parte 1 — Criar conta e projeto (5 min)

1. Vai a https://supabase.com
2. **"Start your project"** → cria conta (GitHub ou email)
3. **"New project"**
4. Preenche:
   - **Name:** `gestform`
   - **Database password:** gera forte (guarda num gestor de passwords!)
   - **Region:** `West EU (Ireland)`
   - **Pricing plan:** Free
5. **"Create new project"** → aguarda ~2 min

## Parte 2 — Aplicar o schema (3 min)

1. Painel do projeto → menu lateral → **"SQL Editor"**
2. **"+ New query"**
3. Abre `db/schema.sql` no teu computador
4. **Copia todo o conteúdo** → cola no editor SQL
5. **"Run"** (Ctrl+Enter)
6. Deve aparecer **"Success"** ✅

### Verifica

**Table Editor** → deves ver: `profiles`, `acoes`, `faturas`, `faturacao_consultores`, `reembolsos`, `email_log`, `agent_events`

## Parte 3 — Chaves (2 min)

1. **Project Settings → API**
2. Copia:
   - **Project URL** → `https://xxx.supabase.co`
   - **anon / public key**
   - **service_role key** (NUNCA exponhas no cliente!)

## Parte 4 — `.env`

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
```

## ❓ Problemas

**"Project paused"** → Projetos gratuitos pausam após 7 dias sem uso. Clica "Restore project".

**Esqueci password BD** → Settings → Database → "Reset database password".
