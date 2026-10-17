---
applyTo: "**"
---

# Gestion des dependences 
Une grand nombre des libs partagées utilisées au sein de GLC sont majoritairement des libs internes. Elles sont utilisées afin de simplifier l’adoption des nouvelles guidelines et les évolutions concernées en rendant la complexité liée aux infrastructures, utils et services abstraite.
A LaCentrale il existe différentes catégories de dépendances (plus d’info [ici](https://jira-glc.atlassian.net/wiki/spaces/ARCHI/pages/935297057/Dependencies+Update+Using+Dependabot#Dependencies-Types)  ) :
- Packages (CDK constructs, SDKs, Dev Tools )
- Docker Images
- GitHub Actions
Malgré l’intêret de simplifier la phase onboarding et usage initial,  à long terme, cela conduit à la frustration avec des versions et dependences obsolétes. ce qui nous ramène à l'état actuel d’avoir des versions très ancient qui datent des année ( 2-3 ou 4 ans )
# Using Dependabot
> [NOTE] Dependabot est complètement gratuit ne consomme pas “Github Actions Minute Usage”, Mais ca peut être un process long et pour cela cette documentation fournit des mitigation et recommendations pour améliorer cette mise en place.
## Npm dependencies **[SUBMITTED]**
La configuration dependabot suivent represent l’exemple le plus adapté à notre usage et culture interne et couvre les packages managers npom , pnpm et yarn. ( plus d'info [ici](https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories) )
> [INFO] La raison d’avoir l’element `target-branch`dans deuxime config et pas la premiere est la façon que github dependabot valide les configurations par un validation sémantique . ceci permettra de bypasser la detection de la configuration dupliqué.

```yaml
version: 2

registries:
  npm-github:
    type: npm-registry
    url: https://npm.pkg.github.com
    token: ${{secrets.GLC_OPERATIONS_READ_PACKAGES_DEPENDABOT}}

updates:
  - package-ecosystem: 'npm'
    open-pull-requests-limit: 2
    directories: 
      - '/'
    schedule:
      interval: 'weekly'
    allow:
      - dependency-type: "direct"
    ignore:
      - dependency-name: "*"
        update-types: [ "version-update:semver-major" ]
    groups:
      prod-dependencies:
        dependency-type: 'production'
        update-types:
          - "minor"
          - "patch"
      dev-dependencies:
        dependency-type: 'development'
        update-types:
          - "minor"
          - "patch"
    commit-message:
      prefix: "chore"
      include: "scope"

  - package-ecosystem: "npm"
    open-pull-requests-limit: 2
    directories: 
      - "/"
    target-branch: "main"
    schedule:
      interval: "monthly"
    allow:
      - dependency-type: "direct"
    ignore:
      - dependency-name: "*"
        update-types: [ 
          "version-update:semver-minor",
          "version-update:semver-patch"
        ]
    groups:
      prod-dependencies:
        dependency-type: "production"
        update-types:
          - "major"
      dev-dependencies:
        dependency-type: "development"
        update-types:
          - "major"
    commit-message:
      prefix: "chore"
      include: "scope"

```
> [WARNING] Lié à historique de GLC nous avons un usage elevé de la lib `serverless`qui est devenue payant, donc la configuration suivent permetra d’exclure les mise à jour de cette lib à partir de la version 4.
```yaml
ignore:
      - dependency-name: "*"
        update-types: [ 
          "version-update:semver-minor",
          "version-update:semver-patch"
        ]
      - dependency-name: "serverless"
        versions: [">=4.0.0"]
```
## Container Base Images Dependencies **[SUBMITTED]**
Les images publiques sont utilisé dans les stacks applicatives et dans les images references fournit par team Operations.
Example
```yaml
version: 2

registries:
  ecr-publichub:
    type: "docker-registry"
    url: "https://gallery.ecr.aws"
    username: "fakeit" // required but value has no effect
    password: "fakeit" // required but value has no effect

updates:
  - package-ecosystem: "docker"
    open-pull-requests-limit: 1
    directories:
      - '/'
    schedule:
      interval: "monthly"
    registries:
      - ecr-publichub
    ignore:
      - dependency-name: "*"
        update-types: [ "version-update:semver-major" ]
    commit-message:
      prefix: "chore"
      include: "scope"
  - package-ecosystem: "docker"
    open-pull-requests-limit: 1
    directories:
      - '/'
    target-branch: "main"
    schedule:
      interval: "monthly"
    registries:
      - ecr-publichub
    ignore:
      - dependency-name: "*"
        update-types: [ 
          "version-update:semver-minor",
          "version-update:semver-patch"
        ]
    commit-message:
      prefix: "chore"
      include: "scope"
```

**Private Images:** Les images privé peut être géré par `Dependabot` mais ceci n’est pour sous couvert de ce documentation comme ca va nous obligé de avoir les ACCESS_KEY and SECRET_KEY dans GitHub.

**Quelque recommendation sont:**
- **Major version**: La migration des major versions sont éligibles à être traitée dans une durée assez large comme ces runtime sont pas released fréquemment. en plus le runtime nodejs ( cas usage major chez GLC ) suit un pattern des version paire comme stable. cela peut etre configuré sans problem pour les runtimes comme python.
- **Minor/Patch Version**: Une configuration dédié aux upgrade des images par les release minor et patch version.

## GitHub Actions **[SUBMITTED]**
Example
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    open-pull-requests-limit: 2
    directories: 
     - "/"
    schedule:
      interval: "monthly"
```
## Caution
Si les PRs des `Dependabot`sont pas pris en compte pour longtime, github empeche le process de update en le mettant en pause. un message sera affiché dans le repo avec un message comme l’image ci-desous 
> [MEDIA]
# Running Dependabot manually
`Dependabot` doit être configuré en mode `Scheduled` mais pour les besoin debug, mise en place initial, ou lancement à volonté par team y a l’option de lancement manuel ( plus d’info:  )
- Dans onglet `insights` de repository
- Selectionnez `Dependencies Graph` dans le sidebar à gauche
- Selectionnez l’onglet  `Dependabot`
- Allez dans la partie `Recent Update Jobs`
- cliquez sur `Run Update check` et puis `Check for updates`  button
# Dependabot Errors
Il y a des errors qu’on peut rencontré lors de utilisation de `Dependabot` ( les errors connue dans GitHub docs :  )
Cette exemple montre un cas avec une configuration qui applique `open-pull-requests-limit` avec une longue liste des dependences a updater dans un coup, et par le config `open-pull-requests-limit: 2` le bot n’est pas capable de créer plus de PRs
> [MEDIA]
# Dependencies Types
## Packages
Chaque librarie ramène ses dependences interne et externe, quelque soit le cas, ces dependences ont leurs propre cycle de vie de versioning, et nouvelles versions ( major, minor, or path ) sont sorties fréquemment. en tant que owner de la lib, nous devrons garder les dependencies à jour et upgrader ces versions souvent selon la possiblité. 
Y a aucun interet de appliquer les MAJ de chaque dependence tous les jours, mais en voyant ce process en tant qu’une tache afin de reducir le taux de technical debt à long terme.

The dependencies upgrade had the following considerations
- Patch/Minor version upgrades ont meme lifecycle
- Major versions ont un propre Lifecycle
- Dependences Development et Production doivent être treaté separrement
- Les dependences `indirect` ( deps of direct deps ) doivent être exclu et Considerez que les dependences `direct`.
- Dependabot Automated PullRequest doivent être groupé
- Utilisez la branche  par defaut qui ne receoit pas frequement le smise à jours
- Limitez le nombre des PRs `Dependabot`
- Considerez tester les update des dependences en isolation and valider la bonne fonctionnement
- Ne mettez pas une effort elevé dans gestion des dependencies en quotedian et considerez le comme un long term process afin de reduire le `Technical Debt`
- Considerez à verifierles `Release Note` des dependencies si necessaire qui sont presentent dans la PR.
## Runtime and Engines
Certaines Libs sont dévélopé et sortie pour un runtime dedié (i.e. **nodejs18**), pendant que ca n’est pas un problem en soi et c’est dédié à  la lib et les resoponsabilité de lib concerné, les laisser sams MAJ deviendrait un problem lors de fin de security updates de runtime et generallement EOL. 
Le owner de la lib doit appliquer un process afin de simplifier les MAJ et garder les dependences à jour et fournir des nouvelles version à jour. le point important est validation de backward compatibility et si un impact sortir une version major.
## Container Images
Lorsqu'il s'agit d'images de conteneurs et des images de base dépendantes suivant différents cycles de publication, il est important de prendre en considération les versions de sécurité et de publication, ainsi que les versions mineures basées sur les scénarios et les cycles de publication et de versionnement des images de base. Cela peut différer pour les images de base internes (comme nous suivons souvent les mêmes pratiques internes) et externes.
La mise à jour des images de base de conteneurs peut être réalisée avec Dependabot ; nous devons établir des contraintes pour chaque dépendance et examiner son cycle de publication.
Il existe trois types d'images ECR utilisées dans GLC : **public, shared, **et** application**. .
**Public** : Les images de base publiques fournies par Amazon, telles que nodejs:22-slim, aws-lambda-adapter:0.9.0, ou python:3.12.0-bookworm, suivent des cycles d'évolution et de versionnement différents. Par exemple, l'image du web adaptateur lambda reçoit plus de mises à jour dans notre intérêt à court terme que Node.js 22, mais Node.js 22 doit également être pris en compte car nous suivons l'évolution des nouvelles plateformes d'exécution, etc., dans l'écosystème AWS.
**Reference images** : Les images de référence fournies par l'équipe des opérations sont des images de base fournies par GLC pour tout besoin de personnalisation et sont déployées sur le compte DPL. Ces images suivent un processus d'évolution lente mais dépendent de certaines images de base publiques. Bien que le taux de publication soit lent, il est important de les maintenir à jour en ce qui concerne les mises à jour des dépendances externes et publiques. Une fois les mises à jour effectuées, tous les utilisateurs de l'image partagée interne personnalisée doivent envisager de mettre à jour leur référence.
**Application Images**: Les images d'application sont les actifs d'application construits sur une image de base publique ou partagée interne et doivent suivre les révisions et maintenir à jour les dépendances.
## Github Actions
dans les cas rare nous utilisons les GitHub Actions, ceci oblige utilisations de certains actions publique comme  `actions/checkout`, `actions/setup-node` , or `pnpm/action-setup` . Sachant que le cycle de release de ces dependence est vraiment lent, mais rien nous empêche de les garder à jour et reduire nos coups de Debt.
# Reviewers
Afin de simplifier la collaboration et cycle de gestion des PRs generer par dependabot chaque repo doit contenir un fichier `CODEOWNERS` sous répertoire `.github` indiquant le nom de l'équipe owner de repository. Cette Configuration va automatiquement attaché le team en tant que Reviewer à chaque PR.
