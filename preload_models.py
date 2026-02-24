#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

from voices import VOICE_CATALOG, MODELS

MODELS.mkdir(exist_ok=True)
(MODELS / "piper").mkdir(parents=True, exist_ok=True)

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def ensure_bin(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing required binary: {name}")


def preload_piper():
    ensure_bin("curl")
    voices = {
        "en_US-lessac-medium": "en/en_US/lessac/medium",
        "en_GB-alan-medium": "en/en_GB/alan/medium",
    }
    for voice, rel in voices.items():
        model = MODELS / "piper" / f"{voice}.onnx"
        config = MODELS / "piper" / f"{voice}.onnx.json"
        if not model.exists():
            run(["curl", "-L", f"{PIPER_BASE}/{rel}/{voice}.onnx", "-o", str(model)])
        if not config.exists():
            run(["curl", "-L", f"{PIPER_BASE}/{rel}/{voice}.onnx.json", "-o", str(config)])


def preload_coqui():
    ensure_bin("tts")
    warmup_dir = MODELS / "coqui_warmup"
    warmup_dir.mkdir(exist_ok=True)

    # US model
    run([
        "tts",
        "--model_name",
        VOICE_CATALOG["coqui"]["voices"]["en_US-ljspeech"]["model_name"],
        "--text",
        "Model warmup for preload",
        "--out_path",
        str(warmup_dir / "coqui_us.wav"),
    ])

    # GB-like voice via VCTK speaker
    run([
        "tts",
        "--model_name",
        VOICE_CATALOG["coqui"]["voices"]["en_GB-vctk-p225"]["model_name"],
        "--speaker_idx",
        VOICE_CATALOG["coqui"]["voices"]["en_GB-vctk-p225"]["speaker"],
        "--text",
        "Model warmup for preload",
        "--out_path",
        str(warmup_dir / "coqui_gb.wav"),
    ])


def preload_espeak():
    ensure_bin("espeak-ng")
    print("eSpeak NG uses built-in voices (en-us/en-gb), no model files to download.")


if __name__ == "__main__":
    preload_piper()
    preload_coqui()
    preload_espeak()
    print("\n✅ Preload complete.")
