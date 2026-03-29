#!/usr/bin/env python3
import shutil
import subprocess

from kokoro_runtime import KOKORO_DIR, KOKORO_MODEL, KOKORO_VOICES
from voices import VOICE_CATALOG, MODELS, PIPER_VOICE_PATHS

MODELS.mkdir(exist_ok=True)
(MODELS / "piper").mkdir(parents=True, exist_ok=True)

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
KOKORO_RELEASE_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"


def run(cmd, allow_fail=False):
    print("+", " ".join(str(c) for c in cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p.returncode == 0


def ensure_bin(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing required binary: {name}")


def preload_piper():
    ensure_bin("curl")
    ok, fail = 0, 0
    for voice, rel in PIPER_VOICE_PATHS.items():
        model = MODELS / "piper" / f"{voice}.onnx"
        config = MODELS / "piper" / f"{voice}.onnx.json"
        if not model.exists():
            if not run(["curl", "-fL", f"{PIPER_BASE}/{rel}/{voice}.onnx", "-o", str(model)], allow_fail=True):
                fail += 1
                continue
        if not config.exists():
            if not run(["curl", "-fL", f"{PIPER_BASE}/{rel}/{voice}.onnx.json", "-o", str(config)], allow_fail=True):
                fail += 1
                continue
        ok += 1
    print(f"Piper preload done: ok={ok}, fail={fail}")


def preload_coqui():
    ensure_bin("tts")
    warmup_dir = MODELS / "coqui_warmup"
    warmup_dir.mkdir(exist_ok=True)

    # download each unique model at least once
    unique_models = {}
    for key, spec in VOICE_CATALOG["coqui"]["voices"].items():
        unique_models.setdefault(spec["model_name"], spec)

    for i, (model_name, spec) in enumerate(unique_models.items(), start=1):
        out_path = warmup_dir / f"coqui_model_{i}.wav"
        cmd = [
            "tts",
            "--model_name",
            model_name,
            "--text",
            "Model warmup for preload",
            "--out_path",
            str(out_path),
        ]
        if spec.get("speaker"):
            cmd += ["--speaker_idx", spec["speaker"]]
        run(cmd)


def preload_kokoro():
    try:
        import kokoro_onnx  # noqa: F401
    except Exception:
        print("Skipping Kokoro preload: optional dependency not installed (`uv pip install kokoro-onnx==0.5.0 soundfile==0.13.1`).")
        return

    ensure_bin("curl")
    KOKORO_DIR.mkdir(parents=True, exist_ok=True)

    if not KOKORO_MODEL.exists():
        run([
            "curl",
            "-fL",
            f"{KOKORO_RELEASE_BASE}/kokoro-v1.0.onnx",
            "-o",
            str(KOKORO_MODEL),
        ])

    if not KOKORO_VOICES.exists():
        run([
            "curl",
            "-fL",
            f"{KOKORO_RELEASE_BASE}/voices-v1.0.bin",
            "-o",
            str(KOKORO_VOICES),
        ])

    print("Kokoro preload done.")


def preload_espeak():
    ensure_bin("espeak-ng")
    print("eSpeak NG uses built-in voices. EN-US/EN-GB variants are already available.")


if __name__ == "__main__":
    preload_piper()
    preload_coqui()
    preload_kokoro()
    preload_espeak()
    print("\n✅ Preload complete.")
