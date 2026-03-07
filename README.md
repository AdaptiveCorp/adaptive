# Developer

You need those tools to start the project localy :

- uv

Then to set up the project, run :
uv sync

## Migrations

Use the alembic command to create and run the migrations.
If you want to change the database schema or add some data, you need to create a new migration.
To do this, run :

```
uv run alembic revision -m "migration_name"
```

Then, write some sqlalchemy code to update or populate the database and run :

```
uv run alembic upgrade head
```
