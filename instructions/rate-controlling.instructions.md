---
applyTo: "**"
---

# Rate Controlling
# Introduction
Dans le cadre de usage des service partners ou communications entre des services interne au seine de GLC, il y a eu certains incidents qui ont eu des impacts remarquable et important. Après des analyses, nous avons identifié des problèmes designs et couplage des services et ces elements sont les motivations de fournir ce guideline. 
Le major categories présentés sont :
- Asynchronous
- Synchronous
- Monitoring / Alarming
# Historiques des incidents recents
Nous avions subit plusieurs fois et introduit des vrais regressions coté downstream soit interne, ou externe
- **External**: DocuSign
- **Internal**: Search Notifications
# Etat de lieu Systems Externes
Une etude est réalisée afin de preparer une visions sur les quota et limits des systems externe fin en février 2025.
> [WARNING] Cette Documentation est par un besoin d’analysis lié aux stacks communiquant avec les system principalement externe, les recommendations dans cette documentation auront un impact sur la vitesse de traitement et sont afin de controller le taux de traitement par réduire la capacité realtime. 

# Typologie Asynchronous
La communication asynchronous oblige des considerations a prendre en compte étant coté producer ou coté consommateur. Les cas de design connue chez GLC sont:
- DynamoDB Stream
- Kinesis Streams
- Queue SQS
- Topic SNS
- EventBridge Bus
## **Recommendations General**
| Pattern  | Description  |
| --- | --- |
| Back Pressure Prevention | Garantira l'équilibre de charges coté consommateur par les patterns equivalent SNS/SQS (Fanout).<br> <blockquote>Tous les integrations ayant des Limitations/Quotas ( BDD, OpenSearch, ou des Apis) doivent être faite avec un Queue (SQS) comme une couche intermediate pour équilibrage.</blockquote> |
| Lambda Trigger | Event Source Mapping: <br> 1. **Batching**: Utilisation de Batching afin d’avoir le records lié à chaque entité ensemble.<br>**Batch Time Window**: Afin de retarder l’invocation de lambda et attend pour plus de chance de recevoir les records lié à meme entité ensemble. <br> > <blockquote>[NOTE] Le Batch window n’est pas à 100% effective mais le service lambda l’adapte selon le service source de trigger et une verification si le retarde vaut le coup ou pas à un moment donnée. mais le max de temps d’attente sera le time window configuré.</blockquote> Retry & DLQ: Pour mieux gérer les messages en erreur afin de: <br> 1. Ne pas perdre les messages <br> 2.Ne pas bloquer les messages suivent à cause d’un message en erreur permanance (poison pile) |
| Events Distribution | 1. **Distribution des Events via Broker**: Informer les DownStreams via un broker (SNS, EventBridge, Kinesis) <br> 2. **Synthétiser les Records liés**: Distribuer l'état final de processing à un moment donnée. (ici ou là ) <br> A) **Fusion**: Fusionner/Grouper afin de produire un état final par entité à distribuer.<br>  B) **Abandonner Records Inutiles**: Abandonner certains records inutiles et privilégier l'état plus recent de l’entité <br> **Exemple A**: UPDATE suivie par un DELETE en meme temps doit générer un état final en tant que DELETE sans intérêt de propager l’état UPDATE.<br> **Exemple B**: Une CREATION suit par un UPDATE reçu en meme temps doit distribuer un événement CREATION avec état final qui represent fusion des deux records où le UPDATE ( plus recent ) surchargera des info de record CREATION. |
> [NOTE] Dans cette partie nous allons presenter des patterns lié aux designs architecture connue au seine de l'entreprise.
## SQS/ Load Leveling
Cette pattern a deux cas d’implementation Standard et FIFO qui vont être explorer  dans cette partie
- **ReceiveMessageWaitTime**: Augmentez afin que SQS puisse solliciter toutes les nodes storage des message de son coté. This will optimize the integration with SQS distributed design (Long Polling)

