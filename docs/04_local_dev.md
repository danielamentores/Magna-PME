# Guia 4 — Correr a app localmente (Windows)

Tempo estimado: **5 minutos**.

## Pré-requisitos

- Python 3.12+ ✅
- Git ✅
- VS Code ✅
- Guias 1 e 2 concluídos (com `.env` preenchido)

---

## Passo 1 — Abrir o projeto no VS Code

```powershell
cd C:\Projetos\gestform
code .
```

(O `code .` abre o VS Code nesta pasta.)

## Passo 2 — Criar ambiente virtual Python

No terminal do VS Code:

```powershell
python -m venv venv
```

## Passo 3 — Ativar o venv

```powershell
venv\Scripts\activate
```

Deves ver `(venv)` no início da linha.

⚠️ **Se der erro de "execution policy"** corre primeiro:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

E confirma com `Y`.

## Passo 4 — Instalar dependências

```powershell
pip install -r requirements.txt
```

(Demora 1-2 minutos.)

## Passo 5 — Configurar `.env`

```powershell
copy .env.example .env
```

Abre o `.env` no VS Code e preenche pelo menos:
- `GEMINI_API_KEY` (do guia 1)
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` (do guia 2)

## Passo 6 — Correr a app

```powershell
streamlit run app/main.py
```

Abre automaticamente em http://localhost:8501

---

## O que podes testar nesta versão

✅ Login simulado (4 perfis)
✅ Leitura de fatura PDF com IA (Gemini)
✅ Listar ações da Magna (se colocaste Excel em `data/magna_export.xlsx`)

🚧 Ainda não funcional:
- Login OAuth Google
- Gravação na BD
- Envio de emails
- Sincronização automática

---

## ❓ Problemas comuns

**`ModuleNotFoundError`** → Não estás no venv. Corre `venv\Scripts\activate`.

**`Configuracao em falta: GEMINI_API_KEY`** → `.env` não preenchido ou na pasta errada.

**`400 API key not valid`** → Chave Gemini errada ou não ativada para este projeto.

**Port 8501 em uso** → `streamlit run app/main.py --server.port 8502`
