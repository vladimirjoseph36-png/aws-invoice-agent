/* ==========================================================================
   Alexa+ Simulation — Intro + Background + Chat
   Author: Anio Joseph
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. INTRO ANIMATION — particles converge to form the A+ logo
   -------------------------------------------------------------------------- */

(function introAnimation() {
  const intro = document.getElementById('intro');
  const app = document.getElementById('app');
  const canvas = document.getElementById('intro-canvas');

  if (!intro || !canvas) return;

  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const targets = [];

  // Letter "A" — left leg
  for (let i = 0; i <= 20; i++) {
    targets.push({ x: cx - 70 + i * 2, y: cy + 60 - i * 6 });
  }
  // Right leg
  for (let i = 0; i <= 20; i++) {
    targets.push({ x: cx - 30 + i * 2, y: cy - 60 + i * 6 });
  }
  // Horizontal bar
  for (let i = 0; i <= 15; i++) {
    targets.push({ x: cx - 55 + i * 3, y: cy + 5 });
  }
  // "+" horizontal
  for (let i = 0; i <= 15; i++) {
    targets.push({ x: cx + 40 + i * 3, y: cy });
  }
  // "+" vertical
  for (let i = 0; i <= 15; i++) {
    targets.push({ x: cx + 62, y: cy - 22 + i * 3 });
  }

  const particles = targets.map((t) => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    tx: t.x,
    ty: t.y,
    size: 2 + Math.random() * 2,
  }));

  const startTime = performance.now();
  const DURATION = 1800;

  function animate() {
    const elapsed = performance.now() - startTime;
    const progress = Math.min(elapsed / DURATION, 1);
    const eased = 1 - Math.pow(1 - progress, 3);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((p) => {
      p.x = p.x + (p.tx - p.x) * 0.05 * eased * 3;
      p.y = p.y + (p.ty - p.y) * 0.05 * eased * 3;

      const alpha = 0.4 + 0.6 * eased;
      ctx.fillStyle = `rgba(0, 212, 255, ${alpha})`;
      ctx.shadowColor = 'rgba(0, 212, 255, 0.9)';
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });

    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }

  animate();

  // After ~2.8s, fade out intro and show app
  setTimeout(() => {
    intro.classList.add('fade-out');
    if (app) app.classList.add('visible');

    setTimeout(() => {
      intro.classList.add('hidden');
    }, 900);
  }, 2800);
})();

/* --------------------------------------------------------------------------
   2. ANIMATED BACKGROUND — floating particles + connections
   -------------------------------------------------------------------------- */

(function animatedBackground() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const particles = [];
  const PARTICLE_COUNT = 60;
  const MAX_DISTANCE = 150;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: 1 + Math.random() * 1.5,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      ctx.fillStyle = 'rgba(0, 212, 255, 0.6)';
      ctx.shadowColor = 'rgba(0, 212, 255, 0.9)';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.shadowBlur = 0;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < MAX_DISTANCE) {
          const alpha = (1 - dist / MAX_DISTANCE) * 0.3;
          ctx.strokeStyle = `rgba(0, 212, 255, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  draw();
})();

/* --------------------------------------------------------------------------
   3. CHAT LOGIC
   -------------------------------------------------------------------------- */

const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const micBtn = document.getElementById('mic');

// --- Web Speech API ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (SpeechRecognition && micBtn) {
  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('listening');
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('listening');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    sendMessage();
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
  };

  micBtn.addEventListener('click', () => {
    if (isListening) recognition.stop();
    else recognition.start();
  });
} else if (micBtn) {
  micBtn.disabled = true;
  micBtn.title = 'Speech recognition not supported in this browser';
}

// --- Text send ---
if (sendBtn) {
  sendBtn.addEventListener('click', sendMessage);
}
if (input) {
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

function addMessage(text, role) {
  const msg = document.createElement('div');
  msg.className = 'message ' + role;
  const avatarLabel = role === 'user' ? 'ME' : 'A+';
  msg.innerHTML = `
    <div class="avatar">${avatarLabel}</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function showTyping() {
  const t = document.createElement('div');
  t.className = 'message agent';
  t.id = 'typing';
  t.innerHTML = `
    <div class="avatar">A+</div>
    <div class="bubble"><div class="bubble-title">▶ PROCESSING</div>Analyzing your request…</div>
  `;
  chat.appendChild(t);
  chat.scrollTop = chat.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById('typing');
  if (t) t.remove();
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, 'user');
  input.value = '';
  input.disabled = true;
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch('/simulate-alexa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    hideTyping();
    if (data.error) {
      addMessage('❌ Error: ' + data.error, 'agent');
    } else {
      addMessage(data.reply, 'agent');
    }
  } catch (err) {
    hideTyping();
    addMessage('❌ Network error: ' + err.message, 'agent');
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

if (input) input.focus();