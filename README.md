# Open Source TTS Research Web

A local web app to compare popular open-source TTS engines and voices.

## Included engines

- Piper
- Coqui TTS
- Kokoro
- eSpeak NG

## Features

- Choose engine + voice
- Default benchmark text prefilled
- One-click synthesis and audio playback/download
- **Preload step** downloads US/GB English assets ahead of time (no lazy download during first use)
- Kokoro support with curated English US/GB voices

## Quick start (uv)

```bash
cd /Users/bulusi/Documents/GitHub/opensource-tts-research
uv venv
source .venv/bin/activate
uv sync
uv run python preload_models.py
uv run python app.py
```

To enable Kokoro too (recommended in a separate virtualenv because Coqui and Kokoro have conflicting NumPy requirements):

```bash
uv pip install kokoro-onnx==0.5.0 soundfile==0.13.1
uv run python preload_models.py
```

Open: http://127.0.0.1:7850

## Ngrok

```bash
ngrok http 7850
```

Use the generated `https://*.ngrok-free.app` URL.

## Notes

- `preload_models.py` requires `piper`, `tts`, and `espeak-ng` binaries available in PATH.
- If you manually install Kokoro dependencies, preload also downloads Kokoro ONNX assets into `models/kokoro/`.
- Coqui model preload can take significant time and disk.
