from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from music_engine import GENERATED_DIR, STYLE_CONFIG, generate_music

st.set_page_config(
    page_title="MuseLab — Music Generator",
    page_icon="♪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600&display=swap');

    :root {
        --ink: #1f2a24;
        --muted: #6f7771;
        --line: #e7e8e3;
        --paper: #fbfaf7;
        --card: #ffffff;
        --accent: #355c4d;
        --accent-soft: #edf3ef;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: var(--paper); color: var(--ink); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }

    .topbar {
        display:flex; align-items:center; justify-content:space-between;
        border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:42px;
    }
    .brand { font-size:19px; font-weight:700; letter-spacing:-.4px; }
    .brand span { color:var(--accent); }
    .tiny { color:var(--muted); font-size:12px; letter-spacing:.03em; }

    .hero { max-width:760px; margin-bottom:34px; }
    .eyebrow { color:var(--accent); font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:12px; }
    .hero h1 { font-family:'Playfair Display', serif; font-size:52px; line-height:1.03; letter-spacing:-1.8px; margin:0 0 16px; color:var(--ink); }
    .hero p { font-size:17px; line-height:1.75; color:var(--muted); max-width:680px; margin:0; }

    .panel {
        background:var(--card); border:1px solid var(--line); border-radius:18px;
        padding:22px 22px 18px; box-shadow:0 10px 30px rgba(35,43,38,.035);
    }
    .section-title { font-size:13px; font-weight:700; margin-bottom:4px; }
    .section-copy { color:var(--muted); font-size:12px; margin-bottom:12px; }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stSlider [data-baseweb="slider"] { border-radius:10px; }

    .stButton > button {
        width:100%; border-radius:10px; border:1px solid var(--accent);
        background:var(--accent); color:white; min-height:46px; font-weight:600;
    }
    .stButton > button:hover { background:#28483b; border-color:#28483b; color:white; }

    .result-head { display:flex; justify-content:space-between; align-items:flex-start; gap:20px; margin-bottom:16px; }
    .result-title { font-family:'Playfair Display', serif; font-size:30px; margin:0 0 5px; }
    .badge { display:inline-flex; align-items:center; border-radius:999px; padding:6px 10px; font-size:11px; font-weight:700; background:var(--accent-soft); color:var(--accent); }

    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:14px 0 18px; }
    .stat { border:1px solid var(--line); border-radius:12px; padding:13px 14px; background:#fdfdfb; }
    .stat strong { display:block; font-size:17px; margin-bottom:3px; }
    .stat span { color:var(--muted); font-size:11px; }

    .info-strip { margin-top:34px; display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .info-card { border-top:1px solid var(--line); padding-top:16px; }
    .info-card b { font-size:13px; }
    .info-card p { color:var(--muted); font-size:12px; line-height:1.6; margin-top:7px; }

    [data-testid="stDownloadButton"] button {
        width:100%; border-radius:10px; min-height:44px; background:white; color:var(--ink); border:1px solid var(--line);
    }
    [data-testid="stDownloadButton"] button:hover { border-color:#b7bdb9; color:var(--ink); background:white; }

    @media (max-width: 760px) {
        .block-container { padding:1.2rem 1rem 3rem; }
        .hero h1 { font-size:40px; }
        .stats, .info-strip { grid-template-columns:1fr 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topbar">
        <div class="brand">Muse<span>Lab</span></div>
        <div class="tiny">CODEALPHA · TASK 3</div>
    </div>
    <div class="hero">
        <div class="eyebrow">Music generation with AI</div>
        <h1>Compose something<br>worth listening to.</h1>
        <p>Generate original MIDI ideas from a trained LSTM model when available, with a lightweight composition engine as a deployable fallback.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([0.36, 0.64], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Composition settings</div><div class="section-copy">Shape the character and length of your piece.</div>', unsafe_allow_html=True)

    style = st.selectbox(
        "Style",
        options=list(STYLE_CONFIG.keys()),
        format_func=lambda x: x.title(),
        index=0,
    )
    length = st.slider("Notes / events", min_value=48, max_value=200, value=96, step=8)
    creativity = st.slider("Creativity", min_value=0.3, max_value=1.6, value=0.9, step=0.1)

    generate_clicked = st.button("Generate composition", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    if generate_clicked:
        with st.spinner("Writing the next phrase..."):
            st.session_state["piece"] = generate_music(style=style, length=length, creativity=creativity)

    piece = st.session_state.get("piece")

    if not piece:
        st.markdown(
            """
            <div class="panel" style="min-height:360px; display:flex; align-items:center; justify-content:center; text-align:center;">
                <div style="max-width:390px;">
                    <div style="font-family:'Playfair Display',serif;font-size:27px;margin-bottom:10px;">Your next composition starts here.</div>
                    <div style="color:#6f7771;font-size:13px;line-height:1.7;">Choose a style, set the length and creativity, then generate a MIDI piece. The piano roll and playback controls will appear here.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        source_label = "Trained LSTM" if piece["source"] == "trained-lstm" else "Composition engine"
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-head">
                <div>
                    <div class="result-title">{piece['style'].title()} study</div>
                    <div style="color:#6f7771;font-size:12px;">A new MIDI sequence generated for this session.</div>
                </div>
                <span class="badge">{source_label}</span>
            </div>
            <div class="stats">
                <div class="stat"><strong>{piece['tempo']}</strong><span>BPM</span></div>
                <div class="stat"><strong>{piece['bars']}</strong><span>Estimated bars</span></div>
                <div class="stat"><strong>{len(piece['events'])}</strong><span>Events</span></div>
                <div class="stat"><strong>{creativity:.1f}</strong><span>Creativity</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        events_json = json.dumps(piece["events"])
        player_html = f"""
        <!doctype html>
        <html><head><meta charset="utf-8"><style>
        body {{ margin:0; font-family:Inter,Arial,sans-serif; color:#1f2a24; }}
        .wrap {{ border:1px solid #e7e8e3; border-radius:12px; overflow:hidden; background:#fbfaf7; }}
        canvas {{ display:block; width:100%; height:180px; background:#fbfaf7; }}
        .controls {{ display:flex; gap:8px; padding:12px; border-top:1px solid #e7e8e3; background:white; }}
        button {{ border:1px solid #dfe2df; background:white; border-radius:8px; padding:9px 14px; cursor:pointer; color:#1f2a24; font-weight:600; }}
        button.primary {{ background:#355c4d; color:white; border-color:#355c4d; }}
        .note {{ font-size:11px; color:#788079; margin-left:auto; align-self:center; }}
        </style></head><body>
        <div class="wrap">
          <canvas id="roll" width="900" height="180"></canvas>
          <div class="controls">
            <button class="primary" onclick="playPiece()">Play</button>
            <button onclick="stopPiece()">Stop</button>
            <span class="note">Web Audio preview · piano synth</span>
          </div>
        </div>
        <script>
        const events = {events_json};
        const tempo = {piece['tempo']};
        const canvas = document.getElementById('roll');
        const ctx = canvas.getContext('2d');
        let audioCtx = null, active = [];

        function drawRoll() {{
          const pitches = events.flatMap(e => e.pitches);
          const minP = Math.min(...pitches, 48), maxP = Math.max(...pitches, 72);
          const total = Math.max(...events.map(e => e.start + e.duration), 1);
          ctx.clearRect(0,0,canvas.width,canvas.height);
          ctx.strokeStyle='#eceeea'; ctx.lineWidth=1;
          for(let i=1;i<8;i++) {{ const y=i*canvas.height/8; ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.stroke(); }}
          events.forEach(e => {{
            e.pitches.forEach(p => {{
              const x=(e.start/total)*canvas.width;
              const w=Math.max(4,(e.duration/total)*canvas.width-2);
              const y=canvas.height-18-((p-minP)/Math.max(1,maxP-minP))*(canvas.height-36);
              ctx.fillStyle='#355c4d';
              ctx.fillRect(x,y,w,7);
            }});
          }});
        }}

        function midiToFreq(n) {{ return 440*Math.pow(2,(n-69)/12); }}
        function stopPiece() {{ active.forEach(o=>{{try{{o.stop();}}catch(e){{}}}}); active=[]; if(audioCtx){{audioCtx.close();audioCtx=null;}} }}
        function playPiece() {{
          stopPiece(); audioCtx=new (window.AudioContext||window.webkitAudioContext)();
          const beat=60/tempo;
          events.forEach(e=>{{
            e.pitches.forEach(p=>{{
              const osc=audioCtx.createOscillator(); const gain=audioCtx.createGain();
              osc.type='triangle'; osc.frequency.value=midiToFreq(p);
              const s=audioCtx.currentTime+0.06+e.start*beat; const end=s+Math.max(.08,e.duration*beat*.92);
              gain.gain.setValueAtTime(0.0001,s); gain.gain.exponentialRampToValueAtTime(0.11,s+.025); gain.gain.exponentialRampToValueAtTime(0.0001,end);
              osc.connect(gain); gain.connect(audioCtx.destination); osc.start(s); osc.stop(end+.03); active.push(osc);
            }});
          }});
        }}
        drawRoll();
        </script></body></html>
        """
        components.html(player_html, height=245, scrolling=False)

        midi_path = GENERATED_DIR / piece["filename"]
        if midi_path.exists():
            with midi_path.open("rb") as f:
                st.download_button(
                    "Download MIDI file",
                    data=f.read(),
                    file_name=piece["filename"],
                    mime="audio/midi",
                    use_container_width=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="info-strip">
        <div class="info-card"><b>01 · MIDI preprocessing</b><p>Music21 converts notes and chords into numerical sequences suitable for model training.</p></div>
        <div class="info-card"><b>02 · LSTM learning</b><p>The training pipeline learns note-to-note patterns and saves a reusable Keras model.</p></div>
        <div class="info-card"><b>03 · Generation</b><p>Predicted sequences are converted back to playable, downloadable MIDI compositions.</p></div>
    </div>
    """,
    unsafe_allow_html=True,
)
