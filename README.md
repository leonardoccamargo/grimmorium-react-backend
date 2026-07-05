# Grimmorium Backend API

API Flask/OpenAPI para gerenciamento de personagens, magias e economia do MVP.

## Objetivo deste guia

Este README foi escrito para quem nao tem experiencia tecnica.
Siga os passos na ordem, sem pular.

## Pre-requisitos

1. Windows com PowerShell
2. Python 3.10 ou superior instalado

Para conferir se o Python esta instalado, rode:

```powershell
python --version
```

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

4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

5. Iniciar backend

```powershell
python main.py
```

## Como testar se esta funcionando

Com o servidor ligado, abra no navegador:

1. API raiz: http://127.0.0.1:5000/
2. Health check: http://127.0.0.1:5000/api/hello
3. Swagger (tela para testar endpoints): http://127.0.0.1:5000/openapi/swagger

## Como parar o backend

No terminal onde a API esta rodando, pressione `Ctrl + C`.

## Se der erro comum

1. "python nao reconhecido"

- Reinstale o Python e marque a opcao Add Python to PATH.

2. "execucao de scripts desabilitada"

- Rode este comando e depois tente ativar de novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

3. Porta 5000 ocupada

- Feche outro processo que esteja usando a porta ou rode novamente apos reiniciar o terminal.

## Variaveis de ambiente

Atualmente este backend nao precisa de arquivo .env para rodar localmente.

- Banco padrao: SQLite local em `instance/grimmorium.db`
- Porta padrao: `5000`

## Endpoints principais

### Health

- GET /
- GET /api/hello

### Magias e sincronizacao

- GET /api/magias
- POST /api/sync/import-local-json
- POST /api/sync/export-local-json

### Personagens (legado MVP 1)

- GET /api/personagens
- POST /api/personagens

### Personagens (V2)

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

## Banco e sincronizacao de dados

1. O backend usa SQLite local.
2. O backend e a fonte principal dos dados.
3. Se o banco estiver vazio ao iniciar, ele importa dados de:

- grimmorium-react-main/public/personagens.json
- grimmorium-react-main/public/magias.json

4. Em alteracoes bem-sucedidas (POST, PUT, PATCH, DELETE), o backend exporta dados para os JSONs do frontend.

## Creditos

- D&D 5e API: https://dnd5eapi.co
