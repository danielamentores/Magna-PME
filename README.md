# Magna-PME

APP para gestão administrativa e financeira de ações de formação.

Substitui o fluxo atual de Excel + Forms + Drive por uma aplicação centralizada
que se integra com a Magna (plataforma de gestão de formação).

## 🎯 O que faz

- **Formadores** submetem faturas → app lê e valida contra a Magna
- **Coordenadores** veem o estado das suas ações e formadores .
- **Gestor de projeto** seleciona ações para faturação/reembolso
- **Financeiro** aprova pagamentos e regista comprovativos
- **alertas de faturas** envia alertas automáticos (10 dias, 30 dias) e marca eventos no calendário e na Formação-Ação quando a execução está a 80 % será faturado os 10 % á empresa.

## 🏗️ Stack técnica

| Componente | Tecnologia |
|---|---|
| Interface | Streamlit |
| Base de dados | Supabase (PostgreSQL) |
| Autenticação | Google OAuth 2.0 |
| ler faturas com código python |
| Email | Gmail API |
| Calendário | Google Calendar API |
| Armazenamento | Google Drive API |
| Magna | Adaptador (API ou Excel) |

## 📂 Estrutura

```
gestform/
├── app/                  # UI Streamlit
│   ├── main.py           # Entrypoint
│   └── pages/            # Páginas por perfil
├── core/
│   ├── models.py         # Modelos de dados
│   ├── auth.py           # OAuth Google
│   ├── permissions.py    # Quem vê o quê
│   └── config.py         # Configuração
├── integrations/
│   ├── gmail.py          # Enviar/receber emails
│   ├── calendar.py       # Alertas no calendário
│   ├── drive.py          # Arquivo de ficheiros
│   └── magna.py          # Adaptador Magna (API ou Excel)
├── agent/
│   ├── invoice_flow.py   # Fluxo de faturas (formadores)
│   ├── action_flow.py    # Fluxo de ações fechadas (consultores)
│   └── refund_flow.py    # Fluxo de reembolsos
├── db/
│   ├── schema.sql        # Schema do PostgreSQL
│   └── supabase_client.py
├── docs/                 # Guias passo a passo
├── scripts/              # Setup e seeds
└── data/sample/          # Dados de exemplo
```

## 🚀 Setup inicial


1. [`docs/01_google_cloud_setup.md`](docs/01_google_cloud_setup.md) — Criar projeto + APIs + OAuth
2. [`docs/02_supabase_setup.md`](docs/02_supabase_setup.md) — Criar BD e tabelas
3. [`docs/03_magna_questions.md`](docs/03_magna_questions.md) — Integração com a Magna
4. [`docs/04_local_dev.md`](docs/04_local_dev.md) — Correr a app localmente

## 📋 Estado do projeto

- [x] Estrutura do projeto
- [x] Schema da BD
- [x] Modelos de dados
- [x] Módulo de leitura de faturas com Gemini
- [x] Adaptador Magna (Excel)
- [x] App Streamlit + login simulado
- [ ] Integração Supabase
- [ ] OAuth Google
- [ ] Gmail API
- [ ] Calendar API
- [ ] Adaptador Magna (API)
- [ ] Deploy

## 📜 Licença

Privado — uso interno.
