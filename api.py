"""
Flask backend for the Language Translation Tool web UI.
Wraps translator.py and tts.py behind a small JSON API consumed by static/script.js.

Run with:
    python api.py
Then open http://localhost:5000 in your browser.
"""
from flask import Flask, jsonify, request, send_from_directory, Response

from translator import get_supported_languages, translate_text
from tts import text_to_speech_bytes, is_tts_supported

app = Flask(__name__, static_folder="static", static_url_path="")


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.route("/api/languages", methods=["GET"])
def api_languages():
    """Returns { languages: [{name, code}, ...] }, 'auto' included."""
    langs = get_supported_languages()
    payload = [{"name": name, "code": code} for name, code in langs.items()]
    return jsonify({"languages": payload})


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    Body: { text: str, source: str (lang code or 'auto'), target: str (lang code) }
    Returns: { translation: str } or { error: str }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    source = data.get("source", "auto")
    target = data.get("target", "en")

    if not target or target == "auto":
        return jsonify({"error": "Please choose a specific target language."}), 400

    try:
        translation = translate_text(text, source, target)
        return jsonify({"translation": translation})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tts", methods=["POST"])
def api_tts():
    """
    Body: { text: str, lang: str (language code) }
    Returns: raw MP3 audio bytes, or JSON { error: str } on failure.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    lang = data.get("lang", "en")

    if not is_tts_supported(lang):
        return jsonify({"error": f"Text-to-speech is not available for language '{lang}'."}), 400

    try:
        audio_bytes = text_to_speech_bytes(text, lang)
        return Response(audio_bytes, mimetype="audio/mpeg")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
