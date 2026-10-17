---
applyTo: "**"
---

# Convention nommage des ressources
## Introduction
La convention de nommage est conçue en fonction du contexte AWS et de l’application à laquelle appartient chaque ressource. Son application rigoureuse garantit :
- **L'efficacité** : un repérage plus rapide et intuitif des composants
- **La cohérence** : une homogénéité dans le nommage des ressources d’une application, facilitant leur compréhension et leur maintenance
- **La sécurité** : une gestion plus fine des accès, en permettant d’attribuer les droits aux équipes selon les noms des ressources si la stratégie de tagging ne suffit pas
## La règle générale
Ci-dessous le pattern à respecter de manière globale sur toutes les ressources :
```
<TagApp>-<TagComp>-<Details>-<TagEnv>
```
**regles standard**
- Toujours utiliser le tag `App` en préfixe
- Toujours utiliser le tag `Env` en suffixe
- Eventuellement utiliser le tag `Comp` si présent ou bien un détail succint au milieu si besoin

**ne pas faire**
- Ne jamais utiliser le tag `Bloc` ou le tag `Team` (seules exceptions pour les ALBs et les workgroups Athena des FTs)
- Ne pas ajouter le type de la ressource dans son nom, par exemple :
 - exposed-classified-get-by-id-role-prod (pour un role IAM)
 - pro-gate-v2-aurora-cluster-prod (pour un cluster Aurora)
 - efk-os-prod (pour un cluster OpenSearch)

## Les règles spécifiques 
| Ressource AWS | Règle spécifique | Exemples | Commentaire | Contrainte / Objectif |
| --- | --- | --- | --- | --- |
| ALB des FTs | `<AcronymeTeam>-<int/ext>-<TagEnv> | ico-ext-prod |   | ALB mutualisé par FT (GOV-12). Le plus commun possible. Limiter le nombre d'ALB. |
| Bucket S3 | `<TagApp>-<AwsRegion>-<AwsAccountId>-<TagEnv>` | classified-deposit-eu-west-1-395174950964-prod |   | Les noms de bucket doivent être uniques globalement. Facilite le PRA. |
| Workgroup Athena des FTs | `workgroup-ft-<TagTeam>-<TagEnv>` | workgroup-ft-guardians-prod | Les workgroups des applications respectent la règle générale. | Des workgroup "applicatifs" VS des workgroup "d'équipe" avec des quotas adaptés. |
| Parameter Store | `/<TagEnv>/<TagApp>/…` :warning: Exception pour les ALB (idéalement le tag App pour les stacks déployant l'ALB doit correspondre à l'exception ci-dessous) `/<TagEnv>/<AcronymeTeam>-commons/alb/...` | /prod/bot-protection/edge/arn /prod/cfd-commons/alb/... |   |   |
