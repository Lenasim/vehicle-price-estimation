---
applyTo: "**"
---

## Sécurisation des internet-facing endpoints
Pour assurer une protection optimale de toutes les surfaces exposées sur internet et réduire les risques d’attaques, il est essentiel de mettre en place des mesures de sécurité adaptées. Cette documentation couvre les recommandations de sécurité applicables aux ressources suivantes :
- CloudFront
- ALB
- Function URL
- API Gateway
## Les différentes typologies
Le domaine doit être sélectionné selon l’usage prévu de la ressource :
- Si usage externe → domaine publique, accessible depuis internet
- Si usage interne → domaine privé, accessible uniquement depuis le VPN ou le VPC

|   | Cible | Domaine publique | Domaine privé |
| --- | --- | --- | --- |
| CloudFront WEB | Tout ce qui dessert du contenu pour le WEB (HTML, JS, CSS, BFF). Contenu HTML généré en SSR Assets JS, CSS, etc… <br> Certains endpoints spécifiques rattachés à un BFF Concerne uniquement du client-to-server | *.lacentrale.fr*.caradisiac.com*.espacevo.fr | *.carboat.cloud |
| CloudFront API | Tout ce qui dessert des APIs d'applications agnostiques du consommateur. Contenu JSON généralementConcerne du server-to-server ou client-to-server | *.carboatservices.fr | *.carboat.cloud |
## Protections à mettre en place
### Utilisation de CloudFront
> [INFO] CloudFront est intrinsèquement une ressource exposée sur internet, même lorsque configuré avec un nom de domaine privé. Dans ce cas, le nom de domaine privé sera résolvable uniquement depuis le VPN ou le VPC interne, permettant de bénéficier de fonctionnalités telles que la mise en cache (caching) pour des API internes.
CloudFront doit toujours être configuré en tant que couche de protection en amont des ressources suivantes :
- ALB
- Function URL
- API Gateway
- S3 (dans le cas où des fichiers doivent être exposés sur internet)
### Interdire le traffic en direct sur le domaine par défaut de AWS
Par mesure de sécurité, le domaine par défaut généré automatiquement par AWS pour chaque ressource ne doit pas permettre un accès direct. Cela permet d’éviter les risques associés à l’exposition non contrôlée d’une ressource.
La solution à mettre en place dépend du type de la ressource :
- CloudFront
  - Règle WAF → TODO

- ALB
  - Pour les ALB publiques → utiliser la CloudFront managed prefix list sur le SG de l’ALB (utiliser le SG existant de la nouvelle infra réseau si éligible)
  - Pour les ALB privés → RAS

- Function URL
  - Soit IAM natif → TODO
  - Soit header spécifique mis par le CloudFront → TODO

- API Gateway
  - TODO

### Au niveau CloudFront
- Private DNS: Utilisation de WAF 
- Public DNS: Utilisation de WAF et Bot Protection

### Au niveau application
> [INFO]cUn endpoint unique ne doit jamais être utilisé à la fois pour les communications client-to-server et server-to-server.
> Dans les cas où les deux types de communication sont nécessaires, créez deux endpoints distincts dédiés à chaque usage.
> [INFO] Les API Keys doivent rester strictement confidentielles et ne jamais être exposées, quelle que soit la situation.  
> Par exemple : une API Key ne doit jamais être intégrée ou packagée côté client (browser), afin d'éviter les risques de fuite.
