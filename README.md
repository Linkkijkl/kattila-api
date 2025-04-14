# Kattila API

## Contributing

- Use rebase merges
- Your commit messages should be quickly understandable, follow [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) guidelines
- Keep your commits atomic and upstream branchnames simple
- Delete your branches upstream when done working

## Development

```bash
# Creating an API key
dd if=/dev/urandom bs=32 count=1 2>/dev/null | base64 > apikey.txt
```

```bash
# Starting a development build
docker compose up --build --watch
```

```bash
# Cleaning up
docker compose down --remove-orphans
```