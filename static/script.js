/**
 * Language Translator — frontend logic.
 *
 * This file talks to the Flask backend (api.py) via three JSON endpoints:
 *   GET  /api/languages              -> { languages: [{name, code}, ...] }
 *   POST /api/translate               -> { translation } | { error }
 *   POST /api/tts                     -> raw MP3 bytes    | { error }
 *
 * If you plug this UI into a different backend, you only need to edit
 * the three functions in the "API CALLS" section below — everything
 * else (DOM wiring, animations, state) can stay as-is.
 */

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const sourceLangSelect = document.getElementById("source-lang");
const targetLangSelect = document.getElementById("target-lang");
const swapBtn = document.getElementById("swap-btn");

const sourceText = document.getElementById("source-text");
const targetText = document.getElementById("target-text");
const sourceCount = document.getElementById("source-count");
const targetStatus = document.getElementById("target-status");

const translateBtn = document.getElementById("translate-btn");
const copyBtn = document.getElementById("copy-btn");
const listenSourceBtn = document.getElementById("listen-source-btn");
const listenTargetBtn = document.getElementById("listen-target-btn");

const audioSource = document.getElementById("audio-source");
const audioTarget = document.getElementById("audio-target");

const errorBanner = document.getElementById("error-banner");

const MAX_CHARS = 5000;

// ---------------------------------------------------------------------------
// API CALLS — edit these three functions to plug in a different backend
// ---------------------------------------------------------------------------

/** Fetches the list of supported languages: [{name, code}, ...] */
async function fetchLanguages() {
  const res = await fetch("/api/languages");
  if (!res.ok) throw new Error("Could not load the language list.");
  const data = await res.json();
  return data.languages;
}

/** Translates `text` from `source` to `target` language codes. Returns a string. */
async function fetchTranslation(text, source, target) {
  const res = await fetch("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, source, target }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Translation failed.");
  return data.translation;
}

/** Requests text-to-speech audio for `text` in `lang`. Returns an object URL for an <audio> tag. */
async function fetchSpeechAudioUrl(text, lang) {
  const res = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, lang }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || "Text-to-speech failed.");
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

// ---------------------------------------------------------------------------
// Error banner helper
// ---------------------------------------------------------------------------
function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}

function clearError() {
  errorBanner.hidden = true;
  errorBanner.textContent = "";
}

// ---------------------------------------------------------------------------
// Language dropdowns
// ---------------------------------------------------------------------------
function populateLanguageSelect(select, languages, { includeAuto }) {
  select.innerHTML = "";
  for (const lang of languages) {
    if (lang.code === "auto" && !includeAuto) continue;
    const option = document.createElement("option");
    option.value = lang.code;
    option.textContent = capitalize(lang.name);
    select.appendChild(option);
  }
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

async function initLanguages() {
  try {
    const languages = await fetchLanguages();

    populateLanguageSelect(sourceLangSelect, languages, { includeAuto: true });
    populateLanguageSelect(targetLangSelect, languages, { includeAuto: false });

    // Sensible defaults: source = auto-detect, target = French if available, else 2nd language
    sourceLangSelect.value = "auto";
    const preferredTarget = languages.find((l) => l.code === "fr");
    targetLangSelect.value = preferredTarget ? "fr" : languages[1]?.code ?? "en";
  } catch (err) {
    showError(err.message);
  }
}

// ---------------------------------------------------------------------------
// Swap languages
// ---------------------------------------------------------------------------
swapBtn.addEventListener("click", () => {
  // "auto" has no real slot on the target side, so skip the swap in that case
  if (sourceLangSelect.value === "auto") return;

  const tmp = sourceLangSelect.value;
  sourceLangSelect.value = targetLangSelect.value;
  targetLangSelect.value = tmp;

  // Move the text over too, for a natural "reverse translation" flow
  const tmpText = sourceText.value;
  sourceText.value = targetText.value;
  targetText.value = tmpText;
  updateCharCount();

  swapBtn.classList.add("is-spinning");
  setTimeout(() => swapBtn.classList.remove("is-spinning"), 450);
});

// ---------------------------------------------------------------------------
// Character counter
// ---------------------------------------------------------------------------
function updateCharCount() {
  sourceCount.textContent = `${sourceText.value.length} / ${MAX_CHARS}`;
}
sourceText.addEventListener("input", updateCharCount);

// ---------------------------------------------------------------------------
// Translate action
// ---------------------------------------------------------------------------
async function handleTranslate() {
  clearError();

  const text = sourceText.value.trim();
  if (!text) {
    showError("Please enter some text to translate.");
    return;
  }

  setTranslateLoading(true);
  targetStatus.textContent = "Translating…";

  try {
    const translation = await fetchTranslation(
      text,
      sourceLangSelect.value,
      targetLangSelect.value
    );
    targetText.value = translation;
    targetStatus.textContent = `${translation.length} characters`;
  } catch (err) {
    showError(err.message);
    targetStatus.textContent = "";
  } finally {
    setTranslateLoading(false);
  }
}

function setTranslateLoading(isLoading) {
  translateBtn.classList.toggle("is-loading", isLoading);
  translateBtn.disabled = isLoading;
}

translateBtn.addEventListener("click", handleTranslate);

// Convenience: Ctrl/Cmd + Enter triggers translation from the source textarea
sourceText.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    handleTranslate();
  }
});

// ---------------------------------------------------------------------------
// Copy button
// ---------------------------------------------------------------------------
copyBtn.addEventListener("click", async () => {
  if (!targetText.value) return;

  try {
    await navigator.clipboard.writeText(targetText.value);
    flashSuccess(copyBtn);
  } catch (err) {
    showError("Could not copy to clipboard.");
  }
});

function flashSuccess(button) {
  button.classList.add("is-success");
  setTimeout(() => button.classList.remove("is-success"), 1200);
}

// ---------------------------------------------------------------------------
// Listen buttons (text-to-speech)
// ---------------------------------------------------------------------------
async function handleListen(button, textValue, langCode, audioEl) {
  if (!textValue.trim()) return;

  button.classList.add("is-loading");
  clearError();

  try {
    const url = await fetchSpeechAudioUrl(textValue, langCode);
    audioEl.src = url;
    await audioEl.play();
  } catch (err) {
    showError(err.message);
  } finally {
    button.classList.remove("is-loading");
  }
}

listenSourceBtn.addEventListener("click", () => {
  const lang = sourceLangSelect.value === "auto" ? "en" : sourceLangSelect.value;
  handleListen(listenSourceBtn, sourceText.value, lang, audioSource);
});

listenTargetBtn.addEventListener("click", () => {
  handleListen(listenTargetBtn, targetText.value, targetLangSelect.value, audioTarget);
});

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
initLanguages();
updateCharCount();
