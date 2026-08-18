from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import LSTM, BatchNormalization, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical

BASE_DIR = Path(__file__).resolve().parent
SONGS_PATH = BASE_DIR / "data" / "processed" / "songs.json"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

SEQUENCE_LENGTH = 64


def load_tokens():
    if not SONGS_PATH.exists():
        raise SystemExit("Run `python preprocess.py` first.")

    songs = json.loads(SONGS_PATH.read_text(encoding="utf-8"))
    all_tokens = []
    for song in songs:
        all_tokens.extend(song["tokens"])
    return all_tokens


def build_dataset(tokens):
    vocab = sorted(set(tokens))
    token_to_int = {token: i for i, token in enumerate(vocab)}
    int_to_token = {i: token for token, i in token_to_int.items()}

    network_input = []
    network_output = []

    for i in range(len(tokens) - SEQUENCE_LENGTH):
        seq_in = tokens[i : i + SEQUENCE_LENGTH]
        seq_out = tokens[i + SEQUENCE_LENGTH]
        network_input.append([token_to_int[token] for token in seq_in])
        network_output.append(token_to_int[seq_out])

    x = np.reshape(network_input, (len(network_input), SEQUENCE_LENGTH, 1)).astype("float32")
    x /= float(len(vocab))
    y = to_categorical(network_output, num_classes=len(vocab))

    return x, y, network_input, token_to_int, int_to_token


def build_model(input_shape, n_vocab):
    model = Sequential(
        [
            LSTM(256, input_shape=input_shape, return_sequences=True),
            Dropout(0.25),
            LSTM(256, return_sequences=True),
            BatchNormalization(),
            Dropout(0.25),
            LSTM(128),
            Dense(128, activation="relu"),
            Dropout(0.2),
            Dense(n_vocab, activation="softmax"),
        ]
    )
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model


def main():
    tokens = load_tokens()
    if len(tokens) < SEQUENCE_LENGTH + 100:
        raise SystemExit("Not enough note events. Add more MIDI files before training.")

    x, y, seeds, token_to_int, int_to_token = build_dataset(tokens)
    model = build_model((x.shape[1], x.shape[2]), len(token_to_int))

    checkpoint = ModelCheckpoint(
        MODEL_DIR / "music_model.keras",
        monitor="loss",
        save_best_only=True,
        verbose=1,
    )
    early_stop = EarlyStopping(monitor="loss", patience=8, restore_best_weights=True)

    print(model.summary())
    print(f"Training samples: {len(x):,}")
    print(f"Vocabulary size: {len(token_to_int):,}")

    model.fit(
        x,
        y,
        epochs=60,
        batch_size=64,
        callbacks=[checkpoint, early_stop],
        verbose=1,
    )

    vocab_payload = {
        "sequence_length": SEQUENCE_LENGTH,
        "token_to_int": token_to_int,
        "int_to_token": {str(k): v for k, v in int_to_token.items()},
    }
    (MODEL_DIR / "vocab.json").write_text(json.dumps(vocab_payload), encoding="utf-8")

    safe_seeds = seeds[:: max(1, len(seeds) // 250)][:250]
    (MODEL_DIR / "seed_sequences.json").write_text(json.dumps(safe_seeds), encoding="utf-8")

    print("\nTraining complete.")
    print("Saved model/music_model.keras, models/vocab.json, and models/seed_sequences.json")


if __name__ == "__main__":
    main()
