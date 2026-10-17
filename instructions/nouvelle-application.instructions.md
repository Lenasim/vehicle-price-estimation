---
applyTo: "**"
---

# Process à suivre pour les nouvelles applications

# **Process attendu**
## **1. Brainstorm technique**
Avant d'entamer un nouveau projet, tous les membres de la Feature Team doivent être au fait de la documentation suivante : 
- [Principes et conventions](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13535296)
- [Bonnes pratiques Amazon Web Services](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13533847)
Ainsi que toute la section [TECHNOLOGIES ET OPÉRATIONS](https://jira-glc.atlassian.net/wiki/spaces/ARCHI)
Ensuite le début du brainstorm technique peut démarrer pour poser les idées et les pistes de réalisation
## **2. ****Création Fiche architecture**
La première étape d'un nouveau projet c'est la rédaction de la fiche archi : page modele [[Modèle] Fiche architecture](https://jira-glc.atlassian.net/wiki/pages/createpage.action?spaceKey=ARCHI&title=%5BMod%C3%A8le%5D%C2%A0Fiche%20architecture&linkCreation=true&fromPageId=13533576)
Tous les champs de la fiche doivent être définis sans exception : Tags (Bloc App Comp Team), Github [Tag sur les ressources (Référentiel du SI)](https://jira-glc.atlassian.net/wiki/pages/createpage.action?spaceKey=ARCHI&title=Tag%20sur%20les%20ressources%20AWS&linkCreation=true&fromPageId=13533576)
Un schéma de l'architecture devra être fait avec [LucidChart](https://lucid.app/documents) (les identifiants du compte d'équipe sont disponibles dans votre vault 1Password d'équipe).
N'oubliez pas le diagramme de dépendances avec les autres équipes et les autres systèmes
- Echanger avec votre TechLead et votre PO pour vous aider à identifier des dépendances fonctionnelles
- Concevoir en commun lorsque ces périmètres sont conjoints (API, ou parcours utilisateur commun)
- Associer les personnes en amont.
  

> [WARNING]
> Penser à faire une première présentation globale du projet (Fiche archi + besoin) par l'équipe aux CSA pour validation des grands principes.  
> Ceci est un accompagnement afin que la team CSA puisse collaborer avec la FT pour prendre le ou les choix technique(s) les plus avisés selon le besoin et le contexte pour ne pas tout remettre en question lors de la review préliminaire.
## **3. Data Model and Data Flow Design **
### DynamoDB
[DynamoDB](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13533361) est la solution préconisée pour stocker les données. Une étude particulière doit être menée pour son utilisation avec l'ensemble des cas d'usages (c'est à dire l'identification des access patterns).
Il faudra également respecter le [dictionnaire de données GLC](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13533700), si des nouvelles données venaient a être crée ou modifiées, il faudrait alors alimenter un nouveau modèle documenté.
Conformément au RGPD, il convient d'être dans une démarche "Privacy by default" où la durée de rétention des données personnel est prévu dès la conception, en fonction de son usage prévu. Aucune donnée personnelle n'est gardé advitam.
Cette page vous guidera dans les étapes à suivre : [Modèle Physique DynamoDB](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13538469)
### Autres
Dans tous les autres cas d'échanges de données, les modèles doivent être documentés : API Swagger , Message SNS, Structure de données livrée sur datalake... 
### Artefacts
Tous les projets conduisent à produire ou modifier les artefacts suivants :
- Le glossaire métier, Business Glossary ( [https://atlan.carboatservices.fr/glossary/95516b42-7c82-47d3-85c2-d8947585d4d6](https://atlan.carboatservices.fr/glossary/95516b42-7c82-47d3-85c2-d8947585d4d6) )
- [Les modèles de données, Data Model and Dictionary](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13538427) (par exemple pour DynamoDB : [Modèle Physique DynamoDB](https://noe.carboatmedia.fr/pages/viewpage.action?pageId=83626801) )
- Les dictionnaire de champs, [[DataGov] Dictionnaire Log & Event](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13541277)
## **4. Etude de couts**
Pour toute nouvelle stack, l'étude doit être faite dans un fichier Excel puis attaché à la page.
Le chiffre mensuel devra être indiqué dans la fiche archi.
Un modèle XLS est dispo dans le modèle de fiche archi.
  

## **5****. Revue Stack Préliminaire : Fiche Architecture & présentation**
Lors de cette revue avec les CSA, vous effectuerez la revue comme si vous étiez en train de faire la présentation de la revue initiale.
Demander aux CSA de vous partager leurs avis à fin de valider les détails de structure de fiche architecture, principes & choix effectué & les coûts engendrés par cette archi.
**Vous pouvez utiliser la liste de diffusion **[**csa@lacentrale.fr**](mailto:csa@lacentrale.fr)** (CSA)**
> [WARNING]
> Cette étape peut être réalisée soit en mode présentation (réunion physique ou distancielle) ou asynchrone selon la disponibilité et le choix.  
>   
> **Historique:** lors des different points **Review stack initiale, **nous avons constaté un passage rapide du temps et beaucoup de discussions portée par l'équipe CSA et nous souhaitons que l'ensemble des participants puissent partager leurs points de vue tout en évitant de remettre en question la base même de l'architecture. Cette étape permettra de revue préliminaire permet de minimiser les retours dans la phase de revue initiale, ce qui permettra aux autres participants d'échanger autour des points opérationnels et fonctionnels afin de mieux profiter de ce moment d'échange.
## **6****. Revue Stack initiale : Fiche Architecture & présentation**
Convoquer une réunion, afin de valider tous les principes & choix effectués & le cout, avant de commencer les développements (hors POC) avec :
- tout ou partie de votre équipe (votre deputy cto et votre Tech Lead sont facultatifs) afin de présenter le projet de stack
- pour établir une relecture croisée:
  - CTO @62061d5bff9289006eed1d68  (ou un Deputy CTO pour le représenter)
  - un autre Deputy CTO que celui de votre l'équipe. **Vous pouvez utiliser la liste de diffusion **[**ctos@lacentrale.fr**](mailto:ctos@lacentrale.fr)** (LISTE_CTOS)**
  - un autre TechLead que celui de votre l'équipe. **Vous pouvez utiliser la liste de diffusion **[**team-techleads@lacentrale.fr**](mailto:team-techleads@lacentrale.fr)** (Team Tech Leads)**
  - un CSA. **Vous pouvez utiliser la liste de diffusion **[**csa@lacentrale.fr**](mailto:csa@lacentrale.fr)** (CSA)**
  - un autre OPS. **Vous pouvez utiliser la liste de diffusion **[**operations@carboatmedia.fr**](mailto:operations@carboatmedia.fr)** (LISTE-OPERATIONS)**
  - les équipes fortement dépendantes ou impactées. Même s'il n'y a pas besoin d'évolution concrète, il reste important d'informer l'équipe qui gère le service qui sera utilisé.

Une revue par une autre équipe est également conseillée pour partage de pratiques et aller un peu plus dans le détail.

>> Page à mettre en sous page de la fiche archi : [Fiche Archi] Review Stack
## **7. Réalisation, Iterations et Refinement**
Préparer tous les tickets pour la réalisation du projet et itérer en N Sprints de 2 semaines
Chaque re-conception fera l'objet d'une réunion avec un CSA (idéalement celui de la première revue), et éventuellement les personnes nécessaires de la première revue (en cas de synchro inter-FT).
Prévoir une review tous les 2 sprints en debut de projet, ajustable avec le CSA en fonction de la progression du projet.
## **8. Review Stack finale**
Étape indispensable qui validera votre stack, avant la MEP
L'objectif est de valider d'une manière exhaustive que les points suivants ont été checkés :
- Dictionnaire métier & physique [Modèle Physique DynamoDB](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13538469)
- Technologies utilisées
- Pipeline & Build automatisés
- Usage des librairies communes GLC : [Librairies communes](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13538958)
- Qualité du code
- Respect du dictionnaire de données
- Reprise de données (du legacy)
- Tests & couverture
- Tests de charge
- Monitoring & Alerting
- Coût prévisionnel
- Bilan des reservations / saving plans / spot
>> Page modèle à utiliser, a mettre en sous page de la fiche archi : [Fiche Archi] Review Stack
## **9. MEP**
Mise en production planifiée et chronologiquement préparée via un ticket, associé à l'épopée JIRA du projet.
L'usage est d'utiliser un canal projet lorsque ce dernier est transverse.
Tous les étapes devront être détaillées, par ex : double run, reprise de données, batchs, etc...
# **Process light**
Pour des "petites" stacks, il est possible de demander un process light à la place du process classique.
Ce process light a pour but d'accélérer le workflow en simplifiant les étapes : 
- Soumission de la demande de process light sur le channel Gouvernance DT
- Si acceptation par CTO/DeputyCTO/CSA, organisation d'une pair review pour validation
- Si pas de validation, passage par le process classique
:info: la notion de "petite" stack est volontairement non définie, et il est de la responsabilité du demandeur et du validateur de considérer ou non si la stack est légitime au process light
