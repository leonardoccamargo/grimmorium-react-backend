# 🔮 Grimmorium Backend API

Este repositório contém o **backend** responsável pela lógica de negócios, persistência e gerenciamento do sistema Grimmorium. Ele funciona de forma integrada ao [repositório frontend](https://github.com/leonardoccamargo/grimmorium-react), garantindo que os dados estejam sempre atualizados.

---

## 🛠️ Pré-requisitos

1. **Docker Desktop:** instalado e em execução ([instalação](https://docs.docker.com/desktop/install/windows-install/)).

---

## 🐳 Execução com Docker

Para executar apenas a API, na raiz deste repositório:

```powershell
docker build -t grimmorium-backend .
docker run --rm -p 5000:5000 grimmorium-backend
```

Use [http://localhost:5000](http://localhost:5000) para a API e [http://localhost:5000/openapi/swagger](http://localhost:5000/openapi/swagger) para o Swagger. Para iniciar API e interface juntas, use `docker compose up --build` no repositório principal [grimmorium-react](https://github.com/leonardoccamargo/grimmorium-react). O SQLite é mantido em um volume Docker entre reinicializações.

---

## 💻 Execução local (alternativa para desenvolvimento)

Para executar sem Docker, instale Python 3.10+ e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Valide em [http://127.0.0.1:5000/](http://127.0.0.1:5000/) e no [Swagger](http://127.0.0.1:5000/openapi/swagger). Para interromper, pressione `Ctrl + C`.

---

## 📋 Endpoints Principais

### 🩺 Health

* `GET /`
* `GET /api/hello`

### 🪄 Magias e Sincronização

* `GET /api/magias`
* `POST /api/sync/import-local-json`
* `POST /api/sync/export-local-json`

### 🧙‍♂️ Personagens

* `GET /api/v2/characters`
* `GET /api/v2/characters/<id>`
* `DELETE /api/v2/characters/<id>`
* `POST /api/v2/characters/wizard`
* `PUT /api/v2/characters/<id>/play`
* `PUT /api/v2/characters/<id>/spell-slots/<slot_level>`
* `POST /api/v2/characters/<id>/rest/short`
* `POST /api/v2/characters/<id>/rest/long`
* `PUT /api/v2/characters/<id>/inventory/<item_id>/equip`
* `PUT /api/v2/characters/<id>/inventory/<item_id>/attune`
* `POST /api/v2/characters/<id>/shop/purchase`
* `POST /api/v2/characters/<id>/ledger/reward`
* `GET /api/v2/characters/<id>/ledger`

---

## 💾 Banco de Dados e Sincronização

> ✨ **Regra de Ouro do Sistema:** O backend atua como a **fonte principal da verdade** (Single Source of Truth).

1. **Armazenamento Principal:** O backend utiliza o banco de dados **SQLite** local.
2. **Inicialização:** Ao iniciar o servidor, se o banco SQLite estiver completamente vazio, o sistema automaticamente importa os dados iniciais dos arquivos `personagens.json` e `magias.json`.
3. **Fluxo de Escrita:** Em qualquer operação de escrita bem-sucedida na API (`POST`, `PUT`, `PATCH`, `DELETE`), o backend realiza duas etapas ordenadas:
* **Primeiro:** Atualiza as tabelas correspondentes no SQLite.
* **Segundo:** Exporta e atualiza os JSONs do frontend, mantendo `personagens.json` e `magias.json` sempre sincronizados.



---

## 🎖️ Créditos

* **Base de dados externa:** [D&D 5e API](https://dnd5eapi.co)