### Rate Controlling Standard
- **Concurrency Limit: **Mettez une valeur faible qui correspond à usecase
- **BatchSize: **Mettez une valeur qui permettra d’avoir plus de message dans une invocation de la lambda.
- **MaxBatchingWindow: **Raffinez et configurez une valeur qui permettra au service lambda de cumuler plus de messages pour arriver mieux au batchSize configuré
L’exemple ci-dessous represent une configuration de batching avec une attente de 30 seconds coté service lambda afin de récupérer plus des messages par plusieurs interaction avec SQS avant invocation de la lambda
```typescript
   const queue = new Queue(this, 'Queue', {
      receiveMessageWaitTime: Duration.seconds(20),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: new Queue(this, 'DeadLetterQueue')
      }
    });

    lambdaFunction.addEventSource(new SqsEventSource(queue, {
      batchSize: 10,
      maxBatchingWindow: Duration.seconds(60),
      maxConcurrency: 2,
    }));
```

### **Rate Controlling FIFO**
- **BatchSize**: Mettez une valeur qui permettra d’avoir plus de message dans une invocation de la lambda.
> [INFO] **MessageGroupId:** Le SQS Fifo guarantee distribution en ordre  des messages lié et envoie les messages lié strictement à une seul invocation de la lambda, ceci veut dire que les messages lié à un messageGroupId seront present dans une seul invocation de lambda à un instant donnée.

```typescript
    const queue = new Queue(this, 'Queue', {
      receiveMessageWaitTime: Duration.seconds(20),
      fifo: true,
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: new Queue(this, 'DeadLetterQueue', { fifo: true })
      }
    });

    lambdaFunction.addEventSource(new SqsEventSource(queue, {
      batchSize: 10,
    }));
``` 

## Streams
Les configurations de Dynamodb streams et Kinesis sont relativement pareil 
### Rate Controlling Streams
- **BatchSize**: Mettez une valeur qui permettra d’avoir plus de message dans une invocation de la lambda.
- **MaxBatchingWindow**: Raffinez et configurez une valeur qui permettra au service lambda de cumuler plus de messages pour arriver mieux au batchSize configuré
- **BisectBatchOnError**: Mettez en place pour permettre un decoupage automatique des batch en error qui permettra de exclure les records en cause de failure et avoir ne pas impacter les records traitable.
- **ParallelizationFactor**: Configurez un factor assez bas afin de réduire la concurrency.
> [WARNING] Dans usage **Bisect**, ne mettez pas un batch size elévé. mais aussi considerez application d’un Partial Failure mechanism ( qui sollicite le changement de paradigm de code ) afin de mieux gérer les errors.
> Traitez les records en mode sequential et pas parallel pour guarantee de l’ordre des records.

```typescript
   const stream = new Stream(this, 'Queue', {
      streamMode: StreamMode.ON_DEMAND,
      removalPolicy: RemovalPolicy.DESTROY
    });

    lambdaFunction.addEventSource(new KinesisEventSource(stream, {
      startingPosition: StartingPosition.LATEST,
      batchSize: 10,
      maxBatchingWindow: Duration.seconds(30),
      bisectBatchOnError: true,
      retryAttempts: 3,
      maxRecordAge: Duration.minutes(15),
      parallelizationFactor: 1,
      onFailure: new SqsDlq(new Queue(this, 'DLQ'))
    }));
```

