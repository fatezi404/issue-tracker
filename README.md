# FastAPI issue tracker app

FastAPI based app with PostgreSQL as main database, Redis as a storage for JWT tokens and caching, Alembic and SQLAlchemy.


## Notes

- I'm using HS256 symmetric algorithm to create secret key for JWT. As far as I know, it's not best practice, since you have to share your key. Better to use asymmetric algorithm like RS256. It creates two keys - public and private, which is safer way to handle secret keys.
- I've made async based Alembic connections/migrations for easier development. Because of that Alembic doesn't need multiple database URLs (one with asyncpg line and one w/o)


## Run Locally

Clone the project

```bash
  git clone https://github.com/fatezi404/issue-tracker
```

Go to the project directory

```bash
  cd issue-tracker
```

Create .env file

```bash
  DATABASE_URL=postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@db:${DATABASE_PORT}/${DATABASE_NAME}
  DATABASE_PORT=db_port
  DATABASE_USER=db_user
  DATABASE_PASSWORD=db_pass
  DATABASE_NAME=db_name
  SECRET_KEY=secret_key
```

Build Docker container
```bash
  docker compose up -d
```

Check Swagger documentation
```bash
  http://localhost:8000/api/v1/docs
```

