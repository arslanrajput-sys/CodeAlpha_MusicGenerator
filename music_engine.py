from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from music21 import chord, instrument, note, stream

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
GENERATED_DIR = BASE_DIR / "generated"
MODEL_PATH = MODEL_DIR / "music_model.keras"
VOCAB_PATH = MODEL_DIR / "vocab.json"
SEED_PATH = MODEL_DIR / "seed_sequences.json"

GENERATED_DIR.mkdir(exist_ok=True)

STYLE_CONFIG = {
    "classical": {
        "scale": [60, 62, 64, 65, 67, 69, 71, 72],
        "tempo": 92,
        "velocity": 76,
        "durations": [0.25, 0.5, 0.5, 1.0],
    },
    "jazz": {
        "scale": [60, 62, 63, 65, 67, 69, 70, 72],
        "tempo": 112,
        "velocity": 82,
        "durations": [0.25, 0.5, 0.75, 1.0],
    },
    "ambient": {
        "scale": [60, 62, 64, 67, 69, 72, 74],
        "tempo": 72,
        "velocity": 64,
        "durations": [0.5, 1.0, 1.5, 2.0],
    },
    "cinematic": {
        "scale": [57, 60, 62, 64, 65, 67, 69, 72],
        "tempo": 84,
        "velocity": 88,
        "durations": [0.25, 0.5, 1.0, 1.5],
    },
}


def _load_model_bundle():
    if not (MODEL_PATH.exists() and VOCAB_PATH.exists() and SEED_PATH.exists()):
        return None

    try:
        from tensorflow.keras.models import load_model

        model = load_model(MODEL_PATH)
        vocab = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        seeds = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        return model, vocab, seeds
    except Exception:
        return None


def _token_to_event(token: str) -> Tuple[List[int], float]:
    if "|" in token:
        pitch_part, duration_part = token.rsplit("|", 1)
        duration = float(duration_part)
    else:
        pitch_part, duration = token, 0.5

    if "." in pitch_part:
        pitches = [int(p) for p in pitch_part.split(".")]
    else:
        pitches = [int(pitch_part)]
    return pitches, duration


def _model_generate(length: int, temperature: float):
    bundle = _load_model_bundle()
    if bundle is None:
        return None

    model, vocab, seeds = bundle
    token_to_int: Dict[str, int] = vocab["token_to_int"]
    int_to_token = {int(k): v for k, v in vocab["int_to_token"].items()}
    sequence_length = int(vocab["sequence_length"])
    n_vocab = len(token_to_int)

    pattern = random.choice(seeds)
    output_tokens: List[str] = []

    for _ in range(length):
        x = np.reshape(pattern, (1, sequence_length, 1)).astype("float32")
        x /= float(n_vocab)
        prediction = model.predict(x, verbose=0)[0]

        prediction = np.asarray(prediction, dtype=np.float64)
        prediction = np.log(np.maximum(prediction, 1e-9)) / max(temperature, 0.1)
        exp_prediction = np.exp(prediction - np.max(prediction))
        probabilities = exp_prediction / exp_prediction.sum()
        index = int(np.random.choice(len(probabilities), p=probabilities))

        output_tokens.append(int_to_token[index])
        pattern = pattern[1:] + [index]

    return [_token_to_event(token) for token in output_tokens]


def _demo_generate(style: str, length: int, creativity: float):
    cfg = STYLE_CONFIG.get(style, STYLE_CONFIG["classical"])
    scale = cfg["scale"]
    durations = cfg["durations"]

    tonic_index = random.randint(0, max(0, len(scale) - 3))
    current = tonic_index
    events = []

    phrase = [0, 1, 2, 4, 3, 2, 1, 0]
    jazz_chance = 0.14 if style == "jazz" else 0.06
    chord_chance = 0.12 if style in {"cinematic", "ambient"} else jazz_chance

    for i in range(length):
        if i % 8 == 0 and i > 0:
            current = max(0, min(len(scale) - 1, tonic_index + random.choice([-1, 0, 1])))

        phrase_target = phrase[i % len(phrase)] + tonic_index
        drift = random.choice([-1, 0, 0, 0, 1]) if creativity < 1.15 else random.choice([-2, -1, 0, 1, 2])
        current = max(0, min(len(scale) - 1, phrase_target + drift))
        root = scale[current]

        if random.random() < chord_chance:
            third_index = min(current + 2, len(scale) - 1)
            fifth_index = min(current + 4, len(scale) - 1)
            pitches = sorted(set([root, scale[third_index], scale[fifth_index]]))
        else:
            octave_shift = 12 if random.random() < 0.12 else 0
            pitches = [root + octave_shift]

        duration = random.choice(durations)
        events.append((pitches, duration))

    return events


def _events_to_midi(events, style: str, filename: str):
    cfg = STYLE_CONFIG.get(style, STYLE_CONFIG["classical"])
    score = stream.Stream()
    score.insert(0, instrument.Piano())

    offset = 0.0
    for pitches, duration in events:
        if len(pitches) == 1:
            element = note.Note(pitches[0])
        else:
            element = chord.Chord(pitches)
        element.duration.quarterLength = float(duration)
        element.volume.velocity = cfg["velocity"]
        score.insert(offset, element)
        offset += float(duration)

    out_path = GENERATED_DIR / filename
    score.write("midi", fp=str(out_path))
    return out_path


def generate_music(style: str = "classical", length: int = 96, creativity: float = 0.9):
    style = style if style in STYLE_CONFIG else "classical"
    length = max(24, min(int(length), 240))
    creativity = max(0.2, min(float(creativity), 1.8))

    events = _model_generate(length, creativity)
    source = "trained-lstm"
    if events is None:
        events = _demo_generate(style, length, creativity)
        source = "demo-engine"

    filename = f"melody-{random.randint(100000, 999999)}.mid"
    _events_to_midi(events, style, filename)

    cfg = STYLE_CONFIG[style]
    web_events = []
    cursor = 0.0
    for pitches, duration in events:
        web_events.append(
            {
                "pitches": pitches,
                "duration": float(duration),
                "start": round(cursor, 3),
            }
        )
        cursor += float(duration)

    return {
        "filename": filename,
        "events": web_events,
        "tempo": cfg["tempo"],
        "style": style,
        "source": source,
        "bars": max(1, round(cursor / 4)),
        "duration_beats": round(cursor, 2),
    }
