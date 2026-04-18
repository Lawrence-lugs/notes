---
title: Online Caching of Devcontainer builds with GHCR.io
modified: 2026-04-16
date: 2026-04-02
---

> [!summary]
> Problem : Building and rebuilding docker images takes centuries.
> Solution : Cache build in GHCR.io

I wasn't familiar with this yet when I started heavily using docker containers half a year ago (I think just half a year ago).

Devcontainers + Dockerfiles create reproducible and containerized development environments for every project.

However, if we'd like to stop working on a project, we want to delete these containers. 
When we want to open it again, we have to rebuild it locally.

To avoid this, we have to use the `cachedFrom:` option in the `devcontainer.json`:

```json
{
  "name": "My Dev Environment",
  "build": {
    "dockerfile": "Dockerfile",
    "cacheFrom": [
      "ghcr.io/YOUR_GITHUB_USER/YOUR_REPO/devcontainer:latest"
    ]
  },
  "customizations": {
    // ... your vscode extensions, etc.
  }
}
```

Problem is, how does the build get pushed to the remote repository?
In comes CI workflows.

You add a CI workflow that builds the image and pushes to the remote repository.

```yaml
name: Build & push devcontainer image

on:
  push:
    branches: [main]
    paths:
      - ".devcontainer/Dockerfile"
      - "environment.yml"

env:
  IMAGE: ghcr.io/lawrence-lugs/reponame[/something]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout (GH)
        uses: actions/checkout@v4


      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: .devcontainer/Dockerfile
          push: true
          tags: ${{ env.IMAGE }}:latest
          cache-from: type=registry,ref=${{ env.IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ env.IMAGE }}:buildcache,mode=max
```

In that case, the actions worker will build the image by itself and push it to the repository.
Then, once the image is created, you can just pull it.