# Melody Lab — AI Music Generator

A complete CodeAlpha Task 3 project for generating MIDI music with a recurrent neural network. The project includes MIDI preprocessing with `music21`, an LSTM training pipeline with TensorFlow/Keras, MIDI generation, a Flask API, browser playback using Web Audio, a piano-roll style visualizer, and a clean responsive interface.

## What the project covers

- Collect MIDI files for training
- Parse notes and chords with `music21`
- Convert music into fixed-length numerical sequences
- Train a stacked LSTM network to predict the next musical event
- Generate new note/chord sequences from a trained model
- Convert predictions back to `.mid`
- Preview generated music in the browser
- Download generated MIDI files
- Use a built-in demo composition engine before a trained model is available

## Project structure

```text
CodeAlpha_MusicGenerator/
├── app.py                    # Flask web app and API
├── music_engine.py           # Model inference, demo generation and MIDI export
├── preprocess.py             # MIDI -> note/chord token dataset
├── train.py                  # LSTM model training
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── styles.css
│   └── script.js
├── data/
│   ├── midi/                 # Put training MIDI files here
│   └── processed/            # Generated preprocessing output
├── models/                   # Trained model + vocabulary files
└── generated/                # Generated MIDI outputs
```

## Quick start

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/arslanrajput-sys/CodeAlpha_MusicGenerator.git
cd CodeAlpha_MusicGenerator
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the web app immediately

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

The interface works before training by using the built-in demo engine. Once a trained model exists, the API automatically switches to LSTM inference.

## Train the LSTM on MIDI files

### Step 1 — Add a dataset

Create a collection of MIDI files and place them inside:

```text
data/midi/
```

A focused collection generally produces more consistent output than mixing unrelated styles. Piano/classical MIDI is a good starting point for this project.

Only use MIDI files you are allowed to use for training.

### Step 2 — Preprocess

```bash
python preprocess.py
```

This creates:

```text
data/processed/songs.json
```

Each note is represented by its MIDI pitch plus duration. Chords are stored as multiple MIDI pitches. Example tokens:

```text
60|0.5
64|0.5
60.64.67|1.0
```

### Step 3 — Train

```bash
python train.py
```

The network uses:

```text
64-event input sequence
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
Softmax over musical-event vocabulary
```

Training produces:

```text
models/music_model.keras
models/vocab.json
models/seed_sequences.json
```

Restart `app.py` after training. The header will report **LSTM model ready**, and generated compositions will use the trained network.

## Generation controls

- **Style** — changes presentation, tempo and fallback composition character
- **Length** — controls number of generated musical events
- **Variation** — used as temperature during LSTM sampling
- **Play** — previews the MIDI sequence with the browser Web Audio API
- **Download MIDI** — saves the generated composition as a standard MIDI file

## API

### Health

```http
GET /api/health
```

### Generate

```http
POST /api/generate
Content-Type: application/json
```

Example body:

```json
{
  "style": "classical",
  "length": 96,
  "creativity": 0.9
}
```

The response contains note events for browser playback plus a URL for the generated MIDI file.

## Recommended training settings

Start with at least 50–100 MIDI pieces from a reasonably consistent style. More clean training data usually matters more than increasing network size. On a CPU, begin with a smaller dataset to validate the pipeline; a GPU is recommended for larger training runs.

The default script trains for up to 60 epochs and includes early stopping and best-model checkpointing.

## Technologies

- Python
- Flask
- TensorFlow / Keras
- LSTM recurrent neural network
- music21
- NumPy
- HTML / CSS / JavaScript
- Web Audio API
- Canvas visualization

## CodeAlpha Task 3 mapping

| Requirement | Implementation |
| --- | --- |
| Collect MIDI music data | `data/midi/` dataset folder |
| Preprocess data into note sequences | `preprocess.py` + `music21` |
| Build deep learning model | Stacked LSTM in `train.py` |
| Train to generate music | `train.py` |
| Convert output to MIDI | `music_engine.py` |
| Play or save generated output | Browser player + MIDI download |

## Notes

Generated model files, training MIDI files and output MIDI files are excluded from Git by default because they may be large. The source repository stays lightweight while the full training workflow remains reproducible.
