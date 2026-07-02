# 🔮 Grimmorium Backend API

API Flask desenvolvida para o gerenciamento de personagens, grimórios e mecânicas de economia. O backend atua como a fonte padrão de dados para a aplicação.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
* Python 3.10 ou superior
* Pip (Gerenciador de pacotes do Python)

---

## 🛠️ Instalação e Configuração

Siga os passos abaixo no terminal a partir da raiz do projeto para configurar o ambiente isolado (.venv):

### 1. Criar o ambiente virtual na raiz do projeto (Recomendado)
```bash
python -m venv .venv
```

### 2. Acessar o diretório do backend
```bash
cd grimmorium-react-backend
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

---

## 🚀 Execução (Windows / PowerShell)

Certifique-se de que o ambiente virtual esteja ativo (o terminal exibirá `(.venv)` no início da linha). 

Como você já está dentro da pasta `grimmorium-react-backend`, execute o servidor diretamente com o comando do Python:

```powershell
python .\main.py
```

* **Servidor local:** http://127.0.0.1:5000

---

## 📖 Documentação da API (Swagger / OpenAPI)

Com o servidor rodando, você pode acessar a interface de testes ou o esquema nos seguintes links:
* **Interface Swagger UI:** http://127.0.0
* **Esquema JSON:** http://127.0.0

---

## 📍 Endpoints Essenciais

Abaixo estão as principais rotas públicas e internas da aplicação:

### Status e Testes
* `GET /` — Página ou rota raiz.
* `GET /api/hello` — Teste rápido de conectividade.

### Personagens e Grimórios
* `GET /api/v2/characters` — Listar personagens existentes.
* `POST /api/v2/characters/wizard` — Criar um novo mago.
* `GET /api/magias` — Listar magias cadastradas.

### Sincronização de Arquivos
* `POST /api/sync/import-local-json` — Importar dados dos arquivos JSON locais para o banco.
* `POST /api/sync/export-local-json` — Exportar dados do banco de volta para os JSON locais.

---

## 💾 Banco de Dados e Sincronização

* **Tecnologia:** SQLite armazenado localmente em `instance/grimmorium.db`.
* **Fonte da Verdade:** O backend é a fonte principal e oficial de todos os dados (*source of truth*).
* **Seed Inicial Opcional:** Caso o banco SQLite esteja vazio ao iniciar, a API importa automaticamente os arquivos `grimmorium-react-main/public/personagens.json` e `grimmorium-react-main/public/magias.json`.
* **Sincronização Ativa:** Após qualquer alteração via API (`POST`, `PUT`, `PATCH`, `DELETE`), os arquivos JSON locais podem ser atualizados de forma automática pelo backend para manter a compatibilidade com o frontend.

---

## 🛡️ Apoio ao MVP

Este ecossistema de backend sustenta todas as regras de negócio essenciais para o MVP do projeto:
* Criação guiada de novos personagens da classe Mago (*wizard*).
* Modo de jogo (*play mode*) com atualização da ficha em tempo real.
* Consulta e gerenciamento de grimórios de magias.
* Validação rápida e documentada de ponta a ponta via Swagger.

---

## 🌍 Créditos e APIs Externas

* **[D&D 5e API](https://dnd5eapi.co)** — API pública REST utilizada para consumir e integrar dados oficiais do sistema Dungeons & Dragons 5ª Edição.
