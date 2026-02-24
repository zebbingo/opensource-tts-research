from pathlib import Path

BASE = Path(__file__).parent
MODELS = BASE / "models"
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

DEFAULT_TEXT = (
    "Welcome to the Zebbingo World. Zebbingo is a screen-free audio platform for children. "
    "Through smart stories, songs and conversations, we fuel curiosity. "
    "We support parents by providing experiences for children that are genuinely inspiring and safe."
)

VOICE_CATALOG = {
    "piper": {
        "label": "Piper",
        "voices": {
            "en_US-lessac-medium": {
                "label": "English US - Lessac (medium)",
                "model": MODELS / "piper" / "en_US-lessac-medium.onnx",
                "config": MODELS / "piper" / "en_US-lessac-medium.onnx.json",
            },
            "en_GB-alan-medium": {
                "label": "English GB - Alan (medium)",
                "model": MODELS / "piper" / "en_GB-alan-medium.onnx",
                "config": MODELS / "piper" / "en_GB-alan-medium.onnx.json",
            },
        },
    },
    "coqui": {
        "label": "Coqui TTS",
        "voices": {
            "en_US-ljspeech": {
                "label": "English US - LJSpeech Tacotron2-DDC",
                "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
                "speaker": None,
            },
            "en_GB-vctk-p225": {
                "label": "English GB - VCTK VITS (speaker p225)",
                "model_name": "tts_models/en/vctk/vits",
                "speaker": "p225",
            },
        },
    },
    "espeak": {
        "label": "eSpeak NG",
        "voices": {
            "en-us": {"label": "English US - eSpeak", "voice": "en-us"},
            "en-gb": {"label": "English GB - eSpeak", "voice": "en-gb"},
        },
    },
}
