"""
Translation engine using the deep-translator library (Google Translate backend).
No API key required.
"""
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException, NotValidPayload


def get_supported_languages() -> dict:
    """
    Returns a dict of {language_name: language_code} supported by the translator,
    e.g. {"english": "en", "french": "fr", ...}.
    Includes an 'auto' option for automatic source-language detection.
    """
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    # Put "auto" first (for source language auto-detection)
    ordered = {"auto (detect language)": "auto"}
    ordered.update(dict(sorted(langs.items())))
    return ordered


def translate_text(text: str, source: str, target: str) -> str:
    """
    Translates `text` from `source` language code to `target` language code.
    `source` can be "auto" for automatic detection.
    Raises ValueError with a user-friendly message on failure.
    """
    if not text or not text.strip():
        raise ValueError("Please enter some text to translate.")

    if source == target and source != "auto":
        return text

    try:
        translator = GoogleTranslator(source=source, target=target)
        return translator.translate(text)
    except LanguageNotSupportedException as e:
        raise ValueError(f"Language not supported: {e}") from e
    except NotValidPayload as e:
        raise ValueError("The text provided is not valid for translation.") from e
    except Exception as e:
        raise ValueError(
            "Translation failed. Please check your internet connection and try again. "
            f"(details: {e})"
        ) from e


if __name__ == "__main__":
    # Quick CLI test
    langs = get_supported_languages()
    print(f"{len(langs)} languages available (including auto-detect).")
    text = input("Enter text to translate: ")
    target_name = input("Target language (e.g. french, spanish, german): ").strip().lower()
    target_code = langs.get(target_name)
    if not target_code:
        print("Unknown language name. Try a name like 'french' or 'spanish'.")
    else:
        print(translate_text(text, source="auto", target=target_code))
