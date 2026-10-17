---
applyTo: "**"
---

# Backup
Chaque resource stockages comme Dynamodb, RDS, S3 , et etc doit porter un tag BackupLevel.

## Details et Particulrités  
Certains services ont besoin des configurations specifique pour que le process Backup et restore pauvent fonctionner correctement. 
### Application de Tag
Le tag BackupLevel doit être renseigné sur toutes les ressources éligibles.

```typescript
import { Tags } from 'aws-cdk-lib';

// ...

Tags.of(resource).add('BackupLevel', 'none');
Tags.of(resource).add('BackupLevel', 'critical');
```

### Spécificités DynamoDB
Le PITR doit être activé sur la table.
```typescript
import { Table } from 'aws-cdk-lib/aws-dynamodb';

// ...

const table = new Table(this, 'MyTable', {
  // ...
  pointInTimeRecovery: true,
});
```
### Spécificités S3
Le versioning doit être activé sur le bucket. Il est fortement recommandé de mettre en place une lifecycle rule afin de ne pas garder les versions non courantes.
```typescript
import { Duration } from 'aws-cdk-lib';
import { Bucket } from 'aws-cdk-lib/aws-s3';

const bucket = new Bucket(this, 'MyBucket', {
  // ...
  versioned: true,
  lifecycleRules: [
    {
      enabled: true,
      id: 'ExpireNonCurrentVersions',
      expiredObjectDeleteMarker: true,
      noncurrentVersionExpiration: Duration.days(1),
    },
  ],
});
```