## SNS/EventBridge (FanOut)
Les services SNS et EventBridge permettront un design Fanout avec plusieurs consommateurs (abonnés). SNS/EB, ces services envoient un seul message à la fois meme si le model de event present un array de records ( Records[] ) donc ils n'y aura pas de possibilité de traitement raffiné par lots ( batch ) et config batching personnalisé qui derive un niveau plus élevé d'exécutions concurrentes des lambdas et dont un load sans possibilité de control.  (ref: [ici](https://aws.amazon.com/sns/faqs/) )
### Rate Controlling Fanout
- **Reserved Concurrency**: Dans les cas integration direct avec SNS ou Eventbridge la solution pour limiter impact en downstream est appliquer un reserved concurrency.
- **OnFailure Destination**: Intégrer un DLQ , le comportement par défaut est 3 tentatives avec intervalles default entre chaque retry d'invocation ( non modifiable )
  - **1er Retry**: 1 minute.
  - **2em Retry**: 2 minute.

- **Load Leveling**: Utilisez un SQS comme une couche intermédiaire qui facilite l'écilibrage de charge.
> [WARNING] Amazon SNS FIFO ne permet pas avoit un trigger lambda et l’integration se fait par un intermédiaire SQS FIFO qui guarantira l’ordre des messages. (plus d’info: [ici](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/1061978149/Rate+Controlling#FIFO) )

```typescript
   const lambdaFunction = new NodejsFunction(this, 'LambdaZipFunction', {
      reservedConcurrentExecutions: 1,
      ...
      },
    });

    const topic = new Topic(this, 'Topic');

    lambdaFunction.addEventSource(new SnsEventSource(topic, {
      deadLetterQueue: new Queue(this, 'DeadLetterQueue'),
    }));
```

# Typologie Synchronous 
Dans un process synchronous les considerations a prendre en compte sont dans different couches de communications qui permettent de réduire l’impacte en collaboration.
les Couches identifié sont:
- Server Side
- Edge Side
- Client Side
## Server Side
La couche server est responsable à fournir des elements necessaire qui permettra partager l'état de communication avec les couche edge side et client side (browser).
  
- **Monitoring** : Le serveur doit surveiller les seuils et configurer des alarmes pour détecter les problèmes. ca permettra d’observer les changements de tendance et avoir des alertes afin de mieux gérer la situation.
- **Response Code** : Le serveur, en tant que propriétaire des limites et des contraintes du système externe, doit fournir une réponses avec le statut HTTP correct, tel que 429 (TooManyRequests), et les en-têtes correspondants comme faite par github, tels que :
  - **X-Ratelimit-Reset** : le temps de remise à 0 des contraintes de limite.
  - **X-Ratelimit-Remaining** : Nombre de requêtes restantes dans la fenêtre temporelle.
  - **X-Retry-Interval** : Intervalle de temps recommandé entre les tentatives exponentielle (peut être influencé par le taux de backoff).
  - **X-Retry-Backoff**: Taux de backoff exponentiel recommandé à multiplier par l'intervalle.

- **Failing Fast**: La réponse au consommateur sera « Trop de requêtes » si le taux réel dépasse le seuil configuré, le serveur doit fournir une réponse rapid sans solliciter le service externe si le threshold est atteint.
- **Async when Possible**: afin de simplifier la continuité, dès que possible, basculez un process synchronous à un process asynchronous.

## Edge Side
Edge est une couche intermédiaire entre client ( connaissance et maîtrise d’état 0 ) et le server ( connaissance et maîtrise  d'état 100%) , cette couche permettra de réduire le taux des appels aux origin afin de réduire le besoin de RateControlling.
- **WAF:** Mise en place des régles WAF pour reduire la possibilité des attaques qui vont impacter les engagement vis a vis service externe.
- **Caching**: Mettez en place un caching, cette option implique souvent  transition des request POST,PUT vers les requests GET qui seront facile a cacher.
- **Request Collapsing**: C’est un mechanism des CDN qui exists aussi coté CloudFront. Cette mechansime permettra d'écquilibrer la charge au niveau cloudfront en retardant les requests simultané et solicité l’origin que par une seul requête, les requêtes  en attentes vont retourné la réponse fournit par la premiere requête.
> [WARNING] Request Collapsing ne sera pas applicable si la transfère des cookies sont configurés au niveau behavior.
## Client Side
Les recommendations coté client sont afin de mieux gérer l’impact de utilisateur mais aussi améliorer le niveau satisfaction de utilisateur final et la possibilité de continuité de service
- **Exponential Backoff**: Coté client les requêtes doit suivre les indicateur de server dans la header de response http lié au Ratelimiting.
- **Graceful Degradation**: coté client, un comportement dégradé de la fonctionnalité doit être prévu si serveur ne sera pas en mesure de répondre.
