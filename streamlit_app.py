from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

from music_engine import GENERATED_DIR, generate_music

st.set_page_config(
    page_title="MuseLab — Music Generator",
    page_icon="♪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

STYLE_OPTIONS = [
    "classical",
    "jazz",
    "ambient",
    "cinematic",
    "ghazal darbari",
]

STYLE_LABELS = {
    "classical": "Classical",
    "jazz": "Jazz",
    "ambient": "Ambient",
    "cinematic": "Cinematic",
    "ghazal darbari": "Indian Classical",
}

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

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        max-width: 880px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .app-head {
        max-width: 600px;
        margin: 0 auto 2rem;
        text-align: center;
    }

    .mark {
        width: 40px;
        height: 40px;
        display: grid;
        place-items: center;
        margin: 0 auto 14px;
        border: 1px solid var(--border);
        border-radius: 9px;
        background: var(--surface);
        color: var(--accent);
        font-size: 20px;
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
        margin: 9px auto 0;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.6;
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

    .stButton > button {
        min-height: 46px;
        border-radius: 8px;
        border: 1px solid #e4e7eb;
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

    .empty-state {
        min-height: 245px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 28px;
    }

    .empty-state strong {
        display: block;
        margin-bottom: 7px;
        color: var(--text);
        font-size: 18px;
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
        margin-bottom: 16px;
    }

    .result-title {
        color: var(--text);
        font-size: 21px;
        font-weight: 700;
    }

    .result-sub {
        margin-top: 4px;
        color: var(--muted);
        font-size: 12px;
    }

    .badge {
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 6px 9px;
        background: var(--surface-2);
        color: #c5cbd3;
        font-size: 11px;
        white-space: nowrap;
    }

    .stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }

    .stat {
        padding: 11px 12px;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: #14171c;
    }

    .stat strong {
        display: block;
        margin-bottom: 3px;
        color: var(--text);
        font-size: 16px;
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

    @media (max-width: 720px) {
        .block-container { padding: 2rem 1rem 2.5rem; }
        .app-head h1 { font-size: 32px; }
        .stats { grid-template-columns: repeat(2, 1fr); }
        .result-top { align-items: flex-start; flex-direction: column; }
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
        <p>Generate a complete MIDI arrangement with melody, harmony and bass.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        style = st.selectbox(
            "Style",
            options=STYLE_OPTIONS,
            format_func=lambda x: STYLE_LABELS[x],
            index=0,
        )

    with c2:
        length = st.slider(
            "Length",
            min_value=48,
            max_value=168,
            value=96,
            step=12,
        )

    with c3:
        creativity = st.slider(
            "Variation",
            min_value=0.3,
            max_value=1.6,
            value=0.8,
            step=0.1,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    generate_clicked = st.button(
        "Generate music",
        use_container_width=True,
        type="primary",
    )

if generate_clicked:
    with st.spinner("Generating arrangement..."):
        st.session_state["piece"] = generate_music(
            style=style,
            length=length,
            creativity=creativity,
        )

piece = st.session_state.get("piece")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

with st.container(border=True):
    if not piece:
        st.markdown(
            """
            <div class="empty-state">
                <div>
                    <strong>No composition yet</strong>
                    <span>Choose a style and press Generate music. Your composition will appear here.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if piece["source"] == "trained-lstm":
            source_label = "LSTM + arrangement"
        elif piece["source"] == "raga-engine":
            source_label = "Indian music engine"
        else:
            source_label = "Music engine"

        piece_label = STYLE_LABELS.get(piece["style"], piece["style"].title())
        piece_sub = (
            "Melody · drone · soft rhythm"
            if piece["style"] == "ghazal darbari"
            else "Melody · harmony · bass"
        )

        st.markdown(
            f"""
            <div class="result-top">
                <div>
                    <div class="result-title">{piece_label}</div>
                    <div class="result-sub">{piece_sub}</div>
                </div>
                <span class="badge">{source_label}</span>
            </div>
            <div class="stats">
                <div class="stat"><strong>{piece['tempo']}</strong><span>BPM</span></div>
                <div class="stat"><strong>{piece.get('key', '—')}</strong><span>Key</span></div>
                <div class="stat"><strong>{piece['bars']}</strong><span>Bars</span></div>
                <div class="stat"><strong>{len(piece['events'])}</strong><span>Events</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        events_json = json.dumps(piece["events"])
        is_indian = "true" if piece["style"] == "ghazal darbari" else "false"

        player_html = f"""
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif; background:transparent; color:#f2f4f7; }}
            .player {{ overflow:hidden; border:1px solid #2a2f38; border-radius:8px; background:#111419; }}
            canvas {{ display:block; width:100%; height:190px; background:#111419; }}
            .controls {{ display:flex; align-items:center; gap:8px; padding:10px; border-top:1px solid #2a2f38; background:#171a20; }}
            button {{ border:1px solid #363c46; border-radius:7px; padding:8px 14px; background:#20242b; color:#eef1f5; cursor:pointer; font:inherit; font-size:12px; font-weight:600; }}
            button.primary {{ border-color:#f2f4f7; background:#f2f4f7; color:#111318; }}
            .note {{ margin-left:auto; color:#7f8793; font-size:11px; }}
            @media (max-width:520px) {{ .note {{ display:none; }} }}
        </style>
        </head>
        <body>
            <div class="player">
                <canvas id="roll" width="900" height="190"></canvas>
                <div class="controls">
                    <button class="primary" onclick="playPiece()">Play</button>
                    <button onclick="stopPiece()">Stop</button>
                    <span class="note">Browser preview</span>
                </div>
            </div>

            <script>
                const events = {events_json};
                const tempo = {piece['tempo']};
                const isIndian = {is_indian};
                const canvas = document.getElementById('roll');
                const ctx = canvas.getContext('2d');
                let audioCtx = null;
                let active = [];

                function roleColor(role) {{
                    if (role === 'bass') return '#77829a';
                    if (role === 'harmony') return '#68736d';
                    return '#b8d2b0';
                }}

                function drawRoll() {{
                    const pitches = events.flatMap(e => e.pitches);
                    const minP = Math.min(...pitches, 36);
                    const maxP = Math.max(...pitches, 84);
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
                            const w = Math.max(3, (e.duration / total) * canvas.width - 1);
                            const y = canvas.height - 14 - ((p - minP) / Math.max(1, maxP - minP)) * (canvas.height - 28);
                            ctx.fillStyle = roleColor(e.role);
                            ctx.fillRect(x, y, w, e.role === 'bass' ? 5 : 7);
                        }});
                    }});
                }}

                function midiToFreq(n) {{ return 440 * Math.pow(2, (n - 69) / 12); }}

                function stopPiece() {{
                    active.forEach(node => {{ try {{ node.stop(); }} catch (e) {{}} }});
                    active = [];
                    if (audioCtx) {{ audioCtx.close(); audioCtx = null; }}
                }}

                function scheduleVoice(event, pitch, output) {{
                    const role = event.role || 'melody';
                    const beat = 60 / tempo;
                    const start = audioCtx.currentTime + 0.08 + event.start * beat;
                    const end = start + Math.max(0.08, event.duration * beat * 0.94);
                    const velocity = Math.max(0.45, Math.min(1.15, (event.velocity || 78) / 86));
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    const filter = audioCtx.createBiquadFilter();

                    if (role === 'bass') {{
                        osc.type = 'sine';
                        filter.type = 'lowpass';
                        filter.frequency.value = isIndian ? 520 : 720;
                    }} else if (role === 'harmony') {{
                        osc.type = 'sine';
                        filter.type = 'lowpass';
                        filter.frequency.value = isIndian ? 1400 : 1900;
                    }} else {{
                        osc.type = isIndian ? 'sine' : 'triangle';
                        filter.type = 'lowpass';
                        filter.frequency.value = isIndian ? 3000 : 4200;
                    }}

                    osc.frequency.value = midiToFreq(pitch);

                    const peak = (role === 'bass' ? 0.07 : role === 'harmony' ? 0.032 : 0.075) * velocity;
                    const attack = role === 'harmony' ? 0.07 : (isIndian ? 0.035 : 0.018);
                    const release = role === 'harmony' ? 0.20 : (isIndian ? 0.16 : 0.09);
                    const sustainTime = Math.max(start + attack + 0.01, end - release);

                    gain.gain.setValueAtTime(0.0001, start);
                    gain.gain.exponentialRampToValueAtTime(Math.max(0.001, peak), start + attack);
                    gain.gain.setValueAtTime(Math.max(0.001, peak * 0.72), sustainTime);
                    gain.gain.exponentialRampToValueAtTime(0.0001, end);

                    osc.connect(gain);
                    gain.connect(filter);
                    filter.connect(output.master);
                    if (role !== 'bass') filter.connect(output.delay);

                    osc.start(start);
                    osc.stop(end + 0.04);
                    active.push(osc);
                }}

                function playPiece() {{
                    stopPiece();
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();

                    const master = audioCtx.createGain();
                    master.gain.value = isIndian ? 0.78 : 0.72;

                    const compressor = audioCtx.createDynamicsCompressor();
                    compressor.threshold.value = -18;
                    compressor.knee.value = 18;
                    compressor.ratio.value = 4;
                    compressor.attack.value = 0.01;
                    compressor.release.value = 0.18;

                    const delay = audioCtx.createDelay(0.6);
                    delay.delayTime.value = isIndian ? 0.19 : 0.14;
                    const wet = audioCtx.createGain();
                    wet.gain.value = isIndian ? 0.16 : 0.10;

                    delay.connect(wet);
                    wet.connect(master);
                    master.connect(compressor);
                    compressor.connect(audioCtx.destination);

                    const output = {{ master, delay }};
                    events.forEach(event => event.pitches.forEach(pitch => scheduleVoice(event, pitch, output)));
                }}

                drawRoll();
            </script>
        </body>
        </html>
        """

        components.html(player_html, height=255, scrolling=False)

        midi_path = GENERATED_DIR / piece["filename"]
        if midi_path.exists():
            with midi_path.open("rb") as file:
                st.download_button(
                    "Download MIDI",
                    data=file.read(),
                    file_name=piece["filename"],
                    mime="audio/midi",
                    use_container_width=True,
                )

st.markdown(
    '<div class="footer-note">CodeAlpha Task 3 · Python · music21 · LSTM · MIDI</div>',
    unsafe_allow_html=True,
)
