---
applyTo: "**"
---

# Chiffrement des Données
Assurer que toutes les données stockées dans AWS sont systématiquement chiffrées à l'aide d'une clé KMS dédiée, afin de garantir la conformité avec les politiques de sécurité et les exigences réglementaires du Groupe La Centrale.
## Règles générales
1. **Gestion centralisée des clés KMS**
Les clés KMS sont stockées dans un compte AWS dédié (**security-keys)** et sont partagées de manière contrôlée avec d'autres comptes de l'organisation. Chaque compte dispose de son propre ensemble de clés KMS, spécifiquement allouées pour différents types de ressources dédiées à ce compte.
2. **Isolation des clés entre les comptes**
Une clé KMS associée à un **compte A** ne peut pas être utilisée par un **compte B**, sauf dans des cas d'exception clairement définis. Cette politique garantit une isolation stricte des données et renforce la sécurité intercomptes.
3. **Disponibilité régionale des clés KMS**
Les clés KMS sont déployées dans les régions **eu-west-1** et **eu-west-3** pour des raisons de sécurité et de disponibilité. Il est impératif qu'une ressource située dans une région donnée utilise uniquement une clé KMS disponible dans la même région, afin d'assurer une conformité aux meilleures pratiques en matière de sécurité et de réduire les risques de latence et de dépendances inter-régions.
4. **Référencement des clés KMS via Parameter Store**
Étant donné que les **ARNs des clés KMS** ne sont pas prédictibles, des paramètres spécifiques ont été créés dans **AWS Parameter Store** et sont également partagés avec les autres comptes. Pour référencer une clé KMS dans vos configurations ou vos stacks, il est essentiel d'utiliser l'ARN correspondant au type de ressource que vous souhaitez créer, en vous basant sur les paramètres stockés.
## Clés par défaut
> [INFO] Uniquement pour les comptes `corp`, `dev`, `test` et `prod`.

| Type de ressource | ARNs des parameters à utiliser |
| --- | --- |
| DynamoDB | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/dynamodb/arn` |
| EBS (pour EC2 & OpenSearch) | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/ebs/arn` |
| EFS | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/efs/arn` |
| Neptune | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/neptune/arn` |
| RDS | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/rds/arn` |
| S3 | `arn:aws:ssm:${region}:003793130418:parameter/${env}/security-keys/kms/default/s3/arn` |

> [WARNING] Si vous rencontrez une erreur avec CDK de type “stringParameterArn cannot be an unresolved token“, vérifiez que vous avez bien ajouté la ligne suivante dans la création de la stack :
```typescript
new MyStack(app, '...', {
  ...
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION },
  ...
});
```
> [WARNING] Si vous rencontrez l’erreur “Env tag is missing on the stack”, notamment dans les NestedStack, le node enfant créé par le construct kms n’hérite pas des valeurs instanciées par “this”. Il faut explicitement passer “scope” pour résoudre cette erreur:
```typescript
const encryptionKey = DefaultEncryptionKey.fromResourceType(scope, {
    resourceType: 's3',
});
```
### Usage DynamoDB
```typescript
import { DefaultEncryptionKey } from '@groupelacentrale/libs-cdk';
import { Table, TableEncryption } from 'aws-cdk-lib/aws-dynamodb';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';

// ...

const encryptionKey = DefaultEncryptionKey.fromResourceType(this, {
  resourceType: 'dynamodb',
});

new Table(this, 'MyTable', {
  // ...
  encryption: TableEncryption.CUSTOMER_MANAGED,
  encryptionKey,
});

const myFunction = new NodejsFunction(this, 'MyFunction', {
  // ...
});
encryptionKey.grantEncryptDecrypt(myFunction);
```
### Usage OpenSearch
```typescript
import { DefaultEncryptionKey } from '@groupelacentrale/libs-cdk';
import { Domain } from 'aws-cdk-lib/aws-opensearchservice';

// ...

const encryptionKey = DefaultEncryptionKey.fromResourceType(this, {
  resourceType: 'ebs',
});

new Domain(this, 'MyDomain', {
  // ...
  encryptionAtRest: {
    enabled: true,
    kmsKey: encryptionKey,
  },
});
```
### Usage RDS
```typescript
import { DefaultEncryptionKey } from '@groupelacentrale/libs-cdk';
import { DatabaseInstance, DatabaseCluster } from 'aws-cdk-lib/aws-rds';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';

// ...

const encryptionKey = DefaultEncryptionKey.fromResourceType(this, {
  resourceType: 'rds',
});

new DatabaseInstance(this, 'MyInstance', {
  // ...
  storageEncrypted: true,
  storageEncryptionKey: encryptionKey,
});

new DatabaseCluster(this, 'MyCluster', {
  // ...
  storageEncrypted: true,
  storageEncryptionKey: encryptionKey,
});
```
### Usage S3
> [WARNING] Il est obligatoire d’activer la propriété “BucketKeyEnabled” ( ) sur les buckets S3, au risque d’exploser les coûts KMS.
> Voir  pour plus d’informations.
```typescript
import { DefaultEncryptionKey } from '@groupelacentrale/libs-cdk';
import { Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';

// ...

const encryptionKey = DefaultEncryptionKey.fromResourceType(this, {
  resourceType: 's3',
});

new Bucket(this, 'MyBucket', {
  // ...
  bucketKeyEnabled: true,
  encryption: BucketEncryption.KMS,
  encryptionKey,
});

const myFunction = new NodejsFunction(this, 'MyFunction', {
  // ...
});
encryptionKey.grantEncryptDecrypt(myFunction);
```
