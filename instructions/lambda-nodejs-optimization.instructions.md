---
applyTo: "**"
---

# Usage Optimisatimal NodeJS avec Lambda

## Bien maîtriser le contexte d'éxécution partagé
### Principe
Lorsqu’une fonction Lambda est invoquée, AWS crée un environnement d’exécution (sandbox) pour exécuter le code. Cet environnement peut être réutilisé pour plusieurs invocations tant qu’il reste « chaud ».

**Tout code initialisé en dehors du handler est conservé entre les invocations** tant que l’environnement n’est pas détruit
> [INFO] Cela permet de **réutiliser les connexions**, les **objets lourds** ou les **clients réseau** pour **améliorer les performances** et **réduire les coûts**.

> [WARNING] Il ne faut **jamais stocker d’état mutable lié à une requête** (utilisateur, session, etc.) dans ce contexte global, au risque de provoquer des effets de bord non souhaités.
Pour plus d’informations et de détails, consulter la documentation officielle AWS

### Initialisation des ressources à mutualiser
Voici les ressources que l’on peut et doit initialiser en dehors du handler :
- Clients AWS (ex : DynamoDB, S3, SQS, etc.)
- Pools de connexion vers des bases de données (PostgreSQL, MySQL)
- Clients HTTP (Axios, fetch personnalisé…)
- Validateurs (ex : `Ajv`, `Joi`, `Zod`)
- Données statiques en cache (ex : fichiers de config, dictionnaires)
- …
Exemple :
```typescript
import { MyAwesomeService } from '../services/my-awesome-service.ts';

// the service must be initialized "outside" the handler method
const myAwesomeService = new MyAwesomeService(...);

export const handler = async (event) => {
  await myAwesomeService.beAwesome(...);
};
```

#### Recommendations axios
- Créez une instance unique avec `axios.create()`
- Toujours activer le `keepAlive` afin de réutiliser la même connection entre 2 appels
- Configurer correctement l’instance en fonction des requirements (headers, timeout, retries, etc…)
Exemple :
```typescript
import { Agent } from 'https';

import axios, { AxiosInstance } from 'axios';
import axiosRetry, { isNetworkOrIdempotentRequestError } from 'axios-retry';

export const getAxiosInstance = (): AxiosInstance => {
  const axiosInstance = axios.create({
    timeout: 500,
    httpsAgent: new Agent({ keepAlive: true }),
    transitional: { clarifyTimeoutError: true },
    validateStatus: (status: number) => (status >= 200 && status < 300) || status === 404,
    headers: { ... },
  });

  axiosRetry(axiosInstance, {
    retries: 3,
    retryDelay: (retryCount) => retryCount * 100,
    shouldResetTimeout: true,
    retryCondition: (error) => isNetworkOrIdempotentRequestError(error) || error.code === 'ECONNABORTED',
  });

  return axiosInstance;
};
```

```typescript
import { getAxiosInstance } from '../utils/http.ts'
import { MyAwesomeService } from '../services/my-awesome-service.ts';

const axiosInstance = getAxiosInstance();
const myAwesomeService = new MyAwesomeService(axiosInstance);

export const handler = async (event) => {
  await myAwesomeService.beAwesome(...);
};
```

#### Recommendationns aws-sdk
- Instancier une seule fois chaque client (`DynamoDBClient`, `S3Client`, etc…)
- Préciser la région pour éviter que le SDK fasse une sorte de lookup lui même (`AWS_REGION` est disponible automatiquement par AWS)
- Le `keepAlive` est activé par défaut avec `aws-sdk-v3`
Exemple :
```typescript
import { S3Client } from '@aws-sdk/client-s3';

export const getS3Client = (): S3Client => {
  return new S3Client({
    region: process.env.AWS_REGION,
  });
};

```
```typescript
import { getS3Client } from '../utils/s3.ts'
import { MyAwesomeService } from '../services/my-awesome-service.ts';

const s3Client = getS3Client();
const myAwesomeService = new MyAwesomeService(s3Client);

export const handler = async (event) => {
  await myAwesomeService.beAwesome(...);
};
```

## Bundling optimisé pour une taille réduite
### Principe
Optimiser le bundle est **essentiel** pour réduire :
- les temps de déploiement
- les cold starts
- les coûts (moins de bande passante et de stockage)
De manière générale il est recommandé : 
- d'avoir un code bien découpé qui facilite grandement le bundling (ex: 1 handler = 1 fichier, …)
- de choisir avec soin les libs tierces qu’on utilise et l’impact qu’elles peuvent avoir (ex: lodash, zod, …)
### Configuration esbuild
Le bundler `esbuild` est à privilégier de manière générale (sauf exception comme les fragments).
Un exemple de configuration recommandée est disponible dans [aws-cdk-template](https://github.com/groupelacentrale/aws-cdk-template/blob/83cf181edf5c46697e6d2f4c2f2183973168599a/aws/cdk/lib/app/helpers/function-utils.ts#L33-L54).

