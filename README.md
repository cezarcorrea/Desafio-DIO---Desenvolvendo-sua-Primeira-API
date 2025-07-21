# Desafio DIO - Desenvolvendo sua Primeira API 

## WORKOUT_API

Este é o backend da aplicação de gerenciamento de treinos, construído com FastAPI, SQLAlchemy (para ORM) e PostgreSQL. Ele permite o gerenciamento de atletas, categorias e centros de treinamento, oferecendo uma API robusta e paginada.

### 📋 Sumário

- Visão Geral

- Funcionalidades

- Tecnologias Utilizadas

- Estrutura do Projeto

- Configuração do Ambiente

- Pré-requisitos

- Variáveis de Ambiente

- Rodando com Docker (Recomendado)

- Rodando Localmente (Sem Docker)

- Endpoints da API

- Atletas

- Categorias

- Centros de Treinamento

- Paginação

- Tratamento de Erros

- Licença

- Contato

## 🌟 Visão Geral
A WORKOUT_API é a espinha dorsal para um sistema de gestão de academias ou centros de treinamento. Ela expõe endpoints RESTful para criar, ler, atualizar e deletar informações sobre atletas, as categorias em que eles se enquadram e os centros de treinamento onde eles praticam. A API é projetada para ser escalável e fácil de consumir por qualquer aplicação cliente (web, mobile, etc.).

## ✨ Funcionalidades
### Gerenciamento de Atletas:

- Criação, listagem (com paginação), busca por ID e edição de atletas.

- Validação de CPF único para cada atleta.

- Associação de atletas a categorias e centros de treinamento existentes.

### Gerenciamento de Categorias:

- Criação, listagem e busca por ID de categorias de atletas.

- Validação de nome de categoria único.

- Prevenção de exclusão de categorias com atletas vinculados.

### Gerenciamento de Centros de Treinamento:

- Criação, listagem e busca por ID de centros de treinamento.

- Validação de nome de centro de treinamento único.

- Prevenção de exclusão de centros de treinamento com atletas vinculados.

### Paginação:

- Listagem de atletas com suporte a limit e offset para otimização de performance e experiência do usuário.

- Tratamento de Erros:

- Respostas de erro claras e informativas (400 Bad Request, 404 Not Found, 409 Conflict, 500 Internal Server Error).

## 🛠️ Tecnologias Utilizadas
### Backend:

- Python 3.11.4 Linguagem de programação.

- FastAPI: Framework web de alta performance para construir APIs.

- SQLAlchemy: ORM (Object Relational Mapper) para interagir com o banco de dados.

- Alembic: Ferramenta de migração de banco de dados.

- fastapi-pagination: Biblioteca para adicionar paginação aos endpoints.

- pydantic: Para validação de dados e serialização.

- uuid: Para geração de IDs únicos.

### Banco de Dados:

- PostgreSQL 17 Banco de dados relacional robusto.

## Infraestrutura:

- Docker / Docker Compose: Para orquestração de contêineres e facilidade no ambiente de desenvolvimento.

### 📂 Estrutura do Projeto

```
WORKOUT_API/
├── workout_api/
│   ├── atleta/
│   │   ├── controllers.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── categorias/
│   │   ├── controllers.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── centro_treinamento/
│   │   ├── controllers.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── contrib/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   ├── database.py
│   ├── main.py
│   └── routers.py
├── .python-version
├── alembic.ini                
├── Dockerfile.txt
├── docker-compose.yml
└── requirements.txt 
```

## ⚙️ Configuração do Ambiente
### Pré-requisitos
- Docker e Docker Compose (recomendado)

- Python 3.11+

- Pipenv (opcional, para gerenciar dependências Python localmente)

- PostgreSQL 17.x (se não usar Docker)

### Variáveis de Ambiente
As variáveis de ambiente são definidas diretamente no arquivo `docker-compose.yml` para o ambiente Docker, ou podem ser configuradas localmente através de um arquivo `.env` (não versionado) se rodar sem Docker.

- `DATABASE_URL`: String de conexão com o banco de dados PostgreSQL.

- Exemplo para Docker: `postgresql+asyncpg://admin:admin@db:5432/workout` (o nome do host é o nome do serviço do banco de dados no `docker-compose.yml`)

