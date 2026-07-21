# http-server

A learning project: an HTTP/1.1 server built from scratch in Python, standard library only.

Built layer by layer — TCP sockets → request parsing → routing → static files → keep-alive → concurrency — with a heavy emphasis on unit tests.

## Run

```bash
uv sync
uv run pytest
```
