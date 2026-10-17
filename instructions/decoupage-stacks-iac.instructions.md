---
applyTo: "**"
---

# Decoupage des stacks
Actuellement à GLC les équipes sont totalement autonome dans la création de leurs stacks et dans la façon de les organiser en terme de répartitions des ressources. 

## Problème
La problématique que cela apporte c’est qu’en passant d’une équipe à une autre, il est difficile de s’approprier une stack et voire même difficile de la maintenir dans le temps.
Dans un deuxième temps, nous avons aussi constaté des difficultés à la montée en compétence sur CDK ayant pour effet de pousser les gens à créer une stack par type de ressource ou d’autres paradigmes qui ne semblent pas logiques, chose que nous souhaitons éviter.
## Solution apportée
Afin d’aligner tout le monde, un exemple a été produit afin de donner une guideline unique permettant de copier/coller la structure sans se poser de questions. Vous pouvez retrouver cet exemple dans le repository Github . 
La répartition des ressources se fait selon 3 axes : d’un côté les ressources stateless, d’un côté les ressources stateful et pour finir les pipelines. 
> [NOTE] Les alarmes CloudWatch vont être la seule exception à ce paradigme : on préférera mettre en place les alarmes au plus près des ressources concernées.
## Création d’une stack pour les éléments dits `stateless`
> [INFO] Les ressources `stateless` sont les ressources qui ne concernent pas le stockage, tels que les fonctions Lambda, les queues SQS, etc …
Dans cette stack, on y mettra tout ce qui n’est pas une unité de stockage à proprement parler ni la pipeline. On y retrouvera donc : 
- Les fonctions Lambdas
- Les rôles IAM
- Les queues SQS et les topics SNS
- Les StepFunctions
- etc … (la liste n’est pas exhaustive)
Le fait de mettre tous ces éléments dans la même stack n’empêche pas de créer une séparation en utilisant la puissance de CDK : vous pouvez utiliser une méthode afin de créer vos fonctions Lambdas accompagnées de leurs alarmes et faire des références entre vos ressources.
## Création d’une stack pour les éléments dits `stateful`
> [INFO] Les ressources `stateful` sont les ressources qui représentent une unité de stockage, telles que les tables DynamoDB, les buckets S3, etc …
Dans cette stack on viendra mettre tout ce qui représente une unité de stockage. On y retrouvera donc : 
- Les tables Dynamo
- Les buckets S3
- Les disques EFS
- Les bases Aurora
- Les bases RDS
- Les clusters OpenSearch
- etc … (la liste n’est pas exhaustive)
## Création d’une stack pour les pipelines
Et pour finir, une troisième stack viendra enrichir votre application : la stack de pipeline. Celle-ci contiendra tout simplement les pipelines de CI/CD de votre application.