Exemplo para local: `postgresql+asyncpg://admin:admin@localhost:5432/workout`

## Rodando com Docker (Recomendado)
### 1. Construa as imagens e inicie os serviços:


`docker-compose up --build -d`

Isso vai construir a imagem da sua API, iniciar um contêiner PostgreSQL 17 e um contêiner para sua API. O `-d` faz com que eles rodem em segundo plano.

### 2. Executar Migrações (criar tabelas no DB com Alembic):
Após os contêineres subirem, você precisa executar as migrações do Alembic para criar as tabelas no banco de dados.


`docker-compose exec workout-api alembic upgrade head`

Este comando entra no contêiner da sua API (`workout-api`) e executa o Alembic para aplicar todas as migrações pendentes.

### 3. Verificar Status:

`docker-compose ps` 

Você deverá ver seus serviços workout-api e db rodando.

Acessar a API:
A API estará disponível em `http://localhost:8000`.
A documentação interativa (Swagger UI) estará em `http://localhost:8000/docs`.

## Rodando Localmente (Sem Docker)
### 1. Clone o repositório:

```
git clone git@github.com:cezarcorrea/Desafio-DIO---Desenvolvendo-sua-Primeira-API.git
```

### 2. Crie e ative um ambiente virtual:

```
python -m venv venv
.\venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux
```

### 3. Instale as dependências:


`pip install -r requirements.txt`

### 4. Configure o banco de dados PostgreSQL 17.x:
Certifique-se de ter uma instância PostgreSQL 17.x rodando e crie um banco de dados conforme sua `DATABASE_URL`.

### 5. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto e adicione sua `DATABASE_URL`local:


`DATABASE_URL="postgresql+asyncpg://admin:admin@localhost:5432/workout"`

### 6. Executar Migrações (Alembic):

`alembic upgrade head`

Isso vai criar as tabelas no seu banco de dados local.

### 7. Inicie a aplicação:

`uvicorn workout_api.main:app --reload --host 0.0.0.0 --port 8000`

O `--reload` é útil para desenvolvimento, pois reinicia o servidor a cada alteração no código.

### 8. Acesse a API:
A API estará disponível em `http://localhost:8000`.
A documentação interativa (Swagger UI) estará em `http://localhost:8000/docs`.

## 🚀 Endpoints da API
A documentação interativa completa está disponível em `http://localhost:8000/docs` após iniciar o servidor.

### Atletas
- POST `/atletas/`

   - Descrição: Cria um novo atleta.

   - Corpo da Requisição: `AtletaIn` (requer `nome`, `cpf`, `idade`, `peso`, `altura`, `sexo`, `categoria_nome`, `centro_treinamento_nome`).

   - Retorno: `AtletaOut` (201 Created)

   - Erros: 400 Bad Request (CPF já existente, categoria/centro não encontrado), 409 Conflict (CPF duplicado), 500 Internal Server Error.

- GET `/atletas/{id}`

   - Descrição: Consulta um atleta pelo seu ID.

   - Parâmetro de URL: `id` (UUID do atleta).

   - Retorno: `AtletaOut` (200 OK)

   - Erros: 404 Not Found.

- GET `/atletas/`

   - Descrição: Lista todos os atletas com paginação.

   - Parâmetros de Query: `limit` (número máximo de itens, padrão 10), `offset` (número de itens a pular, padrão 0).

   - Retorno: `LimitOffsetPage[AtletaOut]` (200 OK)

- PATCH `/atletas/{id}`

   - Descrição: Edita as informações de um atleta pelo seu ID.

   - Parâmetro de URL: `id` (UUID do atleta).

   - Corpo da Requisição: `AtletaUpdate` (campos opcionais: `nome`, `idade`, `peso`, `altura`, `categoria_nome`, `centro_treinamento_nome`).

   - Retorno: `AtletaOut` (200 OK)

   - Erros: 404 Not Found, 400 Bad Request (categoria/centro não encontrado), 409 Conflict (CPF duplicado), 500 Internal Server Error.

- DELETE `/atletas/{id}`

   - Descrição: Deleta um atleta pelo seu ID.

   - Parâmetro de URL: `id` (UUID do atleta).

   - Retorno: (204 No Content)

   - Erros: 404 Not Found.

