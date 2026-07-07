# CodeAlpha_LanguageTranslator

Language translation tool built as part of the **CodeAlpha** Artificial Intelligence
internship (Task 1).

## 🎯 Features

- Enter text and select **source** and **target** languages from 130+ options.
- Automatic source-language detection (`auto` option).
- Instant translation powered by **Google Translate** (via `deep-translator`, no API key needed).
- **Copy button** to copy the translated text to the clipboard.
- **Text-to-speech** playback of the translation (via `gTTS`), when supported for that language.

## 📁 Project structure

```
CodeAlpha_LanguageTranslator/
├── app.py            # Streamlit UI
├── translator.py      # Translation engine (deep-translator wrapper)
├── tts.py              # Text-to-speech helper (gTTS wrapper)
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
git clone https://github.com/Ado-2k8/CodeAlpha_LanguageTranslator.git
cd CodeAlpha_LanguageTranslator
pip install -r requirements.txt
```

## ▶️ Usage

### Web interface (Streamlit)
```bash
streamlit run app.py
```
Then open the link shown in the terminal (default: http://localhost:8501).

### Command-line quick test
```bash
python translator.py
```

## 🧪 Example

```
Source text: "Good morning, how are you?"
Source: auto (detected: English)
Target: french
Translation: "Bonjour, comment allez-vous ?"
```

## 🛠️ Tech stack

- Python 3
- Streamlit (user interface)
- deep-translator (Google Translate backend, no API key required)
- gTTS (text-to-speech)

## 📌 Notes

- An internet connection is required at runtime, since translation and
  text-to-speech both call external Google services.
- Not every language supports text-to-speech; the "Listen" button only
  appears when the target language is supported by `gTTS`.

## 👤 Author

Project built as part of the AI Internship — CodeAlpha (2026).
