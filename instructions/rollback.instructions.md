---
applyTo: "**"
---

# Rollback de deploiment d'application
Suite de point lié au process rollback à date 2023-12-21 nous avons pris la decision de mettre en place un system simple pour garder un snapshot de chaque artifact deployer. la decision qui a été convoqué est bien utilisation des tags.
Les elements décrits lors de phase etude:  

## Requirement
Le besoin se décrit comme:
- **Rollback Rapid**: Avoir le Taggage comme un moyen d'avoir un pointer vers état stable ( snapshot )
- **Automated Tag / ReleaseNote**: Usage des GitHub Actions
- **Conventional commits**: Standardisation des Conventional commits et les forcer dans la Phase dev

**Les details de besoin**
- Faciliter faire Rollback et revenir en arrière vers un état fiable soit vers la révision précédant
- l'état fiable d’une application doit être identifiable
- Un release represent un état fiable et encapsule une ensemble des changements
- Un release doit presenter les changement qu’il porte via Release Notes
- Les release notes doit avoir un lien vers les Tickets ( Chez GLC Jira )
- La Creation des Tags et Release doit etre automatisé
- Les Tags et release doit presenter une version de type SemVer ( Tag & Release Auto Generation prend en compte )
- Le tag represent une revision fiable et on doit être capable de faire un Rollback d'un revision vers l’autre
# Remarques
Lors de plusieurs points, il y a eu des remonté concernant les cas edge et les cas quotedians qui peuvent arriver
- Hesitation de generer les tags inutil
  - Pour ce but nous avons decider d’activer les tags et release notes que pour la branche source production

- Empechement de Generation des tags au ca besoin
  - Dans certain cas comme reset prod depuis la derniere tag our besoin de retirer un seul commit en vigilence nous avoins besoin de mettre une possibilité de bypasser la generation des tags ceci est realisable en suivant la documentation de GitHub (We can prevent by GitHub known message standard example **[skip ci]** ( [GitHub Documentation](https://docs.github.com/en/actions/managing-workflow-runs/skipping-workflow-runs) ) )

- Avoir les commit conventionels varié
  - Dans le cas de presense de plusieurs type de message dans meme release genre doc, fix, ci, feat ou breaking change , selons les tests suivant effectué le tag generation considere le type plus critical
    - Breaking change + n'importe quel autre type, consideration sera changement major ( Breaking change )
    - Fix + Feat,  consideration sera changement minor ( feat )
    - Docs + Fix, consideration sera changement patch ( fix )


- Avoir la force de generation d’un tag dans le cas urgence
  - Si par example un non-respect de conventional commit est detecter le auto tagging ne sera pas en mesure de generation des tags, dans ce ca la il y aura la possibilité de crée un release et tag dans github à la Mano pour debloquer le process delivery
    - Dans ce cas,  Team owner de projet sera responsable de generation d’un release note propre manuelement
    - Suivre le SemVer pour correctement versioner le tag


- Avoir un Workaround si les conventional commits ne sont pas respecter
  - Mise en place de un hook pour les commits conventionel sera obligatoir
    - Type de changement ( ci, docs, feat, fix etc.. )
    - Subject : Numero Ticket Jira livrable
    - Message: un message representant le changement orienté produit
    - Example: feat([DT-0100]):  add a github reusable workflow

  - Squashing: Si le nombre des commits non conventionnels dans phase development est elevé un Squash sera obligatoire lors de merge dans branche final avec un message de squash conventionnel. ca permettra à workflow considerer le message final et pas les commits message non conventionnel lors de development.

# Pour quoi Tag
Pour le but de process rollback et pouvoir automatiser au maximum possible la phase operationel, nous devrons avoir un minima de control,  observability et standard pour pouvoir prendre les decision dans le pipeline cicd en maniere automatique, observer le behavior et controler le process automatique . donc taggage semble un bon candidat simple et conventionnel pour se lancer.  
  
Un tag ca nous permetra simplement faire le checkout et avoir le ref diff , ca permettra de selectioner un precedant Tag en cas des Alarms durant le deployment en mode atomatique ou semi automatique.  
# Mise en place de process
Pour mettre en place le process de rollback nous considerons un process operationel dans une itération 1 pour l’env Production en utilisation Taggage comme un snapshot mais nous considerons le pouvoir de rollback dans different env comme dev et test aussi sans tag
## Auto Tagging and release note
La mise en place de auto taggage et release note generation sera effectué par **GitHub Actions. GLC **fournie un workflow partagé pour ce process à l’ensemble des applications qui devrais etre utiliser dans le repositories de chaque projet
La documentation:  [https://github.com/groupelacentrale/glc-github-workflows/blob/prod/docs/auto-tagger.md](https://github.com/groupelacentrale/glc-github-workflows/blob/prod/docs/auto-tagger.md) 
> [INFO]
> Les example usage sont fournie dans la documentation, à noter qu’on doit utiliser la derniere version donc latest mais il y a un possibilité de choisir les tags. Lors de utilisation des numero tags considerez des eventuels evolutions.  
> **To Note: **Lisez la section [Versioning](https://github.com/groupelacentrale/glc-github-workflows/blob/prod/README.md#versioning)  de documentation pour avoir une vision detailé de strategy evolution et enhancements
Example usage: [https://github.com/groupelacentrale/pro-user-management/blob/master/.github/workflows/prod-tagger.yml](https://github.com/groupelacentrale/pro-user-management/blob/master/.github/workflows/prod-tagger.yml) 
## Delivery Pipeline
Au seine de groupe notre principal util de deploiement est AWS Code Pipeline ( à date de 2024-04-04 ), Code pipeline fournie de Version V1 et V2 (   ) , nous utilison principalement la V1 soit version default des pipeline crée qui support un declanchement de pipeline par branche , la V2 propose un declanchement par tag aussi que branche, sachant que definition d’un trigger par tag override la configuration de trigger branch.
Pour adopter le declanchement de delivery par tag nous devrons migré vers la V2 de code pipeline, cette evolution sera effectivement realisable par usage de  [Lib CICD](https://github.com/groupelacentrale/ga-libs/blob/master/cdk-cicd/README.md) qui permettra passer un parameter PipelineType ( soit PipelineType.V2 ) et un triggerConfig ( un example present dans Lib Readme ).

Example Usage:  [https://github.com/groupelacentrale/pro-user-management/blob/eb35e63751800436a82090da50dc86d661041063/aws/cdk/bin/pipeline.ts#L24](https://github.com/groupelacentrale/pro-user-management/blob/eb35e63751800436a82090da50dc86d661041063/aws/cdk/bin/pipeline.ts#L24) 
## Rolling back
En cas de besoin d’un rollback code pipeline v2 fournit un declanchement de pipeline à partir d’une révision soir un commit id, donc le rollback sera réalisable pour tous les environment par commit id,

la seul difference entre dev/test et l’env production sera la facon de recuperation de commit id , pour l’environment de Production nous allons regarder le dernier commit id de tag precedant et lancerons le process rollback. pour les env dev et test ca sera a trouver le commit id dans la branch concerné.

 
# References
Voici une liste des refs vers les documentations qui permettra de deep dive dans les sujets varié à considerer lors de notre process Commity Of Excelence ( CoE )
- AWS Pipeline types:
- Choosing Squash / Rebase or Merge :
- SemVer action :
- Auto Delete Head Branches :
- Configuring Allow Merge Commit:
- Branch Protection Rule:
