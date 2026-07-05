# Grimmorium Backend API

API Flask/OpenAPI para gerenciamento de personagens, grimorio de magias e economia do MVP.

## Pre-requisitos

- Python 3.10+
- pip

## Passo a Passo (Setup + Execucao)

Execute os comandos abaixo a partir da raiz do projeto:

1. Criar ambiente virtual na raiz do workspace (recomendado)

```powershell
python -m venv .venv
```

2. Ativar o ambiente virtual (Windows PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

3. Entrar na pasta do backend

```powershell
cd .\grimmorium-react-backend
```

4. Instalar dependencias

```powershell
pip install -r .\requirements.txt
```

5. Iniciar a API

```powershell
python .\main.py
```

6. Validar se subiu corretamente

- API: http://127.0.0.1:5000/
- Health check: http://127.0.0.1:5000/api/hello

## Variaveis de Ambiente

No estado atual do projeto, o backend nao exige arquivo `.env` para rodar localmente.

- Banco padrao: SQLite local (`sqlite:///grimmorium.db`)
- Porta padrao: `5000`

Se quiser evoluir para ambientes distintos (dev/homolog/prod), vale adicionar um `.env` proprio do backend depois.

## Documentacao da API (Swagger/OpenAPI)

Com o servidor rodando:

- Swagger UI: http://127.0.0.1:5000/openapi/swagger
- OpenAPI JSON: http://127.0.0.1:5000/openapi/openapi.json

## Endpoints Principais

### Health

- `GET /`
- `GET /api/hello`

### Magias e Sincronizacao

- `GET /api/magias`
- `POST /api/sync/import-local-json`
- `POST /api/sync/export-local-json`

### Legado (MVP 1)

- `GET /api/personagens`
- `POST /api/personagens`

### V2 (MVP atual)

- `GET /api/v2/characters`
- `GET /api/v2/characters/<id>`
- `DELETE /api/v2/characters/<id>`
- `POST /api/v2/characters/wizard`
- `PUT /api/v2/characters/<id>/play`
- `PUT /api/v2/characters/<id>/spell-slots/<slot_level>`
- `POST /api/v2/characters/<id>/rest/short`
- `POST /api/v2/characters/<id>/rest/long`
- `PUT /api/v2/characters/<id>/inventory/<item_id>/equip`
- `PUT /api/v2/characters/<id>/inventory/<item_id>/attune`
- `POST /api/v2/characters/<id>/shop/purchase`
- `POST /api/v2/characters/<id>/ledger/reward`
- `GET /api/v2/characters/<id>/ledger`

## Banco e Source of Truth

- Banco local em SQLite (arquivo `instance/grimmorium.db`)
- Backend e a fonte principal dos dados
- Ao iniciar, se o banco estiver vazio, a API faz seed a partir de:
	- `grimmorium-react-main/public/personagens.json`
	- `grimmorium-react-main/public/magias.json`
- Em mutacoes bem-sucedidas (`POST`, `PUT`, `PATCH`, `DELETE`), o backend exporta dados para os JSONs do frontend automaticamente

## Creditos

- D&D 5e API: https://dnd5eapi.co
