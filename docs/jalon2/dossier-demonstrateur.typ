// ============================================================
//  Configuration et mise en page
// ============================================================

// --- Couleurs
#let riskRed = rgb("#C0392B")
#let riskOrange = rgb("#E67E22")
#let riskGreen = rgb("#27AE60")
#let riskBlue = rgb("#2980B9")
#let riskDark = rgb("#2C3E50")
#let riskLightGray = rgb("#F4F6F7")

#let pp-stroke = (x, _) => (
  left: if x == 0 { none } else { 0.4pt + rgb("#CCCCCC") },
  right: none,
  top: none,
  bottom: none,
)
// --- Variable entreprise
#let nomEntreprise = [_Nautic Commerce_]

// --- Boîte colorée avec titre (équivalent tcolorbox)
#let boite-risque(couleur, titre, corps) = block(
  width: 100%,
  radius: 4pt,
  clip: true,
  stroke: couleur,
  above: 0.8em,
  below: 0.8em,
  stack(
    block(fill: couleur, width: 100%, inset: 8pt)[
      #text(fill: white, weight: "bold")[#titre]
    ],
    block(fill: couleur.lighten(94%), width: 100%, inset: 8pt)[
      #corps
    ],
  )
)

#show heading: it => {
  it
  v(0.4em)
}

// --- Boîte simple sans titre
#let boite-simple(couleur, corps) = block(
  width: 100%,
  radius: 4pt,
  inset: (x: 6pt, y: 4pt),
  stroke: 0.6pt + couleur,
  fill: couleur.lighten(92%),
  above: 0.4em,
  below: 0.4em,
  corps
)

// --- Badges de niveau de risque
#let badge-red(contenu) = box(
  fill: riskRed.lighten(70%),
  inset: (x: 4pt, y: 2pt),
  radius: 2pt,
  text(fill: riskRed, weight: "bold", size: 0.9em)[#contenu],
)
#let badge-orange(contenu) = box(
  fill: riskOrange.lighten(70%),
  inset: (x: 4pt, y: 2pt),
  radius: 2pt,
  text(fill: riskOrange, weight: "bold", size: 0.9em)[#contenu],
)
#let badge-green(contenu) = box(
  fill: riskGreen.lighten(70%),
  inset: (x: 4pt, y: 2pt),
  radius: 2pt,
  text(fill: riskGreen, weight: "bold", size: 0.9em)[#contenu],
)

// --- Mise en page
#set document(
  title: "Architecture sécurisée — e-Commerce de biens nautiques",
  author: ("Titouan", "Dilan", "Feur"),
)
#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.75cm, right: 1.75cm),
  header: context {
    let pg = counter(page).get().first()
    if pg > 1 [
      #grid(
        columns: (1fr, 1fr),
        align: horizon,
        pad(left: -0.5cm)[
          #text(fill: rgb("#2C3E50").lighten(50%))[
            // TODO: décommenter quand le logo sera ajouté
            #image("images/logo-ensibs.png", width: 2cm)
          ]
        ],
        pad(right: -0.5cm)[
          #align(right)[
            #text(size: 0.9em, fill: rgb("#2C3E50").lighten(50%))[
              #emph[Projet Cyber 4A - Jalon 1 - Adaptive]
            ]
          ]
        ],
      )
    ]
  },
  footer: context {
    let pg = counter(page).get().first()
    if pg > 1 [
      #line(length: 100%, stroke: 0.4pt + rgb("#2C3E50").lighten(50%))
      #v(0.2em)
      #align(center)[
        #text(size: 0.9em, fill: rgb("#2C3E50").lighten(50%))[#str(pg)]
      ]
    ]
  },
)


#set text(font: "New Computer Modern", size: 12pt, lang: "fr")
#set par(leading: 0.9em, spacing: 1.2em, justify: true)
#set heading(numbering: "1.1.1")
#show link: set text(fill: riskBlue)

// ============================================================
//  PAGE DE TITRE
// ============================================================

