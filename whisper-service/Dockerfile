# ============================================================
# whisper-service — lightweight on-device transcription engine
# ------------------------------------------------------------
# NOT a .NET service (Whisper engines are C++/Python). This is a
# whisper.cpp server built from source (static, CPU backend linked
# in — no fragile dlopen of ggml-cpu variants) + ffmpeg, so it can
# run on the low-RAM backend alongside the rest of the stack.
#
#   - Model:   ggml-base.bin (multilingual, ~142 MB) — override with
#              --build-arg WHISPER_MODEL=ggml-tiny.bin on weaker boxes
#   - API:     POST /inference  (multipart: file, response_format=json)
#   - Port:    8095 (internal-only in the prod overlay)
#   - Runtime: WHISPER_MODEL / WHISPER_LANG / WHISPER_THREADS env vars
# ============================================================

# ---- build stage: compile whisper-server (static, portable CPU) ----
FROM ubuntu:24.04 AS build

ARG WHISPER_VERSION=b4938

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${WHISPER_VERSION} https://github.com/ggml-org/whisper.cpp /src \
    && cmake -S /src -B /build \
        -DCMAKE_BUILD_TYPE=Release \
        -DGGML_NATIVE=OFF \
        -DGGML_CPU_ALL_VARIANTS=OFF \
        -DGGML_SSE42=OFF \
        -DGGML_AVX=OFF \
        -DGGML_AVX_VNNI=OFF \
        -DGGML_AVX2=OFF \
        -DGGML_FMA=OFF \
        -DGGML_F16C=OFF \
        -DGGML_BMI2=OFF \
        -DGGML_AVX512=OFF \
        -DGGML_AMX_TILE=OFF \
        -DGGML_AMX_INT8=OFF \
        -DGGML_AMX_BF16=OFF \
        -DGGML_BLAS=OFF \
        -DBUILD_SHARED_LIBS=OFF \
        -DWHISPER_BUILD_TESTS=OFF \
    && cmake --build /build -j4 --target whisper-server

# ---- runtime stage ----
FROM ubuntu:24.04

ARG WHISPER_MODEL=ggml-base.bin

ENV WHISPER_MODEL=${WHISPER_MODEL} \
    WHISPER_LANG=auto \
    WHISPER_THREADS=4 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

# ffmpeg is required by whisper-server's --convert (decodes .m4a -> wav)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Multilingual ggml model (kept as its own layer so binary bumps don't
# re-download the ~142 MB model). Swap via --build-arg WHISPER_MODEL.
RUN mkdir -p /models && \
    curl -fsSL -o "/models/${WHISPER_MODEL}" \
      "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${WHISPER_MODEL}"

COPY --from=build /build/bin/whisper-server /usr/local/bin/whisper-server

EXPOSE 8095

# --convert: decode m4a/mp3/ogg/... via ffmpeg before inference
# -l auto:   detect language per request
# -ng:       force CPU (no GPU in the container)
ENTRYPOINT ["sh", "-c", "exec whisper-server --host 0.0.0.0 --port 8095 -m /models/${WHISPER_MODEL} -l ${WHISPER_LANG} --convert -t ${WHISPER_THREADS} -p 1 -ng --no-timestamps"]
