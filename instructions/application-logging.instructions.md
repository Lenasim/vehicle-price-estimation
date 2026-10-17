---
applyTo: "**"
---

# Logging des applications
Les applicatifs ont besoin de pouvoir envoyer les logs dans EFK et consulter le dashboard ou la partie Discovery de Kibana pour observer les environnements applicatifs. EFK est le system centrale des logs et events BI qui est peut etre alimenté par des types wolkloads variés. 
## Actuellement
Actuellement les application communique directement avec [[**logs-bus**](https://jira-glc.atlassian.net/wiki/x/KRPU)], ce process représente quelque problem comme indiqué ci-dessous:
- Couplage de phase Instrumentation avec phase runtime process
- Nous avons besoins un “await“ pour avoir un log simple
- Ajoute de latence dans process business
- Coté lib-logging avoir un try - catch qui bouffe l’error d'envoie vers log-bus si arrive
## Motivation
Si possible avoir** **une instrumentation de process pour Logging qui sera géré:
- En Background Process
- Sans  impacter le process principale  en cas miss fonctionnalité
- Avoir un Execution LifeCycle isolé au max possible de process business.
## Changement
La nouvelle mechanisme porte les étapes suivants:
- Alimentation de Logs-bus via un sidecar pattern un process totalement séparé
- Permettre d’Activation / Désactivation par use cas ( avoir ou ne pas avoir )
- Permettre de Mise en place buffering dans le process envoie logs
- S’approcher aux Standards que big Observability systems font
- Considérations du Lambda NodeJS >= 18, 20, 22 actuellement
- Avoir indépendance et pas besoin de CloudWatch ( histoire de cout )
## Logging
**Logging: (Doc : **[Doc Lib Logging](https://github.com/groupelacentrale/libs/tree/master/packages/libs-logging) **)** : Lib logging GLC permettra de sanitiser le payload de Logs et ajoute certains meta-données à chaque log. Ce process n’a aucun dependance et simplement fera un log classic console qui va Behind The Scene interoger le **stdout**/**stderr**. ca reste un process lightweight dans un point de vu dureté de dependence et couplage fort.

> [NOTE] Les versions precedentes de Lib-Logging ( inferieur V4.0.0 ) communique directement avec Kinesis de Log Bus en utilisant la methode `flash()`, upgrade vers les versions 4.X.X vas completement decorélé cette envoie des logs et aura comme consequence le manque des logs dans EFK sauf si les etapes de [Log Forwarding](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/444432395/Application+Logging#Log-Forwarding-and-Aggregation) sont correctement considérée

Pour cela un upgrade simple vers la latest version de lib logging vous permettra de avoir un code qui sera agnostic de l’infrastructure et avoir les logs dans cloudwatch. utilisation de cette lib est souhaité fortement pour les raison suivant:
- Control de tail de payload des logs
- Ajout des meta donnée nécessaire
- Ajout de log_type correspondant de log ou event
- Control de Log level configuré

> [WARNING] Si vous ne souhaitez pas enregistrer les logs dans cloudwatch la presence un explicite DENY pour les actions policy de logs:* sera suffisant.

### **Les notes important lors lors de utilisation de cloudwatch logs:**
- Consideration d’un retention pour les logs, la recommendation basique et d’avoir une retention par environment soit Dev, Test et Production.
- Ne pas logger les info sensible et payloads large
- Au seine de GLC nous privilegons usage de EFK pour l’observation des logs sauf le cas exceptionnel ( à voir avec CSA ).
- Dans les cas globaux avoir un policy deny pour les actions de service **logs** sera necessaire

### Log Forwarding and Aggregation
Il y a trois uscenarios identifié chez GLC qui seront explorer dans ce document.
- Lambda
- Fargate
- EC2
### Lambda
Le scenario principalement utilisé dans l’ecosysteme GLC est le service lambda, Pour les application ayant les besoin de lambda integration d’un service sidecar ( process isolé ) qui permettra d’envoie les logs dans EFK sans impact sur le code application, le Extension de lambda est preconisé comme une solution adaptée.
#### **How it works**
- The Caller envoie la request à Lambda
- La lambda Traite la demande et renvoie la réponse
- l’Api Telemetry envoie les logs applications
- Extension envoie le Buffer reçu et cumulé à Log-Bus
- Durant l'invocation, extensions externes sont exécutées en parallel de process execution de function. ils continue aussi l’execution après la fin d’execution de function lambda. ( [AWS Documentation](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-extensions-api.html)  Invoke Phase)
- dans cette premiere version, Buffering est configuré par les limitations Kinesis Data Stream donc ca peut introduire une latence d’alimentation des logs ( on regarde pour le optimiser )
#### **Utilisation**
**Alimentation des logs dans EFK: (Doc: **[Docs GLC Extension Logging ](https://github.com/groupelacentrale/glc-lambda-extensions/blob/prod/docs/kinesis-telemetry-api-extension/README.md)  ** ) **Alimentation des logs dans EFK , c’est fait via Une extension de lambda, cette extension permettra de envoyer les logs vers EFK en mode isolé et dans un process qui est indépendant de cycle de vie de function lambda. pour que extension opère correctement , il n a pas d besoin d’avoir les logs dans cloudwatch **loggroup **donc ca va marcher aussi lors d’avoir un explicit DENY en **logs.** 
The [Docs GLC Extension Logging](https://github.com/groupelacentrale/glc-lambda-extensions/blob/prod/docs/kinesis-telemetry-api-extension/README.md)  represnts differents scenarios of lambda usage such as Zip Package, Custom Ilmage or Web Adapter.
> [WARNING] Sans avoir cette extension aucun log sera forwarder vers EFK mais les logs seront present dans le cloudwatch sauf la presence un explicite DENY pour les actions policy de logs:* .

Usage Example avec AWS CDK for Lambda Zip Package:
```typescript
const extensionArn = StringParameter.fromStringParameterName(
    this, 'extensionId', `/${env}/extension/telemetry/kinesis/extension/arn`).stringValue;

  const managedPolicyName = StringParameter.fromStringParameterName(
    this, 'policyName', `/${env}/extension/telemetry/kinesis/runtime/policy/arn`).stringValue;

  const role = new Role(this, 'function-with-extension-role', {
      assumedBy: new cdk.aws_iam.ServicePrincipal('lambda.amazonaws.com')
  });

  functionRole.addManagedPolicy(
    ManagedPolicy.fromManagedPolicyArn(this, 'managed-policy', managedPolicyName));

  new Function(this, 'function-with-telemetry-extension', {
      runtime: cdk.aws_lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      layers: [ 
        LayerVersion.fromLayerVersionArn(this, 'ExtensionArn', extensionArn) 
      ],
      environment: {
        'STAGE': props.tags.Env,
        'LOG_INDEX': 'example'
      },
      role: functionRole,
      code: Code.fromAsset(path.join(__dirname, 'src/test-function-with-telemetry')),
    })

```

Example of Lambda Custom Image:
```dockerfile
FROM <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/kinesis-telemetry-api-extension-<ENV>:latest AS extensions
FROM public.ecr.aws/lambda/nodejs:22

WORKDIR ${LAMBDA_TASK_ROOT}

COPY dist/* ./
COPY --from=extensions ./opt/ /opt/

CMD ["index.handler"]
```

Example of Lambda Web Adapter:
```dockerfile
FROM <ACCOUNT_ID>.dkr.ecr.<REGION>>.amazonaws.com/kinesis-telemetry-api-extension-dev:latest AS extensions
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.9.0-aarch64 AS webadapter
FROM public.ecr.aws/docker/library/node:22.13.1-slim

WORKDIR ${LAMBDA_TASK_ROOT}

COPY dist/* ./
COPY --from=extensions ./opt/ /opt/
COPY --from=webadapter /lambda-adapter /opt/extensions/lambda-adapter

CMD ["node", "index.js"]
```

### Fargate
Dans le cas usage de service ECS Fargate, l’option d’avoir un process sidecar isolé et sans impact sur le process application peut etre obtenir avec le LogDriver `Firelens` qui est basé sur `FluentBit`. 
Voici les étapes pour y mettre en place :
- Fichiers config `FluentBit` permettra d’appliquer des configurations comme filtering , etc. There are two configuration files to prepare
> [NOTE] Nous recommandons de conserver le même nommage, uniquement pour des raisons de gouvernance et de maintenabilité.

The `parsers.conf`  
```yaml
// parsers.conf file
[PARSER]
    Name    log_json
    Format  json
```
The `container.conf` file 
```yaml
// container.conf file
[SERVICE]
    Parsers_File    parsers.conf

[FILTER]
    Name            parser
    Match           *
    Key_Name        log
    Parser          log_json

[FILTER]
    Name            grep
    Match           *
    Regex           log_index example-app
```

Un fichier `Dockerfile` dédié pour process `Firelens` doit etre crée à partir de image fournie par AWS

```docker
FROM amazon/aws-for-fluent-bit:latest

ADD container.conf /container.conf
ADD parsers.conf /parsers.conf
```

AWS CDK & IaC sont réalisable en ajoutant un container supplementaire à taskdefinition, aws cdk fournie déjà la method helper pour ajouter le container firelens
> [NOTE] Le conteneur `Firelens` écrit les logs du conteneur d'applications dans le LogBus, mais seul, il utilise les Cloudwatch pour ses propres logs.

```typescript
   const jobDefinition = new FargateTaskDefinition(this, 'JobDefinition', {
   });

   jobDefinition.addContainer('Container', {
      image: ContainerImage.fromAsset(join(process.cwd(), './myapp')),
      logging: LogDrivers.firelens({
        options: {
          Name: 'kinesis_streams',
          region,
          stream: props.streamName,
        },
      }),
    });

    jobDefinition.addFirelensLogRouter('LoggingContainer', {
      image: ContainerImage.fromAsset(join(process.cwd(), './fluent-bit')),
      logging: LogDrivers.awsLogs({
        streamPrefix: 'logging',
        logGroup: new LogGroup(this, 'FireLensLogGroup', {
          logGroupName: `/ecs/${props.tags.App}`,
          retention: RetentionDays.ONE_DAY,
          removalPolicy: RemovalPolicy.DESTROY,
        }),
      }),
      environment: { FLB_LOG_LEVEL: 'info' },
      firelensConfig: {
        type: FirelensLogRouterType.FLUENTBIT,
        options: {
          configFileType: FirelensConfigFileType.FILE,
          configFileValue: '/container.conf',
        },
      },
    });

```

Task Role: Le Task doit avoir les droits d’interagir avec Log Bus donc il faut attaché le managed policy de LogBus à TaskRole.
[NOTE] Pas besoin d'attacher le ManagedPolicy à TaskExecutionRole , seulement TaskRole a besoin.

```typescript
  const managedPolicyArn = StringParameter.fromStringParameterName(
    this, 'policyName', `/${env}/extension/telemetry/kinesis/runtime/policy/arn`).stringValue;

  const jobTaskRole = new Role(this, 'JobTaskRole', {
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        ManagedPolicy.fromManagedPolicyArn(this, 'TaskRoleManagedPolicy', managedPolicyArn),
      ],
  });

  const jobTaskExecutionRole = new Role(this, 'JobTaskExecutionRole', {
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
  });

```
