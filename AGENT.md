# Backend Agent Guide - Sletter

Este guia fornece as instruções necessárias para que uma IDE com LLM integrado (como Cascade, Cursor, Copilot) possa entender, consumir e testar este backend localmente.

## 🚀 Visão Geral
O Sletter Backend é uma API construída com **FastAPI**, utilizando **Supabase** como banco de dados e autenticação. Ele gerencia bibliotecas pessoais de filmes, séries e jogos, permitindo a criação de coleções customizadas.

- **Base URL Local:** `http://localhost:8000` (padrão uvicorn)
- **Documentação Automática:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔐 Autenticação e Segurança

### 1. Supabase Auth
A API utiliza o sistema de autenticação do Supabase via tokens **JWT**.
- **Header Obrigatório:** `Authorization: Bearer <SUPABASE_USER_JWT>`
- O token deve ser obtido via Supabase Auth (geralmente passado pelo frontend).
- A lógica de validação está em `@/app/auth/auth.py`.

### 2. Rate Limiting
Utilizamos o `slowapi` para limitar requisições e evitar abusos.
- Erros de limite retornam HTTP 429.

---

## 📡 Endpoints Principais

### 🎬 Media (Filmes e Séries)
Prefixo: `/media` | Integração: TMDB API

- **POST `/media/add_on_lib`**: Adiciona um item à biblioteca.
  - Body: `{"tmdb_id": "string", "media_type": "movie|tv", "watched": "watched|not_watched|in_progress", "collection_id": "uuid|null"}`
- **GET `/media/{tmdb_id}`**: Detalhes de um item na biblioteca do usuário.
- **PUT `/media/{tmdb_id}`**: Atualiza o status (`watched`) de um item.
- **DELETE `/media/{tmdb_id}`**: Remove um item da biblioteca.
- **POST `/media/add_on_collection`**: Adiciona múltiplos itens existentes a uma coleção.

### 🎮 Games
Prefixo: `/game` | Integração: RAWG API

- **POST `/game/add_on_lib`**: Adiciona um jogo à biblioteca.
  - Body: `{"rawg_id": int, "status": "unplayed|playing|completed", "collection_id": "uuid|null"}`
- **GET `/game/{rawg_id}`**: Detalhes de um jogo na biblioteca.
- **PUT `/game/{rawg_id}`**: Atualiza o status de um jogo.
- **DELETE `/game/{rawg_id}`**: Remove um jogo da biblioteca.

### 📂 Collections
Prefixo: `/collections`

- **GET `/collections/`**: Lista todas as coleções do usuário com um preview dos itens.
- **POST `/collections/create`**: Cria uma nova coleção.
  - Body: `{"name": "string"}`
- **GET `/collections/{collection_id}`**: Lista todos os itens (filmes, séries e jogos) de uma coleção específica.

### 🔍 Discover (Busca Externa)
Prefixo: `/discover`

- **GET `/discover/new_movie?title=NAME`**: Busca filmes/séries no TMDB.
- **GET `/discover/new_game?title=NAME`**: Busca jogos na RAWG.

### 🗂️ Catalog
- **GET `/catalog/all`**: Retorna toda a biblioteca do usuário organizada por categorias.

---

## 🛠️ Requisitos de Ambiente (.env)
Para rodar localmente, o arquivo `.env` deve conter:
- `SUPABASE_URL`: URL do projeto Supabase.
- `SUPABASE_KEY`: Service Role ou Anon Key (dependendo da config).
- `TMDB_TOKEN`: Bearer token da API do TMDB.
- `RAWG_API_KEY`: Chave da API RAWG.

---

## 💻 Como Rodar
1. Instale as dependências: `pip install -r requirements.txt`
2. Inicie o servidor: `uvicorn app.main:app --reload`

## 🧠 Instruções para o Agente LLM
Ao realizar requisições para este backend:
1. **Sempre inclua o Header de Autorização** se o endpoint exigir `get_login_user`.
2. **Respeite os modelos Pydantic**: Verifique em `@/app/media/models.py`, `@/app/games/models.py` e `@/app/collections/models.py` os campos obrigatórios.
3. **Tratamento de Erros**: A API retorna detalhes em `{"detail": "mensagem"}` em caso de erro (4xx ou 5xx).
4. **CORS**: O backend está configurado para aceitar requisições de `http://localhost:3000`.
