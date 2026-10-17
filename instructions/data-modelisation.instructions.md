---
applyTo: "**"
---

# Modélisation des tables DynamoDB

## Normalisation des attributs
> [INFO]
> Le nommage des attributs doit être en **camelCase**
La normalisation garantit une certaine cohérence entre toutes les tables DynamoDB.

| Attribut | Obligatoire | Format | Exemples | Remarques |
| --- | --- | --- | --- | --- |
| pk | YES | string | classified#E115798872carmatch#fa6e86e9-d338-484f-8b7f-56b7b6daee68 | Les clés primaires (primary key et sort key) doivent toujours être nommées pk et sk, de manière agnostique (pas de nom métier)sk doit être défini systématiquement, même si aucun besoin immédiat n’est identifiéLes valeurs de pk/sk doivent suivre un format structuré avec des préfixes ou suffixes pour faciliter le Single Table DesignToujours penser à bien choisir les valeurs qui seront utilisées pour pkafin de favoriser la distribution des opérations de read et write (voir ) |
| sk | YES | string | detailsclassified#B300155522 |   |
| ttl | YES (sauf exceptions) | number(timestamp UNIX en secondes) | 1744281949 | Un attribut ttl (Time To Live) doit être utilisé pour les suppressions automatiquesL’exception doit être validée lors de la review initiale pendant l'étape de modélisation |
| createdAt | YES | string(ISO 8601) | 2024-11-18T16:42:26.140Z | Permet de tracer la date de création de l’item |
| updatedAt | YES | string(ISO 8601) | 2024-11-18T16:42:26.140Z | Permet de tracer la date de modification l’item |
## Intégration Atlan
Toutes les tables DynamoDB doivent être documentées et intégrées dans Atlan.
Se référer à [la documentation interne](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/13538469) pour le processus d'intégration.
