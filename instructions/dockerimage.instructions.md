---
applyTo: "**"
---

# Optimization des Images Docker
Le usage des containers Fargate suite de point  est propagé au seine de GLC dans les cas applications mais aussi dans les process Machine Learning était utilisé.
# Cas de Usage
- Applications ( Fargate, Lambda CustomImage)
- MachineLearning ( Sagemaker )
# Problem
Le images portent les dependances et contenu non necessaire qui conduit à des images volumineuses portant un poids inutile et augmentant les risques de sécurité.

# **Recomendations**

## Multi Stage DockerFile:
Separation des phase Build et Runtime, ceci permettra de avoir un process build totalement autonome mais une image final qui contient que le code et dependences util en runtime.

```dockerfile
FROM public.ecr.aws/amazonlinux/amazonlinux:2023-minimal AS build
... 
FROM public.ecr.aws/amazonlinux/amazonlinux:2023-minimal AS runtime 
COPY --from=build ./path/to/bundle ./path/to/destination
...
```

## Triage des Instructions:
Pour optimiser la phase CI et temp de build d’image, une ordonance correct des couches d'instructions peut ameliorer la rapidité de build. L’ordre des instructions son par la muttabilité des chaque layer, ex. pip install poetryest plus solid que install dependencies donc un changement dans les dependencies va pas forcer le reinstallation de poetry mais le chache sera utilisé
```dockerfile
 FROM public.ecr.aws/docker/library/python:3.10-slim-bookworm AS build
RUN pip install poetry 
COPY pyproject.toml poetry.lock ./ 
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
FROM public.ecr.aws/docker/library/python:3.10-slim-bookworm AS runtime 
COPY --from=build ./path/to/bundle ./path/to/destination 
... 
```

## Choose the right base image:
les images base peuvent suivre differents cycle d'evolution et security patches, par exemple debian a moins des patch securité delivré en courte terme mais Amazon Linux 2023 a des updates plus souvent.

## Suivie les tags des images base
Certain image ont un comportement latest par default mais aussi fournie le tags afin de versioné le cycle des releases comme AL2023, c’est important de utiliser les tags afin de mieux automatiser et faire les rebuild des images Reference AL2023

```dockerfile
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.7.20250512.0-minimal AS build 
... 
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.7.20250512.0-minimal AS runtime ... 
```
