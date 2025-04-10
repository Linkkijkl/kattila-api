# Kattila API

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