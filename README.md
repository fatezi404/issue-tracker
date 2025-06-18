FastAPI based app with PostgreSQL, Alembic and SQLAlchemy.

**Notes:**
- I'm using HS256 symmetric algorithm to create secret key for JWT. As far as I know, it's not best practice, since you have to share your key. Better to use asymmetric algorithm like RS256. It creates two keys - public and private, which is safer way to handle secret keys.
- I've made async based Alembic connections/migrations for easier development. Because of that Alembic doesn't need multiple database URLs (one with asyncpg line and one w/o)