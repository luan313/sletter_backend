# Sletter Backend - AI Agent Integration & Developer Guide

Este documento é a especificação técnica definitiva para agentes de IA (Cascade, Cursor, Copilot) e desenvolvedores. Ele detalha como consumir, testar e integrar com o backend do Sletter, garantindo precisão em cada chamada.

## 🚀 Informações Gerais
- **Base URL:** `http://localhost:8000`
- **Docs (Swagger):** `http://localhost:8000/docs`
- **Stack:** FastAPI, Supabase (PostgreSQL + Auth), TMDB API (Mídia), RAWG API (Jogos).

---

## 🔐 Autenticação e Segurança

### Supabase JWT Auth
Endpoints protegidos exigem autenticação via Bearer Token.
- **Header:** `Authorization: Bearer <JWT_TOKEN>`
- **Nota:** O token é validado via `Depends(get_login_user)`. Erro `401` indica token inválido ou expirado.

### Rate Limiting (SlowAPI)
- **Escrita:** ~20-30 req/min.
- **Leitura:** ~60-100 req/min.
- **Erro:** `429 Too Many Requests`.

---

## 📡 Referência Completa de Endpoints

### 🎬 Mídia (Filmes & Séries) - Prefix: `/media`

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/add_on_lib` | Adiciona mídia à biblioteca (valida no TMDB). |
| `POST` | `/add_on_collection` | Adiciona múltiplas mídias a uma coleção. |
| `GET` | `/{tmdb_id}` | Detalhes de mídia salva + IDs de coleções associadas. |
| `PUT` | `/{tmdb_id}` | Atualiza o status de visualização (`watched`). |
| `DELETE` | `/{tmdb_id}` | Remove a mídia da biblioteca. |

#### Detalhes Técnicos:
- **`POST /add_on_lib` Body:**
  ```json
  {
    "tmdb_id": "string",
    "media_type": "movie" | "tv",
    "watched": "watched" | "not_watched" | "in_progress",
    "collection_id": "uuid" (opcional)
  }
  ```
- **`PUT /{tmdb_id}` Body:** `{"watched": "watched" | "not_watched" | "in_progress"}`

---

### 🎮 Jogos - Prefix: `/game`

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/add_on_lib` | Adiciona jogo à biblioteca (valida no RAWG). |
| `POST` | `/add_on_collection` | Adiciona múltiplos jogos a uma coleção. |
| `GET` | `/{rawg_id}` | Detalhes do jogo salvo + IDs de coleções associadas. |
| `PUT` | `/{rawg_id}` | Atualiza o status de progresso (`status`). |
| `DELETE` | `/{rawg_id}` | Remove o jogo da biblioteca. |

#### Detalhes Técnicos:
- **`POST /add_on_lib` Body:**
  ```json
  {
    "rawg_id": integer,
    "status": "unplayed" | "playing" | "completed",
    "collection_id": "uuid" (opcional)
  }
  ```
- **`PUT /{rawg_id}` Body:** `{"status": "unplayed" | "playing" | "completed"}`

---

### 📂 Coleções - Prefix: `/collections`

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/create` | Cria uma nova coleção vazia. |
| `GET` | `/` | Lista todas as coleções com preview de 5 itens. |
| `GET` | `/{collection_id}` | Lista todos os itens de uma coleção. |
| `PUT` | `/{collection_id}` | Renomeia a coleção. |
| `DELETE` | `/{collection_id}` | Deleta a coleção. |

---

### 🔍 Busca e Descoberta

#### 1. Busca Global (Na Biblioteca) - `/search/`
Busca mídias, jogos e coleções do próprio usuário.
- **Query Params:**
  - `query` (string, min 2): Termo de busca.
  - `type` (List): Filtra categorias (`media`, `games`, `collections`). Ex: `?type=media&type=games`.
- **Response:** Resultados organizados por tipo.

#### 2. Descoberta Externa - `/discover`
Busca dados diretamente nas APIs oficiais (TMDB/RAWG).
- `GET /discover/new_movie?title={string}`
- `GET /discover/new_game?title={string}`

---

### 🗂️ Catálogo Geral - `/catalog`
- `GET /catalog/all`: Retorna toda a biblioteca organizada por `movies`, `series` e `games`.

---

## 🛠️ Modelos de Dados (Pydantic)

Ao gerar requisições, siga rigorosamente os modelos em:
- **Media:** `@/app/media/models.py` (`MediaToSave`, `WatchedStatus`)
- **Game:** `@/app/games/models.py` (`GameToSave`, `GameStatus`)
- **Collection:** `@/app/collections/models.py` (`CollectionToCreate`)
- **Search:** `@/app/search/models.py` (`FilterModel`)

---

## 💡 Guia de Troubleshooting para o Agente

- **Erro 401:** Token JWT ausente ou inválido.
- **Erro 403:** Tentativa de acessar/editar recurso de outro usuário (ou coleção inexistente).
- **Erro 404:** Item não encontrado na biblioteca do usuário.
- **Erro 409:** Nome de coleção duplicado para o mesmo usuário.
- **Erro 422:** Payload JSON mal formatado ou tipos incorretos.

**Dica Pró:** Sempre utilize o `tmdb_id` (string/int) ou `rawg_id` (int) como identificadores nas rotas de `/media` e `/game`, respectivamente.