### Categorias
- POST `/categorias/`

   - Descrição: Cria uma nova categoria.

   - Corpo da Requisição: `CategoriaIn` (requer `nome`).

   - Retorno: `CategoriaOut` (201 Created)

   - Erros: 409 Conflict (nome de categoria já existente), 500 Internal Server Error.

- GET `/categorias/{id}`

  - Descrição: Consulta uma categoria pelo seu ID.

  - Parâmetro de URL: `id` (UUID da categoria).

  - Retorno: `CategoriaOut` (200 OK)

  - Erros: 404 Not Found.

- GET `/categorias/`

  - Descrição: Lista todas as categorias.

  - Retorno: `list[CategoriaOut]` (200 OK)

- DELETE `/categorias/{id}`

  - Descrição: Deleta uma categoria pelo seu ID.

  - Parâmetro de URL: `id` (UUID da categoria).

  - Retorno: (204 No Content)

  - Erros: 404 Not Found, 409 Conflict (categorias com atletas vinculados).

### Centros de Treinamento
- POST `/centros_treinamento/`

  - Descrição: Cria um novo centro de treinamento.

  - Corpo da Requisição: `CentroTreinamentoIn` (requer `nome`, `endereco`, `proprietario`).

  - Retorno: `CentroTreinamentoOut` (201 Created)

  - Erros: 409 Conflict (nome de centro de treinamento já existente), 500 Internal Server Error.

- GET `/centros_treinamento/{id}`

  - Descrição: Consulta um centro de treinamento pelo seu ID.

  - Parâmetro de URL: `id` (UUID do centro de treinamento).

  - Retorno: `CentroTreinamentoOut` (200 OK)

  - Erros: 404 Not Found.

- GET `/centros_treinamento/`

   - Descrição: Lista todos os centros de treinamento.

   - Retorno: `list[CentroTreinamentoOut]` (200 OK)

- PATCH `/centros_treinamento/{id}`

   - Descrição: Edita as informações de um centro de treinamento pelo seu ID.

   - Parâmetro de URL: `id` (UUID do centro de treinamento).

   - Corpo da Requisição: `CentroTreinamentoUpdate` (campos opcionais: `nome`, `endereco`, `proprietario`).

   - Retorno: `CentroTreinamentoOut` (200 OK)

   - Erros: 404 Not Found, 409 Conflict (nome de centro de treinamento duplicado), 500 Internal Server Error.

- DELETE `/centros_treinamento/{id}`

  - Descrição: Deleta um centro de treinamento pelo seu ID.

  - Parâmetro de URL: `id` (UUID do centro de treinamento).

  - Retorno: (204 No Content)

  - Erros: 404 Not Found, 409 Conflict (centros de treinamento com atletas vinculados).

## 📄 Paginação
O endpoint `GET /atletas/` suporta paginação para gerenciar grandes conjuntos de dados de forma eficiente.

  - `limit`: Número máximo de itens a serem retornados em uma única resposta (tamanho da página).

  - `offset`: Número de itens a serem "pulados" do início do conjunto de resultados (deslocamento).

### Exemplo:
`GET /atletas/?limit=20&offset=0` - Retorna os primeiros 20 atletas.
`GET /atletas/?limit=10&offset=20` - Retorna os atletas da posição 21 à 30.

## 🚫 Tratamento de Erros
A API retorna códigos de status HTTP apropriados e mensagens de erro descritivas em caso de problemas:

  - `400 Bad Request`: Dados de entrada inválidos ou inconsistentes (ex: categoria/centro não encontrado ao criar atleta).

  - `404 Not Found`: Recurso não encontrado (ex: atleta com ID inexistente).

  - `409 Conflict`: Violação de restrição de unicidade (ex: CPF já cadastrado, nome de categoria/centro duplicado) ou tentativa de exclusão de recurso vinculado.

  - `500 Internal Server Error`: Erro inesperado no servidor.

## 📜 Licença
Este projeto está licenciado sob a Licença MIT.

## 📫 Contato

Fique à vontade para visitar meu perfil no GitHub: [@cezarcorrea](https://github.com/cezarcorrea)

---