#v(3em)
#align(center + horizon)[
  #text(size: 20pt, weight: "bold")[Projet Cyber 4A - Adaptive] \
  #v(0.8em)
  #text(size: 14pt)[Jalon 1 - Dossier démonstrateur]
  #v(1.5em)
  #align(center)[
    Youenn BELZ \
    Malko LECHEVREL \
    Gabriel PINTO DA SILVA \
    Gwendal LE GUELLEC \
    Guillaume MORICE
  ]
]
#v(2em)

// --- Résumé
#align(center)[*Résumé*]
#v(0.5em)
#pad(x: 2em)[
  Ce rapport a pour but de présenter l'état d'avancement du projet Adaptive. Il est nécessaire de rappeler la problématique à laquelle répond la solution. Les choix techniques seront également passés en revue. Les fonctionnalités implémentées pour cette preuve de concept seront documentées. De plus, un point sur la couverture de la solution ainsi que les prochaines étapes seront abordés.
]
#v(2em)
#align(center)[
  // TODO: décommenter quand le logo sera ajouté
  #image("images/logo-ensibs.png", width: 50%)
]

#pagebreak()
#outline()
#pagebreak()

= Introduction

En cyberdéfense, nous avons remarqué la difficulté d'être à l'état de l'art sur la menace. Beaucoup d'agences et de grandes entreprises mettent énormément de moyens afin de maîtriser les dernières techniques d'attaques, à des fins de prévention. 

Pour ce faire, les équipes SOC et PENTEST doivent avoir des environnements leur
permettant d'expérimenter des vulnérabilités modernes, d'entraîner leurs ingénieurs, afin d'améliorer la pertinence des tests d'intrusions et d'évaluer en même temps les outils de détection en conditions contrôlées. La configuration de tels environnements sans outils est une tâche ingrate qui demande un très haut niveau d'expertise et de temps humain.

L’objectif de notre projet est de fournir à nos clients un outil pour déployer rapidement un terrain d’entraînement sécurisé afin que les professionnels puissent mettre à l'épreuve leurs techniques d’intrusion et de détection

= Rappel du dossier de définition

ADaptive lab serait une solution de EaaS (Environment as a Service), permettant de déployer un serveur Windows et d’y configurer des vulnérabilités de manière automatisée. L’utilisateur aurait à sa disposition plusieurs versions de serveur windows et plusieurs configurations de vulnérabilité. 

= Architecture technique V0

Nous avons fait le choix d'une architecture minimaliste, articulée autour de trois briques principales : une API centrale, une interface web et une couche d'automatisation. Cette approche permet un développement rapide tout en gardant une séparation claire des responsabilités.

// TODO: image à ajouter — schéma d'architecture globale (3 briques : API, Frontend, Automatisation)
// #image("images/architecture-globale.png", width: 90%)

== API centrale

Le cœur de la solution repose sur une *API REST* développée en *Python*. Ce choix s'explique par la richesse de l'écosystème Python en matière d'automatisation d'infrastructure : il existe des bibliothèques matures pour piloter des hyperviseurs, exécuter des commandes à distance sur des machines Windows, et orchestrer des configurations réseau. Python permet également un développement rapide et une maintenance simplifiée.

L'API expose un ensemble de routes permettant de gérer l'intégralité du cycle de vie d'un projet : création de l'infrastructure, configuration des serveurs, ajout des utilisateurs, application des vulnérabilités et déclenchement du déploiement. Toutes les données sont stockées dans une base de données locale, ce qui garantit la portabilité de la solution.

== Interface web

L'interface utilisateur est développée en *TypeScript* avec le framework *React*, une technologie à l'état de l'art du développement web. Ce choix garantit une expérience utilisateur moderne, fluide et réactive.

L'interface permet de configurer visuellement l'infrastructure Active Directory souhaitée, de visualiser la hiérarchie sous forme de graphe interactif, et de déclencher le déploiement en un seul clic. Elle communique exclusivement avec l'API centrale, ce qui assure une séparation nette entre la présentation et la logique métier.

// TODO: image à ajouter — capture d'écran de l'interface web (dashboard)
// #image("images/screenshot-dashboard.png", width: 90%)

