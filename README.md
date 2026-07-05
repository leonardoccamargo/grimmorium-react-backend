# Grimmorium Backend API

API Flask/OpenAPI para gerenciamento de personagens, magias e economia do MVP.

## Pre-requisitos

1. Windows com PowerShell
2. Python 3.10+ instalado (https://www.python.org)

## Passo a passo

1. Criar ambiente virtual

```powershell
python -m venv .venv
```

2. Ativar ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Entrar na pasta do backend

```powershell
cd .\grimmorium-react-backend
```

4. Instalar dependências

```powershell
pip install -r requirements.txt
```

5. Iniciar backend

```powershell
python main.py
```

## Como testar se está funcionando

Com o servidor ligado, abra no navegador:

1. API raiz: http://127.0.0.1:5000/
2. Health check: http://127.0.0.1:5000/api/hello
3. Swagger (tela para testar endpoints): http://127.0.0.1:5000/openapi/swagger

## Como parar o backend

No terminal onde a API está rodando, pressione `Ctrl + C`.

## Endpoints principais

### Health

- GET /
- GET /api/hello

### Magias e sincronização

- GET /api/magias
- POST /api/sync/import-local-json
- POST /api/sync/export-local-json

### Personagens

- GET /api/v2/characters
- GET /api/v2/characters/<id>
- DELETE /api/v2/characters/<id>
- POST /api/v2/characters/wizard
- PUT /api/v2/characters/<id>/play
- PUT /api/v2/characters/<id>/spell-slots/<slot_level>
- POST /api/v2/characters/<id>/rest/short
- POST /api/v2/characters/<id>/rest/long
- PUT /api/v2/characters/<id>/inventory/<item_id>/equip
- PUT /api/v2/characters/<id>/inventory/<item_id>/attune
- POST /api/v2/characters/<id>/shop/purchase
- POST /api/v2/characters/<id>/ledger/reward
- GET /api/v2/characters/<id>/ledger

## Banco e sincronização de dados

1. O backend usa SQLite local.
2. O backend é a fonte principal dos dados.
3. Ao iniciar, se o banco SQLite estiver vazio, o backend importa dados iniciais de personagens.json e magias.json.
4. Em operações de escrita bem-sucedidas na API (POST, PUT, PATCH, DELETE), o backend primeiro atualiza o SQLite e depois exporta os dados para os JSONs do frontend, mantendo personagens.json e magias.json sincronizados.

## Créditos

- D&D 5e API: https://dnd5eapi.co
