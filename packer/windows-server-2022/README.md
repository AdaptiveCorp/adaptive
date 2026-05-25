Script de déploiement d'un template windows avec packer.

# Build

Ajouter les ISO suivant :

- windows server
- virtio drivers
- CloudBase Init, pour ce faire :

```
wget https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi
```

Puis transformer le fichier en image iso :

```
mkisofs -J -r -o CloudbaseInitSetup_Stable_x64.iso CloudbaseInitSetup_Stable_x64.msi
```

Créer un fichier `variables.auto.pkrvars.hcl`.
Copier les valeur de `variables.pkrvars.hcl` dans le fichier créer et les modifier avec votre contexte (IP proxmox, ...).

Enfin, pour build le template, rendez vous dans un des répertoire de template.

```
cd packer/windows-server-2022
```

Et lancer :

```
packer build .
```

Pour ne pas supprimer la machine lorsqu'il y'a des erreur :

```
packer build -on-error=ask .
```

Pour avoir des logs plus pertinents pendant le build :

```
PACKER_LOG=1 PACKER_LOG_PATH="packer-debug.log" packer build . 2>&1 | tee /dev/stderr

cat packer-debug.log
```

# Explication des étapes
