# Open Source TTS Research Web

A local web app to compare popular open-source TTS engines and voices.

## Included engines

- Piper
- Coqui TTS
- eSpeak NG

## Features

- Choose engine + voice
- Default benchmark text prefilled
- One-click synthesis and audio playback/download
- **Preload step** downloads US/GB English assets ahead of time (no lazy download during first use)

## Quick start

```bash
cd /Users/bulusi/Documents/Github/opensource-tts-research
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python preload_models.py
python app.py
```

Open: http://127.0.0.1:7860

## Ngrok

```bash
ngrok http 7860
```

Use the generated `https://*.ngrok-free.app` URL.

## Notes

- `preload_models.py` requires `piper`, `tts`, and `espeak-ng` binaries available in PATH.
- Coqui model preload can take significant time and disk.
