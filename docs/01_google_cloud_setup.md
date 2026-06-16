# Guia 1 — Setup do Google Cloud

Tempo estimado: **20 minutos**.

## O que vais obter

- ✅ Projeto Google Cloud criado
- ✅ APIs ativadas: Gemini, Gmail, Drive, Calendar, OAuth
- ✅ Credenciais OAuth (Client ID + Secret) para login
- ✅ Chave Gemini para ler faturas

---

## Parte 1 — Criar o projeto (3 min)

1. Vai a https://console.cloud.google.com
2. Topo: clica no **seletor de projeto**
3. Clica **"Novo projeto"**
4. Nome: `Magna-PME`
5. **"Criar"** → aguarda 30s → **seleciona o projeto**

## Parte 2 — Ativar APIs (5 min)

Para cada API: **APIs e serviços → Biblioteca** → procura nome → **Ativar**

- **Generative Language API** (Gemini)
- **Gmail API**
- **Google Drive API**
- **Google Calendar API**
- **Google Sheets API**

## Parte 3 — Ecrã de consentimento OAuth (5 min)

1. **APIs e serviços → Ecrã de consentimento OAuth**
2. Tipo: **Interno** (se tens Workspace) ou **Externo**
3. **"Criar"** → preenche:
   - Nome da app: `Magna-PME`
   - Email de suporte: o teu
   - Email do programador: o teu
4. **Âmbitos:** adiciona estes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `gmail.send`, `gmail.readonly`
   - `drive.file`, `calendar.events`
5. Se "Externo": adiciona o teu email em **Utilizadores de teste**

## Parte 4 — Credenciais OAuth (3 min)

1. **APIs e serviços → Credenciais**
2. **"Criar credenciais" → "ID de cliente OAuth"**
3. Tipo: **Aplicação Web**
4. Nome: `Gestform Web`
5. **URIs de redirecionamento autorizados:**
   - `http://localhost:8501/oauth/callback`
6. **"Criar"** → copia **Client ID** e **Client Secret**

## Parte 5 — Chave Gemini (2 min)

1. Vai a https://aistudio.google.com/apikey
2. **"Create API key"**
3. Seleciona o projeto `Magna-PME`
4. Copia a chave (`AIza...`)

## Parte 6 — Preencher `.env` (1 min)

```bash
cp .env.example .env
```

Edita `.env`:
```
GOOGLE_CLIENT_ID=<da Parte 4>
GOOGLE_CLIENT_SECRET=<da Parte 4>
GEMINI_API_KEY=<da Parte 5>
```

---

## ❓ Problemas comuns

**"Esta app não foi verificada"** → Normal em testing. Clica "Avançado" → "Ir para a app".

**Não vejo Generative Language API** → Procura "Gemini API" ou vai a https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