== Couche d'automatisation

La troisième brique est la couche d'automatisation, responsable du déploiement effectif de l'infrastructure :

- *Proxmox* : hyperviseur open-source utilisé pour héberger les machines virtuelles. L'API pilote Proxmox pour cloner des templates, configurer le réseau et démarrer les machines.
- *Ansible* : outil d'orchestration permettant de configurer les machines Windows à distance (promotion en contrôleur de domaine, création d'utilisateurs, injection de vulnérabilités). La communication s'effectue via le protocole WinRM, natif à Windows.
- *Packer* : outil de construction d'images machine. Il permet de créer des templates Windows Server réutilisables, pré-configurés avec les outils nécessaires (accès distant, initialisation réseau).

Cette architecture modulaire permet de remplacer facilement l'hyperviseur cible si nécessaire, grâce à une couche d'abstraction entre l'API et Proxmox.

== Modèle de données

L'organisation des données reflète la structure réelle d'un environnement Active Directory. Le schéma suit une hiérarchie logique :

#boite-simple(riskBlue)[
  *Projet* → contient une ou plusieurs *Forêts* \
  #h(2em) *Forêt* → contient un ou plusieurs *Domaines* \
  #h(4em) *Domaine* → contient des *Serveurs* et des *Utilisateurs de domaine* \
  #h(6em) *Serveur* → peut être un contrôleur de domaine (DC) \
  #h(6em) *Serveur* → peut contenir des *Utilisateurs locaux*
]

En parallèle, un *catalogue de vulnérabilités* permet de définir des failles de sécurité sous forme de templates réutilisables. Chaque vulnérabilité peut être associée à un utilisateur, un serveur ou un domaine au sein d'un projet.

= Fonctionnalités implémentées V0

Cette section présente les fonctionnalités opérationnelles dans cette première version de la solution. L'ensemble de ces briques s'enchaîne automatiquement lors du déploiement.

== Déploiement automatisé des machines virtuelles

#boite-simple(riskGreen)[
  L'utilisateur définit les serveurs de son infrastructure via l'interface web. Au moment du déploiement, chaque machine virtuelle est *automatiquement créée, configurée et démarrée* sur l'hyperviseur.
]

Le processus est entièrement transparent pour l'utilisateur :

- Une machine virtuelle est clonée à partir d'un template Windows Server pré-configuré
- Le réseau est automatiquement paramétré (adresse IP, passerelle, serveur DNS)
- La machine est démarrée et prête à recevoir sa configuration Active Directory

L'utilisateur n'a besoin d'aucune connaissance de l'hyperviseur sous-jacent.

== Promotion en contrôleur de domaine

#boite-simple(riskGreen)[
  Les serveurs désignés comme contrôleurs de domaine sont *automatiquement promus*, créant un environnement Active Directory fonctionnel et réaliste.
]

Deux scénarios sont gérés :

- *Création d'une forêt* : le premier contrôleur de domaine installe les services Active Directory et crée la forêt et le domaine racine
- *Ajout d'un contrôleur secondaire* : les serveurs suivants rejoignent le domaine existant, reproduisant une architecture multi-DC réaliste

Après la promotion, le système attend automatiquement que les services Active Directory soient pleinement opérationnels avant de passer à l'étape suivante.

== Création des utilisateurs

#boite-simple(riskGreen)[
  Les comptes utilisateurs définis dans l'interface sont *créés en masse*, avec l'ensemble de leurs attributs. La solution distingue deux types d'utilisateurs.
]

*Utilisateurs de domaine :*
Rattachés à un domaine Active Directory, ils sont créés dans l'annuaire sur le contrôleur de domaine correspondant. Pour chaque utilisateur, sont configurés :
- Identifiant et mot de passe
- Prénom et nom de famille
- Adresse e-mail au format standard de l'entreprise
- Unité organisationnelle (OU) de rattachement

*Utilisateurs locaux :*
Rattachés directement à un serveur spécifique, ils représentent des comptes locaux sur la machine. Cette distinction permet de reproduire des scénarios d'attaque réalistes où certains comptes ne sont pas présents dans l'annuaire centralisé.

