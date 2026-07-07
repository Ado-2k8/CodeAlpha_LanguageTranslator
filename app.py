"""
Streamlit interface for the Language Translation Tool.
Run with: streamlit run app.py
"""
import streamlit as st

from translator import get_supported_languages, translate_text
from tts import text_to_speech_bytes, is_tts_supported

st.set_page_config(page_title="Language Translator", page_icon="🌐", layout="centered")

st.title("🌐 Language Translation Tool")
st.caption("Enter text, pick a source and target language, and get an instant translation.")


@st.cache_data
def load_languages():
    return get_supported_languages()


languages = load_languages()
language_names = list(languages.keys())

col1, col2 = st.columns(2)
with col1:
    source_name = st.selectbox("Source language", language_names, index=0)  # "auto (detect language)"
with col2:
    default_target_index = language_names.index("english") if "english" in language_names else 1
    target_name = st.selectbox("Target language", language_names, index=default_target_index)

source_text = st.text_area("Text to translate", height=150, placeholder="Type or paste your text here...")

translate_clicked = st.button("🔁 Translate", type="primary", use_container_width=True)

if "translation" not in st.session_state:
    st.session_state.translation = ""

if translate_clicked:
    source_code = languages[source_name]
    target_code = languages[target_name]

    if target_code == "auto":
        st.error("Please choose a specific target language (not 'auto').")
    else:
        with st.spinner("Translating..."):
            try:
                st.session_state.translation = translate_text(source_text, source_code, target_code)
            except ValueError as e:
                st.session_state.translation = ""
                st.error(str(e))

if st.session_state.translation:
    st.subheader("Translation")
    st.text_area("Result", value=st.session_state.translation, height=150, key="result_box")

    col_a, col_b = st.columns(2)

    with col_a:
        # Copy-to-clipboard button (pure JS, no server round-trip)
        st.components.v1.html(
            f"""
            <textarea id="copy-source" style="display:none">{st.session_state.translation}</textarea>
            <button onclick="navigator.clipboard.writeText(document.getElementById('copy-source').value);
                              this.innerText='✅ Copied!';"
                    style="width:100%;padding:0.5em;border-radius:8px;border:1px solid #555;
                           background:#262730;color:white;cursor:pointer;">
                📋 Copy translation
            </button>
            """,
            height=50,
        )

    with col_b:
        target_code = languages[target_name]
        if is_tts_supported(target_code):
            if st.button("🔊 Listen (text-to-speech)", use_container_width=True):
                with st.spinner("Generating audio..."):
                    try:
                        audio_bytes = text_to_speech_bytes(st.session_state.translation, target_code)
                        st.audio(audio_bytes, format="audio/mp3")
                    except ValueError as e:
                        st.error(str(e))
        else:
            st.caption("🔇 Text-to-speech not available for this language.")

with st.expander("ℹ️ About this tool"):
    st.write(
        f"Supports **{len(languages) - 1} languages** (plus automatic source-language detection), "
        "powered by Google Translate via the `deep-translator` library. "
        "Text-to-speech is powered by `gTTS`."
    )
