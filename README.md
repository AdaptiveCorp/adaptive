Avant de commencer à travailler sur le projet, installer UV en tant que package manager. Pour ce faire : 
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Pour créer votre virtual env il suffirat de lancer : 
```
uv sync
```
Normalement ca va créer votre venv et télécharger les packets dans le fichiers `pyproject.toml`. 

