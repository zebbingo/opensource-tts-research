from __future__ import annotations

from pathlib import Path
from typing import Any

BASE = Path(__file__).parent
MODELS = BASE / "models"
KOKORO_DIR = MODELS / "kokoro"
KOKORO_MODEL = KOKORO_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES = KOKORO_DIR / "voices-v1.0.bin"

KOKORO_LABELS = {
    "af": "Kokoro · AF (US female)",
    "af_bella": "Kokoro · AF Bella",
    "af_nicole": "Kokoro · AF Nicole",
    "af_sarah": "Kokoro · AF Sarah",
    "af_sky": "Kokoro · AF Sky",
    "am_adam": "Kokoro · AM Adam",
    "am_michael": "Kokoro · AM Michael",
    "bf_emma": "Kokoro · BF Emma (GB)",
    "bf_isabella": "Kokoro · BF Isabella (GB)",
    "bm_george": "Kokoro · BM George (GB)",
    "bm_lewis": "Kokoro · BM Lewis (GB)",
}


def kokoro_installed() -> bool:
    try:
        import kokoro_onnx  # noqa: F401
        import soundfile  # noqa: F401
        return True
    except Exception:
        return False


def kokoro_assets_ready() -> bool:
    return kokoro_installed() and KOKORO_MODEL.exists() and KOKORO_VOICES.exists()


def build_kokoro_voices() -> dict[str, dict[str, Any]]:
    if not kokoro_assets_ready():
        return {}

    return {
        voice: {
            "label": KOKORO_LABELS.get(voice, f"Kokoro - {voice}"),
            "voice": voice,
            "lang": "en-gb" if voice.startswith("b") else "en-us",
            "speed": 1.0,
        }
        for voice in KOKORO_LABELS
    }


_KOKORO_INSTANCE = None


def get_kokoro():
    global _KOKORO_INSTANCE
    if _KOKORO_INSTANCE is None:
        if not kokoro_installed():
            raise RuntimeError(
                "Kokoro dependencies are not installed. Install them manually inside .venv: `uv pip install kokoro-onnx==0.5.0 soundfile==0.13.1`"
            )
        if not (KOKORO_MODEL.exists() and KOKORO_VOICES.exists()):
            raise FileNotFoundError(
                "Kokoro model assets are missing. Run `uv run python preload_models.py` first."
            )
        from kokoro_onnx import Kokoro

        _KOKORO_INSTANCE = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    return _KOKORO_INSTANCE


def synthesize_kokoro_to_file(text: str, voice: str, out_path: Path) -> None:
    spec = build_kokoro_voices().get(voice)
    if spec is None:
        raise ValueError(f"Unknown Kokoro voice: {voice}")

    kokoro = get_kokoro()
    audio, sample_rate = kokoro.create(
        text,
        voice=spec["voice"],
        speed=spec.get("speed", 1.0),
        lang=spec.get("lang", "en-us"),
    )

    import soundfile as sf

    sf.write(str(out_path), audio, sample_rate)
