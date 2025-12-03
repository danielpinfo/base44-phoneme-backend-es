import io
import re
from phonemizer import phonemize
from typing import List

import torch
import torchaudio
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

# Keep it light on small CPU instances
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

app = FastAPI(title="Base44 Spanish wav2vec2 Backend (Sharpened)")

TARGET_SR = 16000
MAX_SECONDS_SENTENCE = 10
MAX_SAMPLES_SENTENCE = TARGET_SR * MAX_SECONDS_SENTENCE

# Spanish CTC model
MODEL_NAME = "jonatasgrosman/wav2vec2-xls-r-1b-spanish"

processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
model.to("cpu")
model.eval()

# Spanish vowels (including accented + ü)
SPANISH_VOWELS = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")


def trim_silence(
    waveform: torch.Tensor,
    sr: int,
    threshold: float = 0.01,
) -> torch.Tensor:
    """
    Remove leading/trailing silence using a simple amplitude threshold.
    """
    if waveform.ndim != 1:
        waveform = waveform.view(-1)

    audio_np = waveform.numpy()
    energy = (audio_np ** 2) ** 0.5  # magnitude

    voiced = (energy > threshold).nonzero()[0]
    if len(voiced) == 0:
        # all silence – just return a short chunk to avoid empty tensors
        return waveform[: sr // 10]

    start = int(voiced[0])
    end = int(voiced[-1]) + 1

    margin = int(0.1 * sr)
    start = max(0, start - margin)
    end = min(len(audio_np), end + margin)

    return waveform[start:end]


def normalize_volume(waveform: torch.Tensor) -> torch.Tensor:
    """
    Normalize waveform so max absolute value is ~1.0.
    """
    max_val = waveform.abs().max()
    if max_val > 0:
        waveform = waveform / max_val
    return waveform


def load_and_resample_to_16k(wav_bytes: bytes) -> torch.Tensor:
    """
    Load WAV bytes, mono-ize, trim silence, normalize volume, resample to 16k,
    and cap to max length.
    """
    with io.BytesIO(wav_bytes) as buf:
        audio, sr = sf.read(buf, dtype="float32")

    # Stereo → mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    waveform = torch.from_numpy(audio)

    # 1) Trim silence at original sample rate
    waveform = trim_silence(waveform, sr)

    # 2) Resample to 16k
    if sr != TARGET_SR:
        waveform = torchaudio.functional.resample(
            waveform, orig_freq=sr, new_freq=TARGET_SR
        )

    # 3) Normalize volume
    waveform = normalize_volume(waveform)

    # 4) Cap to max length (10 seconds)
    if waveform.shape[0] > MAX_SAMPLES_SENTENCE:
        waveform = waveform[:MAX_SAMPLES_SENTENCE]

    return waveform


def cleanup_spanish_transcription(text: str) -> str:
    """
    Light cleanup to reduce 'sloppy' noise in Spanish transcriptions.
    - Lowercases
    - Collapses 3+ repeated consonants into 2 (e.g., 'holaaaa' -> 'holaa')
    """
    text = text.lower()

    # Collapse 3+ repeated consonants to 2
    def _collapse(match):
        ch = match.group(1)
        return ch * 2

    text = re.sub(r"([bcdfghjklmnñpqrstvwxyz])\1{2,}", _collapse, text)
    return text


def spanish_to_syllable_like_chunks(text: str) -> List[str]:
    """
    Very simple syllable-ish chunker for Spanish:
    - Groups consonant(s) + following vowel(s) together.
    - Example: 'mañana' -> ['ma', 'ña', 'na']
    Not perfect linguistic segmentation — practical for Base44 phoneme UI.
    """
    if not text:
        return []

    chars = list(text)
    chunks: List[str] = []
    current = ""

    i = 0
    n = len(chars)

    while i < n:
        ch = chars[i]
        current += ch

        # If this char is a vowel, chunk boundary
        if ch in SPANISH_VOWELS:
            # Look ahead for diphthong / vowel clusters
            j = i + 1
            while j < n and chars[j] in SPANISH_VOWELS:
                current += chars[j]
                i = j
                j += 1

            chunks.append(current)
            current = ""

        i += 1

    if current:
        chunks.append(current)

    return chunks

def text_to_ipa_units(text: str) -> List[str]:
    """
    Real IPA for Spanish using espeak-ng via phonemizer.
    Example: 'caja' -> ['ˈka', 'xa']
    """
    if not text:
        return []

    ipa = phonemize(
        text,
        language="es",
        backend="espeak",
        strip=True,
        with_stress=True,
        preserve_punctuation=False,
        separator=" "
    )

    raw_units = ipa.split()
    units: List[str] = []

    for unit in raw_units:
        # split on syllable dots
        pieces = unit.split(".")
        for p in pieces:
            if p:
                units.append(p)

    return units

@app.get("/languages")
async def list_languages():
    """Returns supported languages (Spanish-only service)."""
    return [
        {
            "code": "es",
            "nativeName": "Español",
            "englishName": "Spanish",
            "flag": "🇪🇸",
        }
    ]


@app.get("/practice-words")
async def get_practice_words(
    lang: str = Query("es", description="Language code: es"),
):
    """Simple Spanish practice words."""
    if lang != "es":
        raise HTTPException(status_code=400, detail=f"Unsupported language '{lang}'")

    return {
        "lang": "es",
        "words": [
            {"id": "hola", "text": "hola", "translation": "hello", "hint": "Saludo básico"},
            {"id": "gracias", "text": "gracias", "translation": "thank you", "hint": "Frase de cortesía"},
            {"id": "agua", "text": "agua", "translation": "water", "hint": "Sustantivo común"},
        ],
    }


@app.post("/phonemes")
async def phonemes(
    file: UploadFile = File(...),
    lang: str = Query("es", description="Language code: es"),
):
    """
    Accepts a WAV file (16k preferred) and returns:
    - Spanish transcription
    - Grapheme 'phoneme' segmentation
    - Real IPA units (via phonemizer + espeak-ng)
    - Base44 from IPA
    """
    if lang != "es":
        raise HTTPException(status_code=400, detail=f"Unsupported language '{lang}'")

    if file.content_type not in (
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/vnd.wave",
        None,
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content-type {file.content_type}. Upload a WAV file.",
        )

    try:
        wav_bytes = await file.read()
        waveform = load_and_resample_to_16k(wav_bytes)

        with torch.no_grad():
            inputs = processor(
                waveform, sampling_rate=TARGET_SR, return_tensors="pt"
            )
            logits = model(inputs.input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            decoded = processor.batch_decode(predicted_ids)

            transcription = decoded[0].strip() if decoded else ""
            transcription = cleanup_spanish_transcription(transcription)

            # Keep only letters and apostrophes
            cleaned = "".join(ch for ch in transcription if ch.isalpha() or ch == "'")

            # Old grapheme chunks (for UI if you want)
            chunks = spanish_to_syllable_like_chunks(cleaned)
            spaced_chunks = " ".join(chunks) if chunks else ""

            # NEW: real IPA units via phonemizer + espeak-ng
            ipa_units = text_to_ipa_units(cleaned)

            # NEW: Base44 from IPA
            base44_units = ipa_to_base44_units(ipa_units)

        return JSONResponse(
            content={
                "lang": "es",
                "phonemes": spaced_chunks,       # grapheme chunks (ma, ña, na)
                "ipa_units": ipa_units,          # real IPA units
                "base44": base44_units,          # Base44 mapped from IPA
                "raw_transcription": transcription,
                "model": MODEL_NAME,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phoneme recognition failed: {e}")



    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phoneme recognition failed: {e}")
