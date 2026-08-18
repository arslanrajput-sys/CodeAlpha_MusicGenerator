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

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

STYLE_CONFIG = {
    "classical": {
        "scale": MAJOR_SCALE,
        "tempo": 118,
        "tempo_range": (112, 124),
        "tonics": [(60, "C"), (62, "D"), (65, "F")],
        "progression": [0, 4, 5, 3],
        "contour": [0, 1, 2, 4, 3, 2, 1, 0],
        "melody_rhythms": [
            [0.5] * 8,
            [1.0, 0.5, 0.5, 1.0, 1.0],
            [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
        ],
    },
    "jazz": {
        "scale": MAJOR_SCALE,
        "tempo": 128,
        "tempo_range": (122, 136),
        "tonics": [(58, "Bb"), (60, "C"), (65, "F")],
        "progression": [1, 4, 0, 5],
        "contour": [0, 2, 1, 3, 2, 4, 2, 1],
        "melody_rhythms": [
            [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
            [0.75, 0.25, 0.5, 0.5, 1.0, 1.0],
            [1.0, 0.5, 0.5, 0.5, 0.5, 1.0],
        ],
    },
    "ambient": {
        "scale": MAJOR_SCALE,
        "tempo": 98,
        "tempo_range": (92, 104),
        "tonics": [(60, "C"), (62, "D"), (67, "G")],
        "progression": [0, 5, 3, 4],
        "contour": [0, 2, 4, 2, 1, 3, 2, 0],
        "melody_rhythms": [
            [1.0, 1.0, 2.0],
            [1.5, 0.5, 1.0, 1.0],
            [2.0, 1.0, 1.0],
        ],
    },
    "cinematic": {
        "scale": MINOR_SCALE,
        "tempo": 114,
        "tempo_range": (108, 122),
        "tonics": [(57, "A minor"), (60, "C minor"), (62, "D minor")],
        "progression": [0, 5, 2, 6],
        "contour": [0, 1, 3, 4, 3, 1, 0, -1],
        "melody_rhythms": [
            [0.5] * 8,
            [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
            [1.0, 0.5, 0.5, 1.0, 1.0],
        ],
    },
    "ghazal darbari": {
        # Darbari Kanada uses the Asavari-note collection:
        # Sa Re komal-ga Ma Pa komal-dha komal-ni.
        "scale": MINOR_SCALE,
        "tempo": 98,
        "tempo_range": (94, 104),
        "tonics": [(60, "C"), (62, "D")],
        # The dedicated Darbari generator below uses phrase grammar rather
        # than Western chord progressions.
        "progression": [0],
        "contour": [0, 1, 2, 1, 0, -1, 0, 1],
        "melody_rhythms": [[0.5] * 8],
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


def _scale_pitch(tonic: int, scale: List[int], degree: int, octave_shift: int = 0) -> int:
    octave, index = divmod(int(degree), 7)
    return tonic + scale[index] + (12 * octave) + (12 * octave_shift)


def _chord_degrees(root_degree: int, seventh: bool = False) -> List[int]:
    degrees = [root_degree, root_degree + 2, root_degree + 4]
    if seventh:
        degrees.append(root_degree + 6)
    return degrees


def _chord_pitches(
    tonic: int,
    scale: List[int],
    root_degree: int,
    register: int = -1,
    seventh: bool = False,
) -> List[int]:
    return [
        _scale_pitch(tonic, scale, degree, register)
        for degree in _chord_degrees(root_degree, seventh=seventh)
    ]


def _add_event(
    events: List[dict],
    pitches: List[int],
    start: float,
    duration: float,
    role: str,
    velocity: int,
):
    cleaned = sorted({max(28, min(96, int(p))) for p in pitches})
    if not cleaned:
        return
    events.append(
        {
            "pitches": cleaned,
            "start": round(float(start), 3),
            "duration": round(float(duration), 3),
            "role": role,
            "velocity": max(30, min(120, int(velocity))),
        }
    )


def _nearest_chord_degree(current_degree: int, root_degree: int, seventh: bool = False) -> int:
    tones = _chord_degrees(root_degree, seventh=seventh)
    candidates: List[int] = []
    for tone in tones:
        for octave in range(-1, 4):
            candidates.append(tone + (7 * octave))
    return min(candidates, key=lambda d: abs(d - current_degree))


def _add_harmony_and_bass(
    events: List[dict],
    style: str,
    tonic: int,
    scale: List[int],
    root_degree: int,
    next_root_degree: int,
    bar_start: float,
):
    if style == "classical":
        chord_p = _chord_pitches(tonic, scale, root_degree, register=-1)
        arpeggio = [0, 1, 2, 1, 0, 1, 2, 1]
        for i, chord_index in enumerate(arpeggio):
            _add_event(
                events,
                [chord_p[chord_index]],
                bar_start + (i * 0.5),
                0.44,
                "harmony",
                58 + (4 if i in {0, 4} else 0),
            )

        root = _scale_pitch(tonic, scale, root_degree, octave_shift=-2)
        fifth = _scale_pitch(tonic, scale, root_degree + 4, octave_shift=-2)
        _add_event(events, [root], bar_start, 1.8, "bass", 68)
        _add_event(events, [fifth], bar_start + 2.0, 1.8, "bass", 64)

    elif style == "jazz":
        chord_p = _chord_pitches(tonic, scale, root_degree, register=-1, seventh=True)
        _add_event(events, chord_p, bar_start, 1.65, "harmony", 62)
        _add_event(events, chord_p, bar_start + 2.0, 1.65, "harmony", 57)

        walk = [
            root_degree,
            root_degree + 2,
            root_degree + 4,
            next_root_degree - 1 if next_root_degree > root_degree else next_root_degree + 6,
        ]
        for beat, degree in enumerate(walk):
            pitch = _scale_pitch(tonic, scale, degree, octave_shift=-2)
            _add_event(events, [pitch], bar_start + beat, 0.86, "bass", 70 if beat == 0 else 64)

    elif style == "ambient":
        chord_p = _chord_pitches(tonic, scale, root_degree, register=-1)
        widened = [chord_p[0], chord_p[1], chord_p[2], chord_p[0] + 12]
        _add_event(events, widened, bar_start, 3.8, "harmony", 48)
        root = _scale_pitch(tonic, scale, root_degree, octave_shift=-2)
        _add_event(events, [root], bar_start, 3.7, "bass", 54)

    else:  # cinematic
        chord_p = _chord_pitches(tonic, scale, root_degree, register=-1)
        widened = [chord_p[0], chord_p[1], chord_p[2], chord_p[0] + 12]
        _add_event(events, widened, bar_start, 3.7, "harmony", 64)

        bass_root = _scale_pitch(tonic, scale, root_degree, octave_shift=-2)
        bass_fifth = _scale_pitch(tonic, scale, root_degree + 4, octave_shift=-2)
        pulse = [bass_root, bass_root, bass_fifth, bass_root, bass_root, bass_fifth, bass_root, bass_fifth]
        for i, pitch in enumerate(pulse):
            _add_event(
                events,
                [pitch],
                bar_start + (i * 0.5),
                0.42,
                "bass",
                74 if i in {0, 4} else 64,
            )


def _add_melody_bar(
    events: List[dict],
    cfg: dict,
    style: str,
    tonic: int,
    scale: List[int],
    root_degree: int,
    bar_index: int,
    bar_start: float,
    current_degree: int,
    creativity: float,
    final_bar: bool,
) -> int:
    rhythm = random.choice(cfg["melody_rhythms"])
    contour = cfg["contour"]
    seventh = style == "jazz"
    cursor = 0.0

    for note_index, duration in enumerate(rhythm):
        strong_beat = abs((cursor % 2.0)) < 0.001
        contour_index = (bar_index * 2 + note_index) % len(contour)
        phrase_target = 7 + root_degree + contour[contour_index]

        if strong_beat:
            target_degree = _nearest_chord_degree(
                phrase_target, root_degree + 7, seventh=seventh
            )
        else:
            step = random.choices(
                [-2, -1, 0, 1, 2],
                weights=[1, 4, 2, 5, 1],
                k=1,
            )[0]
            target_degree = current_degree + step

            if random.random() < min(0.38, max(0.08, creativity * 0.18)):
                target_degree += random.choice([-1, 1])

        if final_bar and note_index == len(rhythm) - 1:
            tonic_candidates = [7, 14, 21]
            target_degree = min(tonic_candidates, key=lambda d: abs(d - current_degree))
            duration = max(duration, 1.0)

        max_jump = 4 if creativity < 1.1 else 6
        if target_degree - current_degree > max_jump:
            target_degree = current_degree + max_jump
        elif current_degree - target_degree > max_jump:
            target_degree = current_degree - max_jump

        current_degree = max(4, min(20, target_degree))
        pitch = _scale_pitch(tonic, scale, current_degree)

        velocity_base = {
            "classical": 82,
            "jazz": 88,
            "ambient": 72,
            "cinematic": 90,
        }[style]
        velocity = velocity_base + random.randint(-5, 6)
        if strong_beat:
            velocity += 5

        _add_event(
            events,
            [pitch],
            bar_start + cursor,
            max(0.18, duration * 0.90),
            "melody",
            velocity,
        )
        cursor += float(duration)

    return current_degree


def _inject_model_influence(
    events: List[dict],
    model_events: List[Tuple[List[int], float]],
    tonic: int,
    scale: List[int],
    creativity: float,
):
    if not model_events:
        return

    melody_events = [event for event in events if event.get("role") == "melody"]
    if not melody_events:
        return

    influence = min(0.42, max(0.14, creativity * 0.22))
    model_index = 0

    allowed = []
    for degree in range(4, 22):
        allowed.append(_scale_pitch(tonic, scale, degree))

    for event in melody_events:
        if random.random() > influence:
            continue

        pitches, _duration = model_events[model_index % len(model_events)]
        model_index += 1
        if not pitches:
            continue

        source_pitch = int(pitches[0])
        while source_pitch < 60:
            source_pitch += 12
        while source_pitch > 88:
            source_pitch -= 12

        fitted = min(allowed, key=lambda p: abs(p - source_pitch))
        event["pitches"] = [fitted]


def _generate_darbari_arrangement(length: int, creativity: float):
    """
    Ghazal-inspired Raag Darbari Kanada arrangement.

    This deliberately avoids Western chord changes. It uses a Sa-Pa drone,
    restrained low-register bass support, and Darbari-shaped melodic phrases
    around komal ga / komal dha / komal ni.
    """
    cfg = STYLE_CONFIG["ghazal darbari"]
    scale = cfg["scale"]
    tonic, tonic_name = random.choice(cfg["tonics"])
    tempo = random.randint(*cfg["tempo_range"])
    bars = max(8, min(28, int(round(length / 6))))
    events: List[dict] = []

    # Degree numbers are relative to the Darbari scale:
    # 0=S, 1=R, 2=g, 3=M, 4=P, 5=d, 6=n, 7=S'.
    phrases = [
        [7, 8, 9, 8, 7, 6, 7, 8],          # S R g R S n S R
        [7, 8, 9, 10, 11, 10, 9, 8],       # S R g M P M g R
        [11, 13, 11, 10, 11, 9, 10, 8],    # P n P M P g M R
        [14, 12, 13, 11, 10, 11, 9, 8],    # S' d n P M P g R
        [8, 9, 10, 11, 13, 11, 10, 9],     # R g M P n P M g
        [6, 7, 8, 9, 8, 7, 6, 7],          # n S R g R S n S
        [7, 8, 9, 10, 11, 12, 13, 14],     # measured ascent
        [14, 12, 13, 11, 10, 11, 9, 10],   # vakra descent
    ]
    rhythms = [
        [0.5] * 8,
        [0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5, 0.5],
        [0.5, 0.5, 0.75, 0.25, 0.5, 0.5, 0.5, 0.5],
    ]

    phrase_order = [0, 1, 2, 0, 4, 3, 2, 5]

    for bar_index in range(bars):
        bar_start = bar_index * 4.0

        # Sa-Pa drone: the harmonic bed used instead of chord progressions.
        drone_low_sa = tonic - 12
        drone_pa = tonic - 5
        _add_event(
            events,
            [drone_low_sa, drone_pa, tonic],
            bar_start,
            3.92,
            "harmony",
            45 if bar_index % 2 else 49,
        )

        # A restrained pulse underneath the melody. It reads like a soft
        # ghazal accompaniment in the browser synth without introducing
        # out-of-raga harmony.
        low_sa = tonic - 24
        low_pa = tonic - 17
        pulse_positions = [0.0, 1.5, 2.0, 3.5]
        pulse_notes = [low_sa, low_pa, low_sa, low_pa]
        for i, (pos, pitch) in enumerate(zip(pulse_positions, pulse_notes)):
            _add_event(
                events,
                [pitch],
                bar_start + pos,
                0.34 if i in {1, 3} else 0.48,
                "bass",
                59 if i == 0 else 51,
            )

        phrase_index = phrase_order[bar_index % len(phrase_order)]
        if creativity > 1.15 and random.random() < 0.30:
            phrase_index = random.randrange(len(phrases))
        phrase = list(phrases[phrase_index])

        # Keep the final cadence unmistakably on Sa.
        if bar_index == bars - 1:
            phrase = [11, 9, 10, 8, 7, 8, 7, 7]

        rhythm = random.choice(rhythms)
        cursor = 0.0

        for note_index, (degree, duration) in enumerate(zip(phrase, rhythm)):
            # Small controlled phrase variation without leaving the raga.
            if (
                creativity > 0.9
                and 0 < note_index < len(phrase) - 1
                and random.random() < min(0.18, (creativity - 0.75) * 0.18)
            ):
                shift = random.choice([-1, 1])
                candidate = degree + shift
                if 5 <= candidate <= 15:
                    degree = candidate

            pitch = _scale_pitch(tonic, scale, degree)

            # Komal ga and dha get slightly more space/weight. Real Darbari
            # uses meend/andolan; MIDI cannot reproduce that nuance perfectly,
            # so the phrase grammar and sustained treatment carry the effect.
            scale_index = degree % 7
            emphasis = 5 if scale_index in {2, 5} else 0
            velocity = 78 + emphasis + random.randint(-4, 5)

            _add_event(
                events,
                [pitch],
                bar_start + cursor,
                max(0.22, duration * (0.94 if scale_index in {2, 5} else 0.88)),
                "melody",
                velocity,
            )
            cursor += duration

        # Every fourth bar adds a soft response phrase around Pa-n-P-M-P-g.
        if bar_index % 4 == 3 and bar_index != bars - 1:
            response = [11, 13, 11, 10, 11, 9]
            response_start = bar_start + 2.0
            for i, degree in enumerate(response):
                _add_event(
                    events,
                    [_scale_pitch(tonic, scale, degree)],
                    response_start + (i * 0.31),
                    0.25,
                    "melody",
                    62 + (3 if degree % 7 == 2 else 0),
                )

    events.sort(key=lambda event: (event["start"], event["role"]))
    return events, tempo, bars, f"{tonic_name} · Raag Darbari", "raga-engine"


def _generate_arrangement(style: str, length: int, creativity: float):
    if style == "ghazal darbari":
        return _generate_darbari_arrangement(length, creativity)

    cfg = STYLE_CONFIG[style]
    scale = cfg["scale"]
    tonic, key_name = random.choice(cfg["tonics"])
    tempo = random.randint(*cfg["tempo_range"])

    bars = max(8, min(28, int(round(length / 6))))
    progression = cfg["progression"]
    events: List[dict] = []
    current_degree = 9

    for bar_index in range(bars):
        root_degree = progression[bar_index % len(progression)]
        next_root_degree = progression[(bar_index + 1) % len(progression)]
        bar_start = bar_index * 4.0

        _add_harmony_and_bass(
            events,
            style,
            tonic,
            scale,
            root_degree,
            next_root_degree,
            bar_start,
        )

        current_degree = _add_melody_bar(
            events,
            cfg,
            style,
            tonic,
            scale,
            root_degree,
            bar_index,
            bar_start,
            current_degree,
            creativity,
            final_bar=bar_index == bars - 1,
        )

    model_events = _model_generate(max(32, bars * 4), creativity)
    source = "arrangement-engine"
    if model_events is not None:
        _inject_model_influence(events, model_events, tonic, scale, creativity)
        source = "trained-lstm"

    events.sort(key=lambda event: (event["start"], event["role"]))
    return events, tempo, bars, key_name, source


def _events_to_midi(events: List[dict], filename: str):
    score = stream.Score()

    for role in ("harmony", "bass", "melody"):
        part = stream.Part()
        part.id = role.title()
        part.insert(0, instrument.Piano())

        for event in events:
            if event.get("role") != role:
                continue

            pitches = event["pitches"]
            if len(pitches) == 1:
                element = note.Note(pitches[0])
            else:
                element = chord.Chord(pitches)

            element.duration.quarterLength = float(event["duration"])
            element.volume.velocity = int(event.get("velocity", 72))
            part.insert(float(event["start"]), element)

        score.insert(0, part)

    out_path = GENERATED_DIR / filename
    score.write("midi", fp=str(out_path))
    return out_path


def generate_music(style: str = "classical", length: int = 96, creativity: float = 0.9):
    style = style if style in STYLE_CONFIG else "classical"
    length = max(48, min(int(length), 200))
    creativity = max(0.3, min(float(creativity), 1.6))

    events, tempo, bars, key_name, source = _generate_arrangement(
        style, length, creativity
    )

    filename = f"composition-{random.randint(100000, 999999)}.mid"
    _events_to_midi(events, filename)

    return {
        "filename": filename,
        "events": events,
        "tempo": tempo,
        "style": style,
        "source": source,
        "bars": bars,
        "key": key_name,
        "duration_beats": bars * 4,
    }
