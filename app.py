from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from music_engine import GENERATED_DIR, MODEL_PATH, generate_music

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_ready": MODEL_PATH.exists(),
            "message": "AI Music Studio is ready.",
        }
    )


@app.post("/api/generate")
def generate():
    payload = request.get_json(silent=True) or {}

    style = str(payload.get("style", "classical")).lower()
    length = payload.get("length", 96)
    creativity = payload.get("creativity", 0.9)

    try:
        result = generate_music(style=style, length=int(length), creativity=float(creativity))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid generation settings."}), 400
    except Exception as exc:
        return jsonify({"error": f"Generation failed: {exc}"}), 500

    result["download_url"] = f"/generated/{result['filename']}"
    return jsonify(result)


@app.get("/generated/<path:filename>")
def generated_file(filename):
    return send_from_directory(GENERATED_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    Path("generated").mkdir(exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
