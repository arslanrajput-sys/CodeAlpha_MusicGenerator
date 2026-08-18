# MuseLab — AI Music Generator

A CodeAlpha Task 3 project for MIDI music generation with Python, `music21`, an LSTM training pipeline, and a clean Streamlit interface.

## Live deployment

The repository is prepared for **Streamlit Community Cloud**.

Use these values on the deployment screen:

```text
Repository: arslanrajput-sys/CodeAlpha_MusicGenerator
Branch: main
Main file path: streamlit_app.py
```

No API key or environment variable is required.

## What the project includes

- MIDI parsing and preprocessing with `music21`
- Notes/chords converted into numerical training sequences
- Stacked LSTM model in TensorFlow/Keras
- Local model training workflow
- MIDI sequence generation
- Four composition styles: Classical, Jazz, Ambient and Cinematic
- Adjustable sequence length and creativity
- Browser Web Audio preview
- Piano-roll visualization
- Downloadable `.mid` output
- Responsive Streamlit frontend
- Lightweight hosted runtime with no TensorFlow install required

## Why TensorFlow is not in `requirements.txt`

TensorFlow is the large training dependency. Installing it on every hosted app build makes deployment much slower and heavier.

The project therefore separates its dependencies:

```text
requirements.txt           # lightweight Streamlit deployment
requirements-training.txt  # TensorFlow/Keras local training
```

The deployed app works immediately with the built-in composition engine. If trained model files are included in an environment that has TensorFlow available, `music_engine.py` can load and use them automatically.

## Project structure

```text
CodeAlpha_MusicGenerator/
├── streamlit_app.py            # Streamlit Community Cloud entry point
├── music_engine.py             # generation + MIDI export
├── preprocess.py               # MIDI -> training tokens
├── train.py                    # stacked LSTM training
├── app.py                      # original Flask implementation
├── requirements.txt            # hosted runtime
├── requirements-training.txt   # local model training
├── .streamlit/
│   └── config.toml             # Streamlit theme
├── data/
│   ├── midi/
│   └── processed/
├── models/
└── generated/
```

## Run the Streamlit app locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the hosted runtime dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run streamlit_app.py
```

## Train the LSTM locally

For training, use Python 3.11 and install the training dependencies:

```bash
pip install -r requirements-training.txt
```

Place MIDI training files in:

```text
data/midi/
```

Preprocess them:

```bash
python preprocess.py
```

Train the model:

```bash
python train.py
```

Training creates:

```text
models/music_model.keras
models/vocab.json
models/seed_sequences.json
```

## Model architecture

```text
64-event sequence
      ↓
LSTM 256
      ↓
Dropout
      ↓
LSTM 256
      ↓
Batch Normalization
      ↓
LSTM 128
      ↓
Dense 128
      ↓
Softmax prediction
```

## CodeAlpha Task 3 mapping

| Requirement | Implementation |
| --- | --- |
| Collect MIDI music data | `data/midi/` |
| Preprocess MIDI into note sequences | `preprocess.py` + `music21` |
| Build a deep-learning model | stacked LSTM in `train.py` |
| Train on the dataset | `train.py` |
| Generate new music sequences | `music_engine.py` |
| Convert output to MIDI | `music21` MIDI writer |
| Play or save the result | Web Audio preview + MIDI download |

Only use MIDI files you have permission to use for training.
