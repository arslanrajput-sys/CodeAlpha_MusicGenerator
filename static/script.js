const state = {
  style: "classical",
  events: [],
  tempo: 92,
  titleCount: 1,
  audioContext: null,
  activeNodes: [],
  startedAt: 0,
  totalSeconds: 0,
  animationFrame: null,
};

const $ = (id) => document.getElementById(id);
const generateButton = $("generateButton");
const lengthRange = $("lengthRange");
const creativityRange = $("creativityRange");
const lengthValue = $("lengthValue");
const creativityValue = $("creativityValue");
const playButton = $("playButton");
const stopButton = $("stopButton");
const restartButton = $("restartButton");
const downloadButton = $("downloadButton");
const canvas = $("visualizer");
const ctx = canvas.getContext("2d");

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function variationLabel(value) {
  const n = Number(value);
  if (n < 0.7) return "Controlled";
  if (n < 1.1) return "Balanced";
  if (n < 1.35) return "Expressive";
  return "Adventurous";
}

function formatTime(seconds) {
  const safe = Math.max(0, Math.floor(seconds || 0));
  const mins = Math.floor(safe / 60);
  const secs = String(safe % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

function resizeCanvas() {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  drawEvents();
}

function drawEvents(progress = 0) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);

  if (!state.events.length) return;

  const pitches = state.events.flatMap((event) => event.pitches);
  const minPitch = Math.min(...pitches) - 2;
  const maxPitch = Math.max(...pitches) + 2;
  const pitchSpan = Math.max(1, maxPitch - minPitch);
  const totalBeats = Math.max(...state.events.map((event) => event.start + event.duration));
  const pad = 18;
  const drawWidth = width - pad * 2;
  const drawHeight = height - pad * 2;

  ctx.strokeStyle = "rgba(255,255,255,0.055)";
  ctx.lineWidth = 1;
  for (let i = 1; i < 8; i += 1) {
    const y = pad + (drawHeight / 8) * i;
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
  }

  state.events.forEach((event) => {
    const x = pad + (event.start / totalBeats) * drawWidth;
    const noteWidth = Math.max(3, (event.duration / totalBeats) * drawWidth - 1);

    event.pitches.forEach((pitch) => {
      const normalized = (pitch - minPitch) / pitchSpan;
      const y = pad + (1 - normalized) * drawHeight;
      const played = event.start / totalBeats <= progress;
      ctx.fillStyle = played ? "rgba(220,235,220,0.92)" : "rgba(255,255,255,0.34)";
      ctx.fillRect(x, y - 2, noteWidth, 4);
    });
  });
}

function stopPlayback(reset = true) {
  state.activeNodes.forEach((node) => {
    try { node.stop(); } catch (_) {}
  });
  state.activeNodes = [];
  if (state.animationFrame) cancelAnimationFrame(state.animationFrame);
  state.animationFrame = null;
  playButton.textContent = "▶";

  if (reset) {
    $("progressFill").style.width = "0%";
    $("timeCurrent").textContent = "0:00";
    drawEvents(0);
  }
}

function midiToFrequency(midi) {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function animateProgress() {
  const elapsed = state.audioContext.currentTime - state.startedAt;
  const ratio = Math.min(1, elapsed / state.totalSeconds);
  $("progressFill").style.width = `${ratio * 100}%`;
  $("timeCurrent").textContent = formatTime(elapsed);
  drawEvents(ratio);

  if (ratio < 1) {
    state.animationFrame = requestAnimationFrame(animateProgress);
  } else {
    playButton.textContent = "▶";
    state.activeNodes = [];
  }
}

function playComposition() {
  if (!state.events.length) return;
  stopPlayback(false);

  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtx) {
    alert("Your browser does not support Web Audio playback.");
    return;
  }

  state.audioContext = state.audioContext || new AudioCtx();
  if (state.audioContext.state === "suspended") state.audioContext.resume();

  const secondsPerBeat = 60 / state.tempo;
  const now = state.audioContext.currentTime + 0.06;
  state.startedAt = now;
  const totalBeats = Math.max(...state.events.map((event) => event.start + event.duration));
  state.totalSeconds = totalBeats * secondsPerBeat;

  state.events.forEach((event) => {
    const start = now + event.start * secondsPerBeat;
    const duration = Math.max(0.08, event.duration * secondsPerBeat * 0.92);

    event.pitches.forEach((pitch, index) => {
      const oscillator = state.audioContext.createOscillator();
      const gain = state.audioContext.createGain();
      oscillator.type = state.style === "ambient" ? "sine" : "triangle";
      oscillator.frequency.value = midiToFrequency(pitch);

      const chordGain = 0.11 / Math.max(1, event.pitches.length);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(chordGain, start + 0.018 + index * 0.002);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);

      oscillator.connect(gain);
      gain.connect(state.audioContext.destination);
      oscillator.start(start);
      oscillator.stop(start + duration + 0.03);
      state.activeNodes.push(oscillator);
    });
  });

  playButton.textContent = "❚❚";
  $("timeTotal").textContent = formatTime(state.totalSeconds);
  state.animationFrame = requestAnimationFrame(animateProgress);
}

async function generateComposition() {
  stopPlayback();
  generateButton.disabled = true;
  generateButton.querySelector("span:first-child").textContent = "Composing…";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        style: state.style,
        length: Number(lengthRange.value),
        creativity: Number(creativityRange.value),
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to generate music.");

    state.events = data.events;
    state.tempo = data.tempo;
    $("emptyState").classList.add("hidden");
    $("trackTitle").textContent = `Untitled No. ${String(state.titleCount).padStart(2, "0")}`;
    $("stylePill").textContent = titleCase(data.style);
    $("tempoStat").textContent = `${data.tempo} BPM`;
    $("barsStat").textContent = data.bars;
    $("engineStat").textContent = data.source === "trained-lstm" ? "LSTM" : "Demo";

    const totalSeconds = data.duration_beats * (60 / data.tempo);
    $("timeTotal").textContent = formatTime(totalSeconds);
    downloadButton.href = data.download_url;
    downloadButton.setAttribute("download", data.filename);
    downloadButton.classList.remove("disabled");
    state.titleCount += 1;
    drawEvents(0);
  } catch (error) {
    alert(error.message);
  } finally {
    generateButton.disabled = false;
    generateButton.querySelector("span:first-child").textContent = "Generate composition";
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    $("modelStatus").textContent = data.model_ready ? "LSTM model ready" : "Demo engine ready";
  } catch (_) {
    $("modelStatus").textContent = "Local studio";
  }
}

$("styleGrid").addEventListener("click", (event) => {
  const button = event.target.closest(".style-card");
  if (!button) return;
  document.querySelectorAll(".style-card").forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
  state.style = button.dataset.style;
  $("stylePill").textContent = titleCase(state.style);
});

lengthRange.addEventListener("input", () => {
  lengthValue.textContent = `${lengthRange.value} notes`;
});

creativityRange.addEventListener("input", () => {
  creativityValue.textContent = variationLabel(creativityRange.value);
});

generateButton.addEventListener("click", generateComposition);
playButton.addEventListener("click", () => {
  if (state.activeNodes.length) stopPlayback();
  else playComposition();
});
stopButton.addEventListener("click", () => stopPlayback());
restartButton.addEventListener("click", () => {
  stopPlayback();
  playComposition();
});
window.addEventListener("resize", resizeCanvas);

checkHealth();
resizeCanvas();
