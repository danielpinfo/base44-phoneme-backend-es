from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import torch
import torchaudio
import soundfile as sf
import io
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

app = FastAPI(title="Base44 Spanish wav2vec2 Backend")

TARGET_SR = 16000
MAX_SECONDS_SENTENCE = 10
MAX_SAMPLES_SENTENCE = TARGET_SR * MAX_SECONDS_SENTENCE

MODEL_NAME = "jonatasgrosman/wav2vec2-large-xlsr-53-spanish"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
model.to("cpu")
model.eval()

def load_and_resample(wav_bytes: bytes):
    with io.BytesIO(wav_bytes) as buf:
        audio, sr = sf.read(buf, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    waveform = torch.from_numpy(audio)
    if sr != TARGET_SR:
        waveform = torchaudio.functional.resample(waveform, sr, TARGET_SR)
    if waveform.shape[0] > MAX_SAMPLES_SENTENCE:
        waveform = waveform[:MAX_SAMPLES_SENTENCE]
    return waveform

@app.post("/phonemes")
async def phonemes(file: UploadFile = File(...), lang: str = Query("es")):
    try:
        wav_bytes = await file.read()
        waveform = load_and_resample(wav_bytes)
        with torch.no_grad():
            inputs = processor(waveform, sampling_rate=TARGET_SR, return_tensors="pt")
            logits = model(inputs.input_values).logits
            ids = torch.argmax(logits, dim=-1)
            decoded = processor.batch_decode(ids)[0].strip().lower()
            cleaned = "".join(ch for ch in decoded if ch.isalpha() or ch == "'")
            spaced = " ".join(list(cleaned))
        return JSONResponse({"lang": "es", "phonemes": spaced, "raw_transcription": decoded, "model": MODEL_NAME})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
