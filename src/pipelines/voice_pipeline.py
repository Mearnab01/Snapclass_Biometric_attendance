import io
import numpy as np
import streamlit as st
import librosa

from resemblyzer import VoiceEncoder, preprocess_wav
from utils.logger import setup_logger

logger = setup_logger("voice_pipeline")


# ── Model loader ──────────────────────────────────────────────────────────────

@st.cache_resource
def _load_voice_encoder() -> VoiceEncoder:
    logger.info("loading VoiceEncoder model...")
    encoder = VoiceEncoder()
    logger.info("VoiceEncoder loaded successfully")
    return encoder


# ── Single embedding ──────────────────────────────────────────────────────────

def get_voice_embedding(audio_bytes: bytes) -> list | None:

    if not audio_bytes:
        logger.warning("audio_bytes is empty — skipping embedding")
        return None

    try:
        encoder   = _load_voice_encoder()
        audio, _  = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        wav       = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)

        return embedding.tolist()

    except Exception as e:
        logger.error("get_voice_embedding failed", exc_info=True)
        st.error("Voice recognition failed.")
        return None


# ── Speaker identification ────────────────────────────────────────────────────

def identify_speaker(
    new_embedding: list,
    candidates_dict: dict,
    threshold: float = 0.65
) -> tuple[str | None, float]:

    if not new_embedding or not candidates_dict:
        logger.warning("identify_speaker called with empty embedding or candidates")
        return None, 0.0

    emb        = np.array(new_embedding)
    best_sid   = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if not stored_embedding:
            logger.warning(f"student {sid} has no stored voice embedding — skipping")
            continue
        similarity = float(np.dot(emb, np.array(stored_embedding)))
        logger.info(f"similarity with student {sid}: {similarity:.4f}")
        if similarity > best_score:
            best_score = similarity
            best_sid   = sid

    if best_score >= threshold:
        return best_sid, best_score

    logger.warning(f"no match above threshold {threshold} — best score was {best_score:.4f}")
    return None, best_score


# ── Bulk audio processing ─────────────────────────────────────────────────────

def process_bulk_audio(
    audio_bytes: bytes,
    candidates_dict: dict,
    threshold: float = 0.65
) -> dict:

    try:
        encoder            = _load_voice_encoder()
        audio, sr          = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments           = librosa.effects.split(audio, top_db=30)
        identified_results = {}

        logger.info(f"audio loaded — {len(segments)} segments detected")

        for start, end in segments:
            duration = (end - start) / sr
            if (end - start) < sr * 0.5:
                logger.info(f"skipping segment [{start}:{end}] — too short ({duration:.2f}s)")
                continue

            segment    = audio[start:end]
            wav        = preprocess_wav(segment)
            emb        = encoder.embed_utterance(wav)

            sid, score = identify_speaker(emb.tolist(), candidates_dict, threshold)

            if sid and (sid not in identified_results or score > identified_results[sid]):
                identified_results[sid] = score
                logger.info(f"updated result — sid: {sid}, score: {score:.4f}")

        return identified_results

    except Exception as e:
        logger.error("process_bulk_audio failed", exc_info=True)
        st.error("Bulk audio processing failed.")
        return {}