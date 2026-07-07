"""
Text-to-speech helper using gTTS (Google Text-to-Speech).
Generates an in-memory MP3 that can be played directly in the Streamlit app.
"""
from io import BytesIO
from gtts import gTTS
from gtts.lang import tts_langs

# gTTS uses its own language code list, close to but not identical with
# deep-translator's. We only attempt TTS if the target language code is supported.
_SUPPORTED_TTS_LANGS = None


def is_tts_supported(lang_code: str) -> bool:
    global _SUPPORTED_TTS_LANGS
    if _SUPPORTED_TTS_LANGS is None:
        try:
            _SUPPORTED_TTS_LANGS = set(tts_langs().keys())
        except Exception:
            _SUPPORTED_TTS_LANGS = set()
    return lang_code in _SUPPORTED_TTS_LANGS


def text_to_speech_bytes(text: str, lang_code: str) -> bytes:
    """
    Converts `text` to speech in `lang_code` and returns MP3 bytes.
    Raises ValueError if the language isn't supported or synthesis fails.
    """
    if not text or not text.strip():
        raise ValueError("No text to convert to speech.")
    if not is_tts_supported(lang_code):
        raise ValueError(f"Text-to-speech is not available for language code '{lang_code}'.")

    try:
        tts = gTTS(text=text, lang=lang_code)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        raise ValueError(f"Text-to-speech generation failed: {e}") from e
