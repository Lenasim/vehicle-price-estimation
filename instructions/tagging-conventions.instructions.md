---
applyTo: "**"
---

## Principe
Les tags servent à mieux identifier et regrouper les ressources pour ensuite :
- suivre les coûts de manière efficace
- donner les autorisations aux équipes sur leurs ressources
## Liste des tags
> [WARNING] <br> - Les Keys doivent commencer par une majuscule. <br> - Les Values sont toujours en minuscule séparées par des tirets.<br> - Sur le compte de dev, si un de ces tags est manquant sur une instance EC2, elle sera détruite.

| Key | Description | Values | Obligatoire | Questions à se poser |
| --- | --- | --- | --- | --- |
| Env | Environnement | Liste fixe dev/test/prod/corp/orga/data/gov/.bkp/logs/seckeys/net/shrd/sdp/ldp/lsbox | YES |   |
| Bloc | Bloc métier | Liste fixe lcedidatasharedpncarait | YES | Quel est le domaine (bounded context) qui utilise la ressource ? Quel site ? Quelle grande fonction metier ? Par exemple la cote est utilisé par LC et MVC donc le bloc est SHARED (pas DATA car l'utilisateur n'est pas le marketing interne) |
| App | Application |   | YES | Quel est mon applicatif métier / mon service / mon système ? 1 App = 1 fiche architecture |
| Comp | Composant | Exemples: api, front, backoffice, service, cicd, etc | | Quel est mon sous-ensemble de traitements cohérents ? (Exemple pour l'App : Recherche, Comp : API → API de recherche pouvant être appelée par le front recherche ou les mobiles, etc... |
| Team | Equipe owner de la ressource | Liste fixe capsulecaradisiacclassifiedcontent-servicesdataguardiansico-sourcingoperationspricingpromoneuve (legacy)sales-enablersearchselluser-contact-experiencevehicle-hub | YES |   |
| IsInfraAsCode | Type de gestion de la ressource | Liste fixe cloudformationcdkserverlessscripthuman | YES |   |
| NonBusinessHoursState | Permet de faire des économies en arrêtant certains systèmes la nuit et le week-end | Liste fixe stopped / stopped-nlc / stopped-bcarunningterminatedshutdown (never restarted)automatically-stopped | RDS: stopped: arrêt à 20h, démarrage à 6hshutdown : arrêté tous les soirs à 20h, à redémarrer manuellementautomatically-stopped : le service s'éteint tout seul (pex aurora serverless) EC2/ASG: terminated: après 20h, l'instance est supprimée et l'asg est suspendu afin de ne pas lancer de nouvelles instances. A 7h, L'asg est ré-activé et les instances sont relancées par ce dernierstopped: après 20h, l'instance est arrêtée. A 7h, on démarre les instances arrêtées si InstanceType < 2xlarge. (instances sans asg)shutdown: après 20h, éteindre l'instance EC2 sans la redémarrer le lendemain et suspendre l'asg s'il existe. Pour redémarrer l'instance (On demand) utiliser ce script ou le faire via la console Lambda stopped: se fait throttle à 20h et se fait unthrottle le matin à 7h (utile pour les lambdas de mises à jour de systèmes qui sont arrêtés) Notebook sagemaker shutdown: se fait arrêter le soir à 20h, à redémarrer manuellement |   |
| BackupLevel | Niveau de backup attendu pour la ressource | Niveaux de backups définis dans Backup AWS nonecritical | :check_mark:(uniquement DynamoDB, EBS, EFS, RDS et S3) | Est-ce que la donnée doit être rétablie dans un scénario de PRA ? Est-ce que la donnée est reconstructible à partir d'une autre source en cas de perte ? Quel est le coût/effort de reconstruction ? |
| BackupFrequency | Fréquence spécifique de backup | Liste fixe 12h | YES | Est-ce le RPO est inférieur à 24h ? |
#
