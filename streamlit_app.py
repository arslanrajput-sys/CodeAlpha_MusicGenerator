from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from music_engine import GENERATED_DIR, STYLE_CONFIG, generate_music

st.set_page_config(
    page_title="MuseLab — Music Generator",
    page_icon="♪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent

st.markdown(
    """
    <style>
    :root {
        --bg: #0f1115;
        --surface: #171a20;
        --surface-2: #1d2128;
        --border: #2a2f38;
        --text: #f2f4f7;
        --muted: #9299a5;
        --accent: #a9c5a0;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif !important;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        max-width: 880px;
        padding-top: 3.5rem;
        padding-bottom: 3rem;
    }

    .app-head {
        text-align: center;
        margin: 0 auto 2.2rem;
        max-width: 620px;
    }

    .app-head .mark {
        width: 42px;
        height: 42px;
        margin: 0 auto 16px;
        border: 1px solid var(--border);
        border-radius: 10px;
        display: grid;
        place-items: center;
        background: var(--surface);
        font-size: 21px;
        color: var(--accent);
    }

    .app-head h1 {
        margin: 0;
        color: var(--text);
        font-size: 38px;
        line-height: 1.15;
        letter-spacing: -1.2px;
        font-weight: 700;
    }

    .app-head p {
        margin: 10px auto 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.6;
    }

    .small-label {
        color: var(--muted);
        font-size: 12px;
        text-align: center;
        margin-top: 8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: 12px;
        padding: 4px;
    }

    label, .stSelectbox label, .stSlider label {
        color: #c8cdd5 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="select"] > div {
        background: var(--surface-2) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="popover"] {
        background: var(--surface-2) !important;
    }

    .stSlider [data-baseweb="slider"] {
        padding-top: 5px;
    }

    .stButton > button {
        min-height: 46px;
        border-radius: 8px;
        border: 1px solid #d9dde3;
        background: #f4f5f7;
        color: #111318;
        font-weight: 700;
        box-shadow: none;
    }

    .stButton > button:hover {
        background: #ffffff;
        border-color: #ffffff;
        color: #111318;
    }

    [data-testid="stDownloadButton"] button {
        min-height: 44px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--surface-2);
        color: var(--text);
        font-weight: 600;
        box-shadow: none;
    }

    [data-testid="stDownloadButton"] button:hover {
        border-color: #444b56;
        background: #22262e;
        color: #ffffff;
    }

    .empty-state {
        min-height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 26px;
    }

    .empty-state strong {
        display: block;
        font-size: 18px;
        color: var(--text);
        margin-bottom: 7px;
    }

    .empty-state span {
        display: block;
        max-width: 430px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }

    .result-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 18px;
    }

    .result-title {
        font-size: 22px;
        line-height: 1.2;
        font-weight: 700;
        color: var(--text);
    }

    .result-sub {
        color: var(--muted);
        font-size: 12px;
        margin-top: 5px;
    }

    .badge {
        border: 1px solid var(--border);
        background: var(--surface-2);
        color: #c5cbd3;
        font-size: 11px;
        padding: 6px 9px;
        border-radius: 999px;
        white-space: nowrap;
    }

    .stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }

    .stat {
        border: 1px solid var(--border);
        background: #14171c;
        border-radius: 8px;
        padding: 12px;
    }

    .stat strong {
        display: block;
        color: var(--text);
        font-size: 16px;
        margin-bottom: 3px;
    }

    .stat span {
        color: var(--muted);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .04em;
    }

    .footer-note {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
        color: #737b87;
        text-align: center;
        font-size: 11px;
    }

    [data-testid="stSpinner"] {
        color: var(--muted) !important;
    }

    @media (max-width: 720px) {
        .block-container {
            padding: 2rem 1rem 2.5rem;
        }

        .app-head h1 {
            font-size: 32px;
        }

        .stats {
            grid-template-columns: repeat(2, 1fr);
        }

        .result-top {
            align-items: flex-start;
            flex-direction: column;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-head">
        <div class="mark">♪</div>
        <h1>MuseLab</h1>
        <p>Generate a MIDI composition, preview it in your browser, and download the result.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        style = st.selectbox(
            "Style",
            options=list(STYLE_CONFIG.keys()),
            format_func=lambda x: x.title(),
            index=0,
        )

    with c2:
        length = st.slider(
            "Length",
            min_value=48,
            max_value=200,
            value=96,
            step=8,
        )

    with c3:
        creativity = st.slider(
            "Creativity",
            min_value=0.3,
            max_value=1.6,
            value=0.9,
            step=0.1,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    generate_clicked = st.button(
        "Generate music",
        use_container_width=True,
        type="primary",
    )

if generate_clicked:
    with st.spinner("Generating composition..."):
        st.session_state["piece"] = generate_music(
            style=style,
            length=length,
            creativity=creativity,
        )
        st.session_state["piece_creativity"] = creativity

piece = st.session_state.get("piece")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

with st.container(border=True):
    if not piece:
        st.markdown(
            """
            <div class="empty-state">
                <div>
                    <strong>No composition yet</strong>
                    <span>Choose your settings above and press Generate music. Your piano roll, playback controls and MIDI download will appear here.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        source_label = "Trained LSTM" if piece["source"] == "trained-lstm" else "Composition engine"
        shown_creativity = st.session_state.get("piece_creativity", creativity)

        st.markdown(
            f"""
            <div class="result-top">
                <div>
                    <div class="result-title">{piece['style'].title()} composition</div>
                    <div class="result-sub">Generated for this session</div>
                </div>
                <span class="badge">{source_label}</span>
            </div>
            <div class="stats">
                <div class="stat"><strong>{piece['tempo']}</strong><span>BPM</span></div>
                <div class="stat"><strong>{piece['bars']}</strong><span>Bars</span></div>
                <div class="stat"><strong>{len(piece['events'])}</strong><span>Events</span></div>
                <div class="stat"><strong>{shown_creativity:.1f}</strong><span>Creativity</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        events_json = json.dumps(piece["events"])
        player_html = f"""
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                color: #f2f4f7;
                background: transparent;
            }}
            .player {{
                border: 1px solid #2a2f38;
                border-radius: 8px;
                overflow: hidden;
                background: #111419;
            }}
            canvas {{
                display: block;
                width: 100%;
                height: 180px;
                background: #111419;
            }}
            .controls {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px;
                border-top: 1px solid #2a2f38;
                background: #171a20;
            }}
            button {{
                border: 1px solid #363c46;
                background: #20242b;
                color: #eef1f5;
                border-radius: 7px;
                padding: 8px 14px;
                cursor: pointer;
                font: inherit;
                font-size: 12px;
                font-weight: 600;
            }}
            button.primary {{
                background: #f2f4f7;
                color: #111318;
                border-color: #f2f4f7;
            }}
            .note {{
                margin-left: auto;
                color: #7f8793;
                font-size: 11px;
            }}
            @media (max-width: 520px) {{
                .note {{ display: none; }}
            }}
        </style>
        </head>
        <body>
            <div class="player">
                <canvas id="roll" width="900" height="180"></canvas>
                <div class="controls">
                    <button class="primary" onclick="playPiece()">Play</button>
                    <button onclick="stopPiece()">Stop</button>
                    <span class="note">Browser preview</span>
                </div>
            </div>

            <script>
                const events = {events_json};
                const tempo = {piece['tempo']};
                const canvas = document.getElementById('roll');
                const ctx = canvas.getContext('2d');
                let audioCtx = null;
                let active = [];

                function drawRoll() {{
                    const pitches = events.flatMap(e => e.pitches);
                    const minP = Math.min(...pitches, 48);
                    const maxP = Math.max(...pitches, 72);
                    const total = Math.max(...events.map(e => e.start + e.duration), 1);

                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.strokeStyle = '#242931';
                    ctx.lineWidth = 1;

                    for (let i = 1; i < 8; i++) {{
                        const y = i * canvas.height / 8;
                        ctx.beginPath();
                        ctx.moveTo(0, y);
                        ctx.lineTo(canvas.width, y);
                        ctx.stroke();
                    }}

                    events.forEach(e => {{
                        e.pitches.forEach(p => {{
                            const x = (e.start / total) * canvas.width;
                            const w = Math.max(4, (e.duration / total) * canvas.width - 2);
                            const y = canvas.height - 18 - ((p - minP) / Math.max(1, maxP - minP)) * (canvas.height - 36);
                            ctx.fillStyle = '#a9c5a0';
                            ctx.fillRect(x, y, w, 7);
                        }});
                    }});
                }}

                function midiToFreq(n) {{
                    return 440 * Math.pow(2, (n - 69) / 12);
                }}

                function stopPiece() {{
                    active.forEach(o => {{
                        try {{ o.stop(); }} catch (e) {{}}
                    }});
                    active = [];
                    if (audioCtx) {{
                        audioCtx.close();
                        audioCtx = null;
                    }}
                }}

                function playPiece() {{
                    stopPiece();
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const beat = 60 / tempo;

                    events.forEach(e => {{
                        e.pitches.forEach(p => {{
                            const osc = audioCtx.createOscillator();
                            const gain = audioCtx.createGain();
                            osc.type = 'triangle';
                            osc.frequency.value = midiToFreq(p);

                            const start = audioCtx.currentTime + 0.06 + e.start * beat;
                            const end = start + Math.max(0.08, e.duration * beat * 0.92);

                            gain.gain.setValueAtTime(0.0001, start);
                            gain.gain.exponentialRampToValueAtTime(0.10, start + 0.025);
                            gain.gain.exponentialRampToValueAtTime(0.0001, end);

                            osc.connect(gain);
                            gain.connect(audioCtx.destination);
                            osc.start(start);
                            osc.stop(end + 0.03);
                            active.push(osc);
                        }});
                    }});
                }}

                drawRoll();
            </script>
        </body>
        </html>
        """

        components.html(player_html, height=245, scrolling=False)

        midi_path = GENERATED_DIR / piece["filename"]
        if midi_path.exists():
            with midi_path.open("rb") as f:
                st.download_button(
                    "Download MIDI",
                    data=f.read(),
                    file_name=piece["filename"],
                    mime="audio/midi",
                    use_container_width=True,
                )

st.markdown(
    """
    <div class="footer-note">CodeAlpha Task 3 · Python · music21 · LSTM · MIDI</div>
    """,
    unsafe_allow_html=True,
)
