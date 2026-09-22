# Grimmorium Backend

API e banco de dados do Grimmorium. O backend guarda as fichas, atualiza os dados da sessao e fornece as informacoes usadas pelo frontend.

## Recomendado: executar o site completo

Para rodar frontend e backend juntos, mantenha os dois repositorios na mesma pasta:

```text
Grimmorium/
├── grimmorium-react/
└── grimmorium-react-backend/
```

Abra o PowerShell na pasta `grimmorium-react` e execute:

```powershell
docker compose up --build
```

Depois, abra:

- Site: [http://localhost:8080](http://localhost:8080)
- API: [http://localhost:5000](http://localhost:5000)
- Documentacao da API: [http://localhost:5000/openapi/swagger](http://localhost:5000/openapi/swagger)

Para encerrar os containers:

```powershell
docker compose down
```

## Executar apenas o backend

Use esta opcao somente se o frontend ja estiver rodando separadamente.

Na pasta deste repositorio:

```powershell
docker build -t grimmorium-backend .
docker run --rm -p 5000:5000 grimmorium-backend
```

## Executar sem Docker

Pre-requisito: Python 3.10 ou superior.

No PowerShell, dentro da pasta do backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

API local: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## O que a API faz

### Personagens

- `GET /api/v2/characters`: lista personagens.
- `GET /api/v2/characters/<id>`: consulta uma ficha.
- `POST /api/v2/characters/wizard`: cria uma ficha.
- `POST /api/v2/characters/sheet`: edita uma ficha.
- `DELETE /api/v2/characters/<id>`: remove uma ficha.

### Sessao de jogo

- `PUT /api/v2/characters/<id>/play`: atualiza HP, CA, velocidade e dados de vida.
- `PUT /api/v2/characters/<id>/spell-slots/<slot_level>`: atualiza slots usados.
- `POST /api/v2/characters/<id>/rest/short`: aplica descanso curto.
- `POST /api/v2/characters/<id>/rest/long`: aplica descanso longo.
- `GET /api/v2/characters/<id>/history`: lista as ultimas 9 alteracoes da ficha.

Alteracoes feitas no modo **Jogar** entram no historico. A edicao completa da ficha nao entra. Quando o limite e ultrapassado, o registro mais antigo e removido.

### Inventario e economia

- Equipar e ajustar itens do inventario.
- Comprar itens da loja.
- Registrar recompensas e consultar o ledger.

### Magias

- `GET /api/magias`: disponibiliza as magias usadas pelo frontend.
- `POST /api/sync/import-local-json`: importa dados locais.
- `POST /api/sync/export-local-json`: exporta dados para o frontend.

## Banco de dados

Os dados sao salvos em SQLite. No Docker Compose, o banco fica em um volume persistente e continua disponivel apos reiniciar os containers.

Quando o banco esta vazio, o sistema carrega os dados iniciais dos arquivos locais de personagens e magias.

## API externa

O frontend tambem consulta a [D&D 5e API](https://www.dnd5eapi.co) para pesquisar magias. Ela e publica, gratuita e nao exige cadastro ou chave.