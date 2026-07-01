# Grimmorium Backend API (v2)

API REST em Python + Flask para o projeto Grimmorium com suporte a:

- fluxo wizard de criação de personagem,
- hub do jogador (play mode),
- sistema de economia, inventário e ledger,
- compatibilidade com endpoints legados do 1o MVP.

## Estrutura

```text
grimmorium-react-backend/
├── app/
│   ├── __init__.py
│   ├── api_routes.py
│   ├── models.py
│   ├── schemas.py
│   ├── api.py
│   └── routes.py
├── instance/
├── main.py
└── requirements.txt
```

## Execução

Pré-requisitos:

- Python 3.10+
- pip

Instalar dependências:

```bash
pip install -r requirements.txt
```

Executar:

```bash
py -3 main.py
```

Servidor local:

- http://127.0.0.1:5000

Swagger/OpenAPI:

- UI: http://127.0.0.1:5000/openapi/swagger
- JSON: http://127.0.0.1:5000/openapi/openapi.json

## Banco de dados

- SQLite: `instance/grimmorium.db`
- Legacy mantido: tabela `personagens`
- V2 principal:
  - `characters`
  - `character_abilities`
  - `character_spell_slots`
  - `inventory_items`
  - `shop_items`
  - `ledger_entries`

## Endpoints principais

Health:

- `GET /api/hello`

Legacy (compatibilidade):

- `GET /api/personagens`
- `POST /api/personagens`

Characters v2:

- `GET /api/v2/characters`
- `GET /api/v2/characters/{id}`
- `POST /api/v2/characters/wizard`
- `PUT /api/v2/characters/{id}/play`
- `PUT /api/v2/characters/{id}/spell-slots/{slot_level}`
- `POST /api/v2/characters/{id}/rest/short`
- `POST /api/v2/characters/{id}/rest/long`
- `PUT /api/v2/characters/{id}/inventory/{item_id}/equip`
- `PUT /api/v2/characters/{id}/inventory/{item_id}/attune`

Shop e economia v2:

- `GET /api/v2/shop/items`
- `POST /api/v2/shop/items`
- `POST /api/v2/characters/{id}/shop/purchase`
- `POST /api/v2/characters/{id}/ledger/reward`
- `GET /api/v2/characters/{id}/ledger`

## Observações de arquitetura

- Optimistic UI e autosave com debounce devem ser feitos no frontend.
- O backend já está preparado para operações de economia em transação única.
- O campo de attunement limita itens sintonizados por personagem.
- AC é recalculada com base no equipamento marcado como em uso.

## Próximos passos

- Integrar o frontend React aos endpoints `/api/v2/...`.
- Adicionar autenticação quando houver multiusuário.
- Evoluir seed de `shop_items` para catálogo inicial do mestre.
