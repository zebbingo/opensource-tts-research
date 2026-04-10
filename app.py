#!/usr/bin/env python3
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from kokoro_runtime import synthesize_kokoro_to_file
from voices import DEFAULT_TEXT, OUTPUTS, VOICE_CATALOG

app = Flask(__name__)
BASE = Path(__file__).parent
VENV_BIN = BASE / ".venv" / "bin"


def resolve_bin(name: str) -> str | None:
    candidate = VENV_BIN / name
    if candidate.exists() and candidate.is_file():
        return str(candidate)
    return shutil.which(name)


def run(cmd, input_text=None):
    return subprocess.run(
        cmd,
        input=input_text.encode("utf-8") if input_text else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def check_bins():
    return {
        "piper": resolve_bin("piper") is not None,
        "coqui": resolve_bin("tts") is not None,
        "kokoro": bool(VOICE_CATALOG.get("kokoro", {}).get("voices")),
        "parler": False,
        "espeak": resolve_bin("espeak-ng") is not None,
    }


def synth_to_file(engine: str, voice: str, text: str, out_path, advanced=None):
    advanced = advanced or {}
    if engine == "piper":
        spec = VOICE_CATALOG["piper"]["voices"][voice]
        piper_bin = resolve_bin("piper")
        if not piper_bin:
            raise FileNotFoundError("piper")
        cmd = [
            piper_bin,
            "--model",
            str(spec["model"]),
            "--config",
            str(spec["config"]),
            "--output_file",
            str(out_path),
        ]
        if advanced.get("length_scale") is not None:
            cmd += ["--length_scale", str(advanced["length_scale"])]
        if advanced.get("noise_scale") is not None:
            cmd += ["--noise_scale", str(advanced["noise_scale"])]
        if advanced.get("noise_w") is not None:
            cmd += ["--noise_w", str(advanced["noise_w"])]
        run(cmd, input_text=text)

    elif engine == "coqui":
        spec = VOICE_CATALOG["coqui"]["voices"][voice]
        tts_bin = resolve_bin("tts")
        if not tts_bin:
            raise FileNotFoundError("tts")
        cmd = [
            tts_bin,
            "--model_name",
            spec["model_name"],
            "--text",
            text,
            "--out_path",
            str(out_path),
        ]
        speaker = advanced.get("speaker") or spec.get("speaker")
        if speaker:
            cmd += ["--speaker_idx", str(speaker)]
        run(cmd)

    elif engine == "kokoro":
        synthesize_kokoro_to_file(text, voice, out_path, advanced=advanced)

    elif engine == "espeak":
        spec = VOICE_CATALOG["espeak"]["voices"][voice]
        espeak_bin = resolve_bin("espeak-ng")
        if not espeak_bin:
            raise FileNotFoundError("espeak-ng")
        cmd = [espeak_bin, "-v", spec["voice"], "-w", str(out_path)]
        if advanced.get("rate") is not None:
            cmd += ["-s", str(int(advanced["rate"]))]
        if advanced.get("pitch") is not None:
            cmd += ["-p", str(int(advanced["pitch"]))]
        cmd.append(text)
        run(cmd)


@app.get("/")
def index():
    simple_catalog = {
        e: {
            "label": cfg["label"],
            "voices": {k: {"label": v["label"]} for k, v in cfg["voices"].items()},
        }
        for e, cfg in VOICE_CATALOG.items()
    }
    return render_template(
        "index.html",
        default_text=DEFAULT_TEXT,
        catalog=simple_catalog,
        bins=check_bins(),
    )


@app.post("/synthesize")
def synthesize():
    data = request.json or {}
    engine = data.get("engine")
    voice = data.get("voice")
    text = (data.get("text") or "").strip()
    advanced = data.get("advanced") or {}

    if not text:
        return jsonify({"ok": False, "error": "Text is empty"}), 400
    if engine not in VOICE_CATALOG:
        return jsonify({"ok": False, "error": "Unknown engine"}), 400
    if voice not in VOICE_CATALOG[engine]["voices"]:
        return jsonify({"ok": False, "error": "Unknown voice"}), 400

    out_name = f"{engine}_{voice}_{int(time.time())}_{uuid.uuid4().hex[:6]}.wav"
    out_path = OUTPUTS / out_name

    try:
        synth_to_file(engine, voice, text, out_path, advanced=advanced)
        return jsonify({"ok": True, "audio_url": f"/audio/{out_name}"})
    except subprocess.CalledProcessError as e:
        return jsonify(
            {
                "ok": False,
                "error": e.stderr.decode("utf-8", errors="ignore")[-2000:],
            }
        ), 500


@app.post("/compare_batch")
def compare_batch():
    data = request.json or {}
    text = (data.get("text") or "").strip()
    advanced = data.get("advanced") or {}
    items = data.get("items") or []

    if not text:
        return jsonify({"ok": False, "error": "Text is empty"}), 400
    if not isinstance(items, list) or len(items) == 0:
        return jsonify({"ok": False, "error": "Please select at least one voice"}), 400

    results = []
    for item in items:
        engine = item.get("engine")
        voice = item.get("voice")
        label = item.get("label") or f"{engine}:{voice}"
        advanced = item.get("advanced") or {}

        if engine not in VOICE_CATALOG or voice not in VOICE_CATALOG[engine]["voices"]:
            results.append({"ok": False, "label": label, "error": "Unknown engine/voice"})
            continue

        out_name = f"{engine}_{voice}_{int(time.time())}_{uuid.uuid4().hex[:6]}.wav"
        out_path = OUTPUTS / out_name

        try:
            synth_to_file(engine, voice, text, out_path, advanced=advanced)
            results.append(
                {
                    "ok": True,
                    "engine": engine,
                    "voice": voice,
                    "label": label,
                    "audio_url": f"/audio/{out_name}",
                    "advanced": advanced,
                }
            )
        except subprocess.CalledProcessError as e:
            results.append(
                {
                    "ok": False,
                    "engine": engine,
                    "voice": voice,
                    "label": label,
                    "error": e.stderr.decode("utf-8", errors="ignore")[-1000:],
                }
            )

    return jsonify({"ok": True, "results": results})


@app.get("/audio/<name>")
def audio(name):
    target = OUTPUTS / name
    if not target.exists():
        return "Not found", 404
    return send_file(target, mimetype="audio/wav")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7850, debug=False)