Les utilisateurs de domaine sont regroupés par domaine et créés sur le contrôleur de domaine approprié, reproduisant fidèlement la structure d'une entreprise.

== Injection de vulnérabilités

#boite-risque(riskRed, "Cœur de la solution : injection automatisée de failles")[
  ADaptive permet d'injecter automatiquement des *vulnérabilités réalistes* dans l'environnement Active Directory. Ces failles reproduisent les techniques d'attaque les plus courantes rencontrées en entreprise.
]

Le système repose sur un *catalogue de vulnérabilités* définies de manière déclarative. Chaque faille est décrite par un template contenant les actions à exécuter sur l'infrastructure cible.

Chaque vulnérabilité appliquée dispose d'un *suivi de statut* permettant de connaître son état à tout moment : en attente, appliquée, modifiée ou en erreur. Les vulnérabilités peuvent également être *retirées* du projet à tout moment, offrant une flexibilité totale dans la configuration de l'environnement d'entraînement.

*Vulnérabilités disponibles en V0 :*

#figure(
  block(
    stroke: 0.5pt + rgb("#CCCCCC"),
    radius: 3pt,
    clip: true,
    {
      set text(size: 0.9em)
      set par(justify: false)
      table(
        columns: (1.5fr, 1fr, 3fr),
        stroke: pp-stroke,
        inset: (x: 6pt, y: 8pt),
        fill: (_, row) => if row == 0 { riskDark } else if calc.odd(row) { riskLightGray } else { white },
        table.header(
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Vulnérabilité]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Catégorie]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Description]],
        ),
        [AS-REP Roasting], [#badge-red[Kerberos]],
          [Désactivation de la pré-authentification Kerberos, permettant à un attaquant de récupérer un hash hors-ligne],
        [Kerberoasting], [#badge-red[Kerberos]],
          [Ajout d'un service fictif à un compte utilisateur, rendant son mot de passe extractible via le protocole Kerberos],
        [GenericAll], [#badge-orange[ACL]],
          [Attribution de droits totaux d'un utilisateur sur un autre, permettant la prise de contrôle complète du compte],
        [WriteDACL], [#badge-orange[ACL]],
          [Possibilité de modifier les droits d'accès d'un objet Active Directory],
        [ForceChangePassword], [#badge-orange[ACL]],
          [Droit de réinitialiser le mot de passe d'un autre utilisateur sans connaître l'ancien],
        [DCSync], [#badge-orange[Réplication]],
          [Droits de réplication du domaine, permettant d'extraire tous les mots de passe de l'annuaire],
      )
    }
  ),
  caption: [Catalogue de vulnérabilités V0],
)

*Exemple de définition d'une vulnérabilité :*

Le template ci-dessous illustre comment une vulnérabilité de type Kerberoasting est définie dans le catalogue. Les paramètres entre accolades sont remplacés automatiquement par les valeurs correspondantes au moment du déploiement.

```yaml
- code: kerberoasting
  name: Kerberoasting
  type: vulnerability
  description: >
    Ajoute un SPN à un compte utilisateur
    pour le rendre Kerberoastable
  category: kerberos
  required_params:
    - username
    - spn_name
```

== Interface web

#boite-simple(riskBlue)[
  L'application web offre une *interface intuitive* pour concevoir, visualiser et déployer une infrastructure Active Directory vulnérable, sans aucune ligne de commande.
]

L'interface se compose de trois écrans principaux :

*Page d'accueil — Liste des projets :*
- Création et suppression de projets
- Accès rapide au détail de chaque projet

// TODO: image à ajouter — capture de la liste des projets
// #image("images/screenshot-projects.png", width: 90%)

*Détail d'un projet — Vue à onglets :*
- *Tableau de bord* : vue d'ensemble avec compteurs (forêts, domaines, serveurs, utilisateurs, vulnérabilités) et graphe interactif de la hiérarchie AD
- *Forêts / Domaines / Serveurs / Utilisateurs* : gestion complète (ajout, suppression) de chaque niveau de la hiérarchie
- *Vulnérabilités* : catalogue disponible et vulnérabilités appliquées au projet

// TODO: image à ajouter — capture du détail projet avec onglets
// #image("images/screenshot-project-detail.png", width: 90%)

*Gestion des templates VM :*
- Enregistrement des images de base disponibles sur l'hyperviseur
- Sélection du template lors de la création d'un serveur

== Déploiement

#boite-risque(riskGreen, "Pipeline de déploiement automatisé")[
  Un *unique bouton* dans l'interface déclenche l'intégralité du processus de déploiement. L'utilisateur n'a qu'à concevoir son infrastructure puis cliquer sur « Déployer ».
]

La solution propose *deux modes de déploiement* complémentaires :

*Déploiement complet en un clic :*
Le pipeline exécute automatiquement les quatre étapes dans l'ordre :

+ *Clonage des machines virtuelles* — création et configuration réseau de chaque serveur
+ *Promotion des contrôleurs de domaine* — installation d'Active Directory
+ *Création des utilisateurs* — peuplement de l'annuaire
+ *Injection des vulnérabilités* — application des failles de sécurité configurées

*Déploiement objet par objet :*
L'utilisateur peut également déployer individuellement chaque élément de son infrastructure. Il est par exemple possible de déclencher la création d'un utilisateur spécifique ou l'application d'une vulnérabilité particulière, sans relancer l'ensemble du pipeline. Cette granularité est utile pour ajuster un environnement déjà déployé ou pour tester des configurations pas à pas.

En cas d'erreur à n'importe quelle étape, le processus s'arrête immédiatement et un message explicite est retourné à l'utilisateur. Le résultat du déploiement (succès ou échec détaillé) est affiché directement dans l'interface.

= Taux de couverture de la conception

== Méthode de calcul

Le taux de couverture mesure l'avancement de l'implémentation par rapport aux fonctionnalités prévues dans le dossier de définition (Jalon 1). Chaque fonctionnalité est évaluée selon trois niveaux :

- #badge-green[Complet] — fonctionnalité pleinement opérationnelle
- #badge-orange[Partiel] — fonctionnalité présente mais nécessitant des améliorations
- #badge-red[Non implémenté] — fonctionnalité prévue mais non encore développée

== Matrice de couverture

#figure(
  block(
    stroke: 0.5pt + rgb("#CCCCCC"),
    radius: 3pt,
    clip: true,
    {
      set text(size: 0.9em)
      set par(justify: false)
      table(
        columns: (2.5fr, 0.8fr, 2.5fr),
        align: (left, center, left),
        stroke: pp-stroke,
        inset: (x: 6pt, y: 8pt),
        fill: (_, row) => if row == 0 { riskDark } else if calc.odd(row) { riskLightGray } else { white },
        table.header(
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Fonctionnalité]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Statut]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Commentaire]],
        ),
        [Clonage et démarrage des VM], [#badge-green[OK]],
          [Clonage automatique + configuration réseau],
        [Promotion en contrôleur de domaine], [#badge-green[OK]],
          [Création de forêt et ajout de DC],
        [Création des utilisateurs AD], [#badge-green[OK]],
          [Création en masse avec attributs complets],
        [Vulnérabilités Kerberos], [#badge-green[OK]],
          [AS-REP Roasting et Kerberoasting],
        [Vulnérabilités ACL], [#badge-green[OK]],
          [GenericAll, WriteDACL, ForceChangePassword],
        [Vulnérabilité DCSync], [#badge-green[OK]],
          [Droits de réplication du domaine],
        [Interface web — gestion de projets], [#badge-green[OK]],
          [CRUD complet sur tous les niveaux],
        [Interface web — tableau de bord], [#badge-green[OK]],
          [Compteurs et graphe de hiérarchie AD],
        [Interface web — vulnérabilités], [#badge-green[OK]],
          [Catalogue et application des failles],
        [Pipeline de déploiement complet], [#badge-green[OK]],
          [4 étapes automatisées en un clic],
        [Interface web — expérience utilisateur], [#badge-orange[Partiel]],
          [Fonctionnel mais feedback et validation à améliorer],
        [Catalogue de vulnérabilités étendu], [#badge-orange[Partiel]],
          [6 vulnérabilités, catégories supplémentaires à ajouter],
        [Templates VM automatisés], [#badge-orange[Partiel]],
          [Template existant, processus à industrialiser],
        [Suivi du déploiement en temps réel], [#badge-red[Non impl.]],
          [Pas de barre de progression dans l'interface],
      )
    }
  ),
  caption: [Matrice de couverture des fonctionnalités],
)

== Taux global

#boite-risque(riskGreen, "Taux de couverture estimé : 75 %")[
  Sur les 14 fonctionnalités identifiées : *10 complètes*, *3 partielles*, *1 non implémentée*. Les fonctionnalités critiques du démonstrateur — déploiement automatisé, configuration Active Directory et injection de vulnérabilités — sont toutes opérationnelles.
]

Les deux axes d'amélioration principaux pour atteindre une couverture complète sont :

- *Amélioration de l'interface web* : retours utilisateur plus détaillés (barre de progression du déploiement, messages d'erreur contextuels, validation des formulaires)
- *Enrichissement du catalogue de vulnérabilités* : ajout de catégories supplémentaires (élévation de privilèges, mouvement latéral, accès aux credentials)

= Perspectives — Jalon 2

== Planning prévisionnel

// TODO: image à ajouter — diagramme de Gantt
#image("images/gantt.png", width: 95%)

== Feuille de route

#boite-risque(riskBlue, "Axes de développement pour le Jalon 2")[
  Le Jalon 2 se concentre sur l'enrichissement du catalogue de vulnérabilités, l'amélioration de l'expérience utilisateur et la robustesse globale de la solution.
]

*Enrichissement du catalogue de vulnérabilités :*
- Ajout de scénarios d'élévation de privilèges (permissions de services, droits locaux)
- Ajout de techniques de mouvement latéral (exécution à distance, rebond entre machines)
- Ajout de techniques d'accès aux credentials (mots de passe en clair, stratégies de groupe)
- Mise en place de chaînes d'attaques pré-configurées reproduisant des scénarios réalistes

*Amélioration de l'expérience utilisateur :*
- Barre de progression en temps réel pendant le déploiement
- Messages d'erreur détaillés et contextuels
- Validation des formulaires côté interface
- Export de la configuration du laboratoire

*Robustesse et industrialisation :*
- Validation du support multi-forêts avec relations d'approbation inter-domaines
- Automatisation de la création des templates VM via un pipeline d'intégration continue
- Extension de la couverture de tests

== Estimation du temps de travail

#figure(
  block(
    stroke: 0.5pt + rgb("#CCCCCC"),
    radius: 3pt,
    clip: true,
    {
      set text(size: 0.9em)
      set par(justify: false)
      table(
        columns: (2.5fr, 1fr, 1.5fr),
        align: (left, center, left),
        stroke: pp-stroke,
        inset: (x: 6pt, y: 8pt),
        fill: (_, row) => if row == 0 { riskDark } else if calc.odd(row) { riskLightGray } else { white },
        table.header(
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Tâche]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Estimation]],
          table.cell(fill: riskDark)[#text(fill: white, weight: "bold")[Priorité]],
        ),
        [Nouvelles vulnérabilités (6-8 templates)], [2 semaines], [#badge-red[Haute]],
        [Amélioration interface utilisateur], [2 semaines], [#badge-red[Haute]],
        [Validation multi-forêts], [1 semaine], [#badge-orange[Moyenne]],
        [Suivi déploiement temps réel], [1 semaine], [#badge-orange[Moyenne]],
        [Automatisation pipeline Packer], [1 semaine], [#badge-green[Basse]],
        [Documentation utilisateur], [1 semaine], [#badge-green[Basse]],
      )
    }
  ),
  caption: [Estimation du temps de travail — Jalon 2],
)

