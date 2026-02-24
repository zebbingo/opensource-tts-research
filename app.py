#!/usr/bin/env python3
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from voices import DEFAULT_TEXT, OUTPUTS, VOICE_CATALOG

app = Flask(__name__)


def run(cmd, input_text=None):
    p = subprocess.run(
        cmd,
        input=input_text.encode("utf-8") if input_text else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return p


def check_bins():
    return {
        "piper": shutil.which("piper") is not None,
        "coqui": shutil.which("tts") is not None,
        "espeak": shutil.which("espeak-ng") is not None,
    }


@app.get("/")
def index():
    simple_catalog = {
        e: {
            "label": cfg["label"],
            "voices": {
                k: {"label": v["label"]} for k, v in cfg["voices"].items()
            },
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

    if not text:
        return jsonify({"ok": False, "error": "Text is empty"}), 400
    if engine not in VOICE_CATALOG:
        return jsonify({"ok": False, "error": "Unknown engine"}), 400
    if voice not in VOICE_CATALOG[engine]["voices"]:
        return jsonify({"ok": False, "error": "Unknown voice"}), 400

    out_name = f"{engine}_{voice}_{int(time.time())}_{uuid.uuid4().hex[:6]}.wav"
    out_path = OUTPUTS / out_name

    try:
        if engine == "piper":
            spec = VOICE_CATALOG["piper"]["voices"][voice]
            run([
                "piper",
                "--model",
                str(spec["model"]),
                "--config",
                str(spec["config"]),
                "--output_file",
                str(out_path),
            ], input_text=text)

        elif engine == "coqui":
            spec = VOICE_CATALOG["coqui"]["voices"][voice]
            cmd = [
                "tts",
                "--model_name",
                spec["model_name"],
                "--text",
                text,
                "--out_path",
                str(out_path),
            ]
            if spec.get("speaker"):
                cmd += ["--speaker_idx", spec["speaker"]]
            run(cmd)

        elif engine == "espeak":
            spec = VOICE_CATALOG["espeak"]["voices"][voice]
            run([
                "espeak-ng",
                "-v",
                spec["voice"],
                "-w",
                str(out_path),
                text,
            ])

        return jsonify({"ok": True, "audio_url": f"/audio/{out_name}"})
    except subprocess.CalledProcessError as e:
        return jsonify({
            "ok": False,
            "error": e.stderr.decode("utf-8", errors="ignore")[-2000:],
        }), 500


@app.get("/audio/<name>")
def audio(name):
    target = OUTPUTS / name
    if not target.exists():
        return "Not found", 404
    return send_file(target, mimetype="audio/wav")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
