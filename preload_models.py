#!/usr/bin/env python3
import shutil
import subprocess

from voices import VOICE_CATALOG, MODELS, PIPER_VOICE_PATHS

MODELS.mkdir(exist_ok=True)
(MODELS / "piper").mkdir(parents=True, exist_ok=True)

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


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


def preload_espeak():
    ensure_bin("espeak-ng")
    print("eSpeak NG uses built-in voices. EN-US/EN-GB variants are already available.")


if __name__ == "__main__":
    preload_piper()
    preload_coqui()
    preload_espeak()
    print("\n✅ Preload complete.")
