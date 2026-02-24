from pathlib import Path
import subprocess

BASE = Path(__file__).parent
MODELS = BASE / "models"
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

DEFAULT_TEXT = (
    "Welcome to the Zebbingo World. Zebbingo is a screen-free audio platform for children. "
    "Through smart stories, songs and conversations, we fuel curiosity. "
    "We support parents by providing experiences for children that are genuinely inspiring and safe."
)

# Curated popular EN-US/EN-GB Piper voices (auto-preloaded)
PIPER_VOICE_PATHS = {
    "en_US-lessac-medium": "en/en_US/lessac/medium",
    "en_US-lessac-high": "en/en_US/lessac/high",
    "en_US-amy-medium": "en/en_US/amy/medium",
    "en_US-joe-medium": "en/en_US/joe/medium",
    "en_US-libritts-high": "en/en_US/libritts/high",
    "en_US-hfc_female-medium": "en/en_US/hfc_female/medium",
    "en_GB-alan-medium": "en/en_GB/alan/medium",
    "en_GB-alba-medium": "en/en_GB/alba/medium",
    "en_GB-cori-medium": "en/en_GB/cori/medium",
    "en_GB-jenny_dioco-medium": "en/en_GB/jenny_dioco/medium",
    "en_GB-semaine-medium": "en/en_GB/semaine/medium",
    "en_GB-northern_english_male-medium": "en/en_GB/northern_english_male/medium",
}

PIPER_LABELS = {
    "en_US-lessac-medium": "English US - Lessac (medium)",
    "en_US-lessac-high": "English US - Lessac (high)",
    "en_US-amy-medium": "English US - Amy (medium)",
    "en_US-joe-medium": "English US - Joe (medium)",
    "en_US-libritts-high": "English US - LibriTTS (high)",
    "en_US-hfc_female-medium": "English US - HFC Female (medium)",
    "en_GB-alan-medium": "English GB - Alan (medium)",
    "en_GB-alba-medium": "English GB - Alba (medium)",
    "en_GB-cori-medium": "English GB - Cori (medium)",
    "en_GB-jenny_dioco-medium": "English GB - Jenny Dioco (medium)",
    "en_GB-semaine-medium": "English GB - Semaine (medium)",
    "en_GB-northern_english_male-medium": "English GB - Northern English Male (medium)",
}


def build_piper_voices():
    out = {}
    for voice in PIPER_VOICE_PATHS:
        model = MODELS / "piper" / f"{voice}.onnx"
        config = MODELS / "piper" / f"{voice}.onnx.json"
        if model.exists() and config.exists():
            out[voice] = {
                "label": PIPER_LABELS.get(voice, voice),
                "model": model,
                "config": config,
            }
    return out


def discover_espeak_voices():
    # Discover many EN voices from local espeak-ng install.
    # Falls back to a small set if discovery fails.
    fallback = {
        "en-us": {"label": "English US - eSpeak", "voice": "en-us"},
        "en-us+f3": {"label": "English US - Female 3", "voice": "en-us+f3"},
        "en-gb": {"label": "English GB - eSpeak", "voice": "en-gb"},
        "en-gb+f3": {"label": "English GB - Female 3", "voice": "en-gb+f3"},
    }

    try:
        p = subprocess.run(
            ["espeak-ng", "--voices=en"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        voices = {}
        for line in p.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            code = parts[1].strip()
            if not (code.startswith("en-us") or code.startswith("en-gb")):
                continue
            name = " ".join(parts[3:])
            voices[code] = {"label": f"{code} - {name}", "voice": code}

        return voices or fallback
    except Exception:
        return fallback


VOICE_CATALOG = {
    "piper": {
        "label": "Piper",
        "voices": build_piper_voices(),
    },
    "coqui": {
        "label": "Coqui TTS",
        "voices": {
            "en_US-ljspeech": {
                "label": "English US - LJSpeech Tacotron2-DDC",
                "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
                "speaker": None,
            },
            "en_US-ljspeech-fastpitch": {
                "label": "English US - LJSpeech FastPitch",
                "model_name": "tts_models/en/ljspeech/fast_pitch",
                "speaker": None,
            },
            "en_GB-vctk-p225": {
                "label": "English GB - VCTK p225",
                "model_name": "tts_models/en/vctk/vits",
                "speaker": "p225",
            },
            "en_GB-vctk-p226": {"label": "English GB - VCTK p226", "model_name": "tts_models/en/vctk/vits", "speaker": "p226"},
            "en_GB-vctk-p227": {"label": "English GB - VCTK p227", "model_name": "tts_models/en/vctk/vits", "speaker": "p227"},
            "en_GB-vctk-p228": {"label": "English GB - VCTK p228", "model_name": "tts_models/en/vctk/vits", "speaker": "p228"},
            "en_GB-vctk-p229": {"label": "English GB - VCTK p229", "model_name": "tts_models/en/vctk/vits", "speaker": "p229"},
            "en_GB-vctk-p230": {"label": "English GB - VCTK p230", "model_name": "tts_models/en/vctk/vits", "speaker": "p230"},
            "en_GB-vctk-p231": {"label": "English GB - VCTK p231", "model_name": "tts_models/en/vctk/vits", "speaker": "p231"},
            "en_GB-vctk-p232": {"label": "English GB - VCTK p232", "model_name": "tts_models/en/vctk/vits", "speaker": "p232"},
        },
    },
    "espeak": {
        "label": "eSpeak NG",
        "voices": discover_espeak_voices(),
    },
}
