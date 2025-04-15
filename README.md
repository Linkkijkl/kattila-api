# Kattila API

## Contributing

- Use rebase merges
- Your commit messages should be quickly understandable, follow [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) guidelines
- Keep your commits atomic and upstream branchnames simple
- Delete your branches upstream when done working

## Development

Preparing your development environment should be simple. Some steps are required while initialising your environment even when using docker. One is creating an API key into `apikey.txt`, this is so that no single default key exists. The command below can generate a garbled key for you.

```bash
# Creating an API key
dd if=/dev/urandom bs=32 count=1 2>/dev/null | base64 > apikey.txt
```

### Docker compose

```bash
# Starting a development build
docker compose up --build --watch
```

```bash
# Cleaning up
docker compose down --remove-orphans
```

### Testing in Docker

```bash
docker build -t kattila-api-test -f Dockerfile-run-tests --no-cache .
```
