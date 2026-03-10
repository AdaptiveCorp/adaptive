# Developer

You need those tools to start the project localy :

- uv

Then to set up the project, run :

```
uv sync
```

Before starting the application, you need to set up the configuration file. To do that, copy paste `.env.example` in file named `.env` and fill in the configuration.

To start the application, run :

```
uv run uvicorn adaptive.main:app --reload
```

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

If you want to reset the db, just delete the app.db file and run the previous command.
