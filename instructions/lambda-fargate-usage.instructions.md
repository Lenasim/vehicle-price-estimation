---
applyTo: "**"
---

# Usage AWS Lambda and Fargate
Dans le cadre adoptation de Fargate nous etudions les possibilitées et scenarios qui peuvent etre legitime pour un usage Fargate, ainssi que etudier les details et comportements de service pour identifier the potentiel impacts de usage.

> [INFO] Chez GLC, aujourd’hui nous utilisons les instances Fargate avec AWS Batch ( à Date 2024-07-19 ) pour les traitement Job Schedulé ou Temporaire.

## Scenario
- **Les Workflows Permanents**: certains workflows applications ont besoin d’être executer et up runing en permanence (dison 24H/24) , ca peut etre potentiellement un candidat de usage Fragate sur ECS si selon different attribute validation les instance EC2 seront pas plus rentable. ca peu etre lié majoritairement aux couts potentiel mais ainssi  les autres elements comme besoin d’avoir access aux instance et etc..
- **Le Workflows Ephemeral Long**: Certains scenario necessite d’executer les workflows par l’impossibilité de garantie la duré max de process ou ont besoin avoir un garantie de execution long, ces scenarios peuvent etre un candidat de usage Fargate.
- **Les Workflows Ephemeral Court**: Certains Scenarios ont besoin un traitement avec une durée courte, ces cas ne sont pas légitimes au usage Fargate dans le sens qu’un instance Fargate a un durée demarage elévé ( dison 2 à 5 minute ) qui met en cause l’usage vs usage Lambda qui perform assez rapide et a un temps de demarage initialement courte ( Cold Start ).

## Critaires validation de choix
|   |   |
| --- | --- |
| Durée execution | Fargate / Lambda |
| Durabilité et cycle de vie d’instance | Permanence / Ephemeral |
| Le Trafic | High Trafic / Low Trafic / Trafic avec peak temporal |
| Besoin integration | Integration avec des autres service managé Fargate / Lambda |

## Points Etude à voir
La liste en desous present les differents details à etudier et confirmer pour voir la legitimité de usage Fargate
| Titre | Context | Observations |
| --- | --- | --- |
| Repartiotion de charge entre les instance | Workflow Permanence |   |
| Configuration Scaling | Workflow Permanence |   |
| Monitoring / Logging | Tous les workflows |   |
| Integration avec autres service | Workflow Ephemeral |   |
| Image / Runtimes / Mise à jour | Tous les workflows |   |
| Integration Agents CloudWatch, SSM etc.. | Tous les Workflows |   |
## Potentiel usecase GLC
| Titre | Context | Observations |
| --- | --- | --- |
| EDI | Traitement des fichiers exposés par les partners qui ont des tails varié selon le PartnerCes Traitement peuvent durée entre qq seconds à des minutes ( plus ? ) |   |
| Composer | Dans le cadre Refonte Mozart et l’architecture Microfrontend le composer sera le premiere point d’enré de site donc un impact direct sur la qualité de site comme User experience et Performance. c’est un cas legitime de voir la benefice de usage Fargate vs Lambda |   |
## Conclusion sur l’usage
- Workflows éphémères légitimes dont la durée d’exécution dépasse le timeout Lambda (15min)
  - Exemples: chaîne EDI

- Workflows éphémères avec un besoin fin sur les ressources (cpu, memory, etc…)
  - Exemples: TNR QA, tests de charge, …

- Workflows permanents qui ne peuvent pas être implémentées avec Lambda pour des raisons validées (performance, coûts, maintenance opérationnelle, sécurité, etc…)
  - Exemples: pas pour le moment
