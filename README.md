# ADaptive — API

Application web pour générer des infrastructures Active Directory vulnérables sur Proxmox, destinées à l'entraînement en pentest.

## Prérequis

- [uv](https://docs.astral.sh/uv/) — gestionnaire de packages et d'environnement Python

## Installation

```bash
# Installer les dépendances et créer l'environnement virtuel
uv sync
```

Copier le fichier `.env.example` en `.env` et renseigner la configuration :

```bash
cp .env.example .env
```

## Lancer l'application

Créer les différentes tables nécessaires. Pour ca il faut lancer la commande `alembic` suivante :

```bash
uv run alembic upgrade head
```

Attention, il faut qu'il y'ai au moins un fichier de migration qui créé les tables dans `migrations/verions`. Si il y'en a pas, il faut le générer avec :

```bash
uv run alembic revision --autogenerate -m "initial"
```

Cette commande va traduire les modèles de nos objets dans `api/models` en table et colonne SQL.

Pour reset la db et la mettre à jour avec les dernière modification fait tout simplement :

```bash
rm app.db && rm -rf migrations/versions/* && uv run alembic revision --autogenerate -m "initial" && uv run alembic upgrade head
```

```bash
# Mode développement (rechargement automatique)
uv run uvicorn adaptive.api.main:app --reload

# Mode production
uv run gunicorn adaptive.api.main:app -k uvicorn.workers.UvicornWorker
```

L'API est disponible sur `http://localhost:8000`. La documentation Swagger est accessible sur `/docs`.

## Migrations de base de données

### Principe

ADaptive utilise **Alembic** pour gérer les migrations de sa base de données SQLite.

Une **migration** est un script Python qui décrit une modification du schéma de la base de données (ajout d'une table, d'une colonne, changement de type, etc.). Chaque migration possède un identifiant unique (un hash) et un pointeur vers la migration précédente, formant ainsi une **chaîne ordonnée** de toutes les évolutions du schéma.

L'intérêt principal est de pouvoir :

- **Versionner** le schéma de la base au même titre que le code
- **Reproduire** la base de données à l'identique sur n'importe quelle machine en rejouant les migrations
- **Collaborer** sans conflits : chaque développeur génère ses migrations depuis ses modifications de modèles, et Alembic les applique dans l'ordre
- **Revenir en arrière** si une migration pose problème (`downgrade`)

### Workflow

Le schéma de référence est défini par les **modèles SQLAlchemy** dans `adaptive/api/models/`. On ne modifie **jamais** une migration à la main.

Le cycle de travail est le suivant :

1. **Modifier un modèle** SQLAlchemy (ajouter un champ, une table, une relation…)
2. **Générer la migration** — Alembic compare les modèles au schéma actuel et produit automatiquement le script de migration :
   ```bash
   uv run alembic revision --autogenerate -m "description du changement"
   ```
3. **Appliquer la migration** — exécute tous les scripts en attente pour mettre la base à jour :
   ```bash
   uv run alembic upgrade head
   ```

### Commandes utiles

```bash
# Voir la révision actuellement appliquée
uv run alembic current

# Afficher l'historique complet des migrations
uv run alembic history

# Annuler la dernière migration appliquée
uv run alembic downgrade -1

# Réinitialiser la base (supprimer et recréer)
rm app.db && uv run alembic upgrade head
```

> **Note :** Les templates de vulnérabilités sont automatiquement injectés au démarrage de l'application depuis `templates.yaml`.

# Status des templates

Un template lorsqu'il est appliqué peut avoir plusieurs status :

- applied
- failed
- modified
- pending

## Linting

Le projet utilise deux linters, installés automatiquement avec `uv sync` (groupe `dev`) :

### Ruff (Python)

uv run yamllint adaptive/api/database/

[Ruff](https://docs.astral.sh/ruff/) s'occupe du lint et du formatage du code Python. La configuration se trouve dans `pyproject.toml` sous `[tool.ruff]`.

```bash
# Vérifier les erreurs de lint
uv run ruff check .

# Corriger automatiquement les erreurs
uv run ruff check . --fix

# Vérifier le formatage
uv run ruff format --check .

# Formater automatiquement
uv run ruff format .
```

Règles activées : pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify.

### yamllint (YAML)

[yamllint](https://yamllint.readthedocs.io/) valide les fichiers YAML du dossier `adaptive/api/database/` (templates de vulnérabilités). La configuration se trouve dans `.yamllint.yml`.

```bash
uv run yamllint adaptive/api/database/
```

### Avant de commit

```bash
uv run ruff check . --fix && uv run ruff format . && uv run yamllint adaptive/api/database/
```

# Docker

Pour build

```bash
docker build -t adaptive-api .
```

Pour lancer :

```bash
docker run --rm -p 8000:8000 --env-file .env adaptive-api
```
