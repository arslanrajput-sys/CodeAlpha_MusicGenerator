from __future__ import annotations

import json
from pathlib import Path
from typing import List

from music21 import chord, converter, note

BASE_DIR = Path(__file__).resolve().parent
MIDI_DIR = BASE_DIR / "data" / "midi"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def midi_to_tokens(path: Path) -> List[str]:
    score = converter.parse(str(path))
    tokens: List[str] = []

    for element in score.flatten().notes:
        duration = round(float(element.duration.quarterLength), 2)
        if isinstance(element, note.Note):
            token = f"{int(element.pitch.midi)}|{duration}"
            tokens.append(token)
        elif isinstance(element, chord.Chord):
            pitches = ".".join(str(int(p.midi)) for p in element.pitches)
            tokens.append(f"{pitches}|{duration}")

    return tokens


def main():
    files = sorted(list(MIDI_DIR.glob("*.mid")) + list(MIDI_DIR.glob("*.midi")))
    if not files:
        raise SystemExit(
            "No MIDI files found. Add .mid or .midi files to data/midi/ and run again."
        )

    songs = []
    skipped = []

    for path in files:
        try:
            tokens = midi_to_tokens(path)
            if len(tokens) >= 80:
                songs.append({"file": path.name, "tokens": tokens})
            else:
                skipped.append(path.name)
            print(f"Processed {path.name}: {len(tokens)} events")
        except Exception as exc:
            skipped.append(path.name)
            print(f"Skipped {path.name}: {exc}")

    output_path = OUTPUT_DIR / "songs.json"
    output_path.write_text(json.dumps(songs), encoding="utf-8")

    print(f"\nSaved {len(songs)} songs to {output_path}")
    if skipped:
        print(f"Skipped {len(skipped)} files: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
