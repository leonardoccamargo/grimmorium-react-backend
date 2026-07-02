# Grimmorium Backend API

API Flask para personagens, grimorio, economia e sincronizacao com JSON local.

## Requisitos

- Python 3.10+
- pip
- venv recomendado na raiz do projeto: `.venv`

## Instalação

No terminal (a partir da raiz do projeto):

```bash
cd grimmorium-react-backend
pip install -r requirements.txt
```

## Execução (Windows/PowerShell)

Comandos:

```powershell
& ".\.venv\Scripts\python.exe" .\grimmorium-react-backend\main.py
```

Esse procedimento evita dependencias do Python global e reduz falhas de ambiente.

Servidor: http://127.0.0.1:5000

Teste rapido de funcionamento:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/hello | Select-Object -ExpandProperty Content
```

## Swagger / OpenAPI

- UI: http://127.0.0.1:5000/openapi/swagger
- JSON: http://127.0.0.1:5000/openapi/openapi.json

## Endpoints essenciais

- GET /
- GET /api/hello
- GET /api/v2/characters
- POST /api/v2/characters/wizard
- GET /api/magias
- POST /api/sync/import-local-json
- POST /api/sync/export-local-json

## Banco e sincronizacao

- SQLite em `instance/grimmorium.db`
- Seed inicial: importa `grimmorium-react-main/public/personagens.json` e `grimmorium-react-main/public/magias.json` quando o banco estiver vazio
- Backend e a fonte principal dos dados
- Apos mutacoes via API (POST/PUT/PATCH/DELETE), os JSON locais sao atualizados automaticamente

## Apoio ao MVP

Este backend sustenta o fluxo do MVP com:

- criacao guiada de personagem (wizard)
- play mode com atualizacao de ficha
- consulta de magias
- validacao de pontas via Swagger
