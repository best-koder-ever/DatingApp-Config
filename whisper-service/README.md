# whisper-service

Tiny **whisper.cpp** transcription engine for the DatingApp, packaged as a
single-binary Docker container. It powers the in-app voice-feedback
transcription: bot-service uploads each recorded `.m4a` and stores the returned
text as the feedback transcript.

It is **deliberately NOT a .NET service** — Whisper engines are C++/Python.
Using the prebuilt `whisper-server` binary keeps the footprint tiny
(≈9 MB binary + model), so it fits on the low-RAM backend
(~300–500 MB RSS with `ggml-base`, ~150 MB with `ggml-tiny`).

## API

```
POST /inference            # multipart form-data
  file=<audio>             # .m4a/.mp3/.wav/.ogg (ffmpeg --convert handles decode)
  response_format=json
  temperature=0.0

→ 200 {"text": "..."}      # transcript (empty string if no speech detected)
```

Smoke test:

```bash
curl -F file=@/tmp/sample.m4a -F response_format=json http://localhost:8095/inference
```

## Configuration

| Env var          | Default         | Notes                                   |
|------------------|-----------------|-----------------------------------------|
| `WHISPER_MODEL`  | `ggml-base.bin` | swap to `ggml-tiny.bin` on weak boxes    |
| `WHISPER_LANG`   | `auto`          | force `sv` for Swedish-only feedback    |
| `WHISPER_THREADS`| `4`             | lower to 2 on constrained CPUs          |

Model files: https://huggingface.co/ggerganov/whisper.cpp/resolve/main/

## Build & run

```bash
docker compose build whisper-service
docker compose up -d whisper-service
```

Custom model (weaker box):

```bash
docker build --build-arg WHISPER_MODEL=ggml-tiny.bin -t datingapp-whisper:latest whisper-service/
```

> Slow-link server (1 Mbit): build locally, then `docker save` → `scp` →
> `docker load` (the model is baked into the image, so no 100+ MB model
> download happens on the box).

## Security

`whisper-server` has no auth layer and accepts file uploads — keep it on the
Docker internal network only. The prod overlay removes host ports entirely.

## Deploy to the little server

Add the service to the server compose (`/home/a/datingapp/docker-compose.yml`)
alongside the other services, and point bot-service at it:

```yaml
  whisper-service:
    image: datingapp-whisper:latest
    ports:
      - "8095:8095"            # LAN-only; remove in prod (Cloudflare/Tailscale)
    environment:
      WHISPER_MODEL: ggml-base.bin
      WHISPER_LANG: auto
      WHISPER_THREADS: "4"
    restart: unless-stopped
    networks: [app-network]

  bot-service:
    environment:
      BotService__Whisper__Enabled: "true"
      BotService__Whisper__BaseUrl: http://whisper-service:8095
```

Transfer the image (built locally with the model baked in — no 100+ MB model
download on the box):

```bash
docker save datingapp-whisper:latest | gzip > whisper.tar.gz
scp whisper.tar.gz a@100.86.173.9:/home/a/datingapp/
# on server: gunzip -c whisper.tar.gz | docker load
docker compose up -d --no-deps --force-recreate whisper-service bot-service
```

Verify:

```bash
curl -F file=@sample.m4a -F response_format=json http://localhost:8095/inference
curl -s http://localhost:8089/api/userfeedback?unprocessed=true   # drains to 0
```

> Memory: `ggml-base` ≈ 300–500 MB RSS. On a tight box use `ggml-tiny.bin`
> (`WHISPER_MODEL=ggml-tiny.bin`) and/or `WHISPER_THREADS=2`.

## Alternative engine

If whisper.cpp accuracy is insufficient for Swedish feedback, swap the engine
for **speaches** (faster-whisper, OpenAI-compatible `/v1/audio/transcriptions`,
same engine the old laptop script used, ~0.6–1.5 GB RAM). The .NET side only
needs `Whisper__BaseUrl` repointed — bot-service's client already parses the
shared `{"text": ...}` response shape.
