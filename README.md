# 🔮 Grimmorium Backend API

Uma API Flask para gerenciamento de personagens.

Este repositório contém o **backend** responsável pela lógica de negócios, persistência e gerenciamento do sistema Grimmorium. Ele funciona de forma integrada ao repositório frontend, garantindo que os dados estejam sempre atualizados.

---

## 🛠️ Pré-requisitos

1. **Sistema Operacional:** Windows com PowerShell.
2. **Linguagem:** Python 3.10+ instalado ([Download aqui](https://www.python.org)).

---

## 🚀 Passo a Passo para Execução

Siga a ordem dos comandos abaixo no seu PowerShell:

### 1. Criar ambiente virtual

```powershell
python -m venv .venv

```

### 2. Ativar ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1

```

### 3. Entrar na pasta do backend

```powershell
cd .\grimmorium-react-backend

```

### 4. Instalar dependências

```powershell
pip install -r requirements.txt

```

### 5. Iniciar backend

```powershell
python main.py

```

👋 **Como parar o backend:** No terminal onde a API está rodando, pressione `Ctrl + C`.

---

## 🧪 Como testar se está funcionando

Com o servidor ligado, você pode abrir os seguintes links no seu navegador para validação:

* **API Raiz:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
* **Health Check:** [http://127.0.0.1:5000/api/hello](http://127.0.0.1:5000/api/hello)
* **Swagger (Interface de testes):** [http://127.0.0.1:5000/openapi/swagger](http://127.0.0.1:5000/openapi/swagger)

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