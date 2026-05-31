// ============================================================
//  CHATBOT UNIVERSIDAD DE MEDELLÍN — chatbot.js
//  Mantiene API con Ollama + UI del código proporcionado
// ============================================================

const msgsEl = document.getElementById('msgs');
const inpEl  = document.getElementById('inp');

// ── Push Notifications Setup ──
async function initPushNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.log('Push notifications not supported');
    return;
  }

  try {
    const registration = await navigator.serviceWorker.register('/static/service-worker.js');
    console.log('Service Worker registered');

    // Solicitar permiso
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('Push notification permission granted');
      subscribeToPushNotifications(registration);
    }
  } catch (e) {
    console.error('Service Worker registration failed:', e);
  }
}

async function subscribeToPushNotifications(registration) {
  try {
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      // Si no está suscrito, crear nueva suscripción
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array('BCEyL-K_-eL3LhC6SY-7eRAXGfX-F1VZyJxCMJ4r8LXqCK5qPl3lxJTKL_AjKQvDCQwk_LfYLEYHhbGvQ6gqKEE')
      });

      // Enviar subscripción al servidor
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription.toJSON())
      });

      console.log('Push subscription sent to server');
    }
  } catch (e) {
    console.error('Failed to subscribe to push:', e);
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Inicializar notificaciones push cuando carga la página
window.addEventListener('load', initPushNotifications);

// ── WhatsApp Integration ──
function openWhatsAppChat() {
  const modal = document.createElement('div');
  modal.className = 'whatsapp-modal';
  modal.innerHTML = `
    <div class="whatsapp-modal-content">
      <button class="close-modal" onclick="this.parentElement.parentElement.remove()">✕</button>
      <h3>💬 Chat por WhatsApp</h3>
      <p>Conecta con nuestro asistente de IA por WhatsApp</p>
      <div class="whatsapp-form">
        <input type="tel" id="wa-phone" placeholder="+57 300 123 4567" required>
        <textarea id="wa-message" placeholder="¿Cuál es tu pregunta?" rows="3"></textarea>
        <button onclick="sendWhatsAppMessage()">Enviar por WhatsApp</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function openWhatsAppAdvisor() {
  const modal = document.createElement('div');
  modal.className = 'whatsapp-modal';
  modal.innerHTML = `
    <div class="whatsapp-modal-content">
      <button class="close-modal" onclick="this.parentElement.parentElement.remove()">✕</button>
      <h3>👨‍💼 Asesor por WhatsApp</h3>
      <p>Un asesor real te atenderá por WhatsApp</p>
      <div class="whatsapp-form">
        <input type="text" id="wa-name" placeholder="Tu nombre" required>
        <input type="tel" id="wa-advisor-phone" placeholder="+57 300 123 4567" required>
        <button onclick="requestAdvisorWhatsApp()">Conectar con Asesor</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

async function sendWhatsAppMessage() {
  const phone = document.getElementById('wa-phone').value.trim();
  const message = document.getElementById('wa-message').value.trim();

  if (!phone || !message) {
    alert('Por favor completa todos los campos');
    return;
  }

  try {
    const res = await fetch('/api/whatsapp/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, message })
    });

    const data = await res.json();

    if (data.success) {
      alert('✅ Mensaje enviado por WhatsApp. Revisa tu teléfono.');
      document.querySelector('.whatsapp-modal').remove();
    } else {
      alert('❌ Error: ' + data.message);
    }
  } catch (e) {
    alert('Error enviando mensaje: ' + e.message);
  }
}

async function requestAdvisorWhatsApp() {
  const name = document.getElementById('wa-name').value.trim();
  const phone = document.getElementById('wa-advisor-phone').value.trim();

  if (!name || !phone) {
    alert('Por favor completa todos los campos');
    return;
  }

  try {
    const res = await fetch('/api/whatsapp/advisor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone })
    });

    const data = await res.json();

    if (data.success) {
      alert('✅ Solicitud recibida. Un asesor te contactará por WhatsApp.');
      document.querySelector('.whatsapp-modal').remove();
    } else {
      alert('❌ Error: ' + data.message);
    }
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

// ── Galería ──────────────────────────────────────────────────
const galleryLabels = ['Campus UdeM', 'Edificio Forum', 'Biblioteca'];
let currentSlide = 0;

function goSlide(n) {
  currentSlide = n;
  document.getElementById('galleryImgs').style.transform = `translateX(-${n * 100}%)`;
  document.getElementById('galleryLabel').textContent = galleryLabels[n];
  document.querySelectorAll('.gdot').forEach((d, i) => {
    d.className = 'gdot' + (i === n ? ' on' : '');
  });
}

const galleryInterval = setInterval(() => goSlide((currentSlide + 1) % galleryLabels.length), 3200);

window.addEventListener('beforeunload', () => clearInterval(galleryInterval));

// ── Avatares ─────────────────────────────────────────────────
function botAvatar() {
  return `<div class="av av-bot">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0 la-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zm-2 10H6V7h12v12zm-9-6c-.83 0-1.5-.67-1.5-1.5S8.17 10 9 10s1.5.67 1.5 1.5S9.83 13 9 13zm7.5-1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zM8 15h8v2H8v-2z"/>
    </svg>
  </div>`;
}

function userAvatar() {
  return `<div class="av av-user">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
  </div>`;
}

// ── Agregar mensajes ──────────────────────────────────────────
function addUserMsg(text) {
  const div = document.createElement('div');
  div.className = 'msg user-msg';
  const bubble = document.createElement('div');
  bubble.className = 'bubble user-b';
  bubble.textContent = text;
  div.innerHTML = userAvatar();
  div.appendChild(bubble);
  msgsEl.appendChild(div);
  scrollToBottom();
}

function addBotMsg(html, hasMore=false, category=null) {
  const div = document.createElement('div');
  div.className = 'msg';
  const bubble = document.createElement('div');
  bubble.className = 'bubble bot-b';
  bubble.innerHTML = DOMPurify.sanitize(html);
  div.innerHTML = botAvatar();
  div.appendChild(bubble);

  // Add action buttons (feedback + see more)
  const actions = document.createElement('div');
  actions.className = 'msg-actions';

  const helpful = document.createElement('button');
  helpful.className = 'btn-small btn-helpful';
  helpful.innerHTML = '👍 Útil';
  helpful.onclick = () => sendFeedback(true, html.substring(0, 100), helpful);

  const notHelpful = document.createElement('button');
  notHelpful.className = 'btn-small btn-not-helpful';
  notHelpful.innerHTML = '👎 No útil';
  notHelpful.onclick = () => sendFeedback(false, html.substring(0, 100), notHelpful);

  actions.appendChild(helpful);
  actions.appendChild(notHelpful);

  if (hasMore && category) {
    const seeMore = document.createElement('button');
    seeMore.className = 'btn-small btn-see-more';
    seeMore.innerHTML = '📖 Ver más';
    seeMore.onclick = () => showExpandedResponse(category);
    actions.appendChild(seeMore);
  }

  div.appendChild(actions);
  msgsEl.appendChild(div);
  scrollToBottom();
}

async function sendFeedback(helpful, responseText, button) {
  try {
    const res = await fetch('/api/response/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        response_text: responseText,
        helpful: helpful,
        feedback: ''
      })
    });

    if (res.ok) {
      button.disabled = true;
      button.style.opacity = '0.5';
      button.textContent = helpful ? '✅ Gracias' : '❌ Noted';
    }
  } catch (e) {
    console.error('Feedback error:', e);
  }
}

async function showExpandedResponse(category) {
  try {
    const res = await fetch(`/api/response/expanded/${category}`);
    const data = await res.json();

    if (data.expanded) {
      const modal = document.createElement('div');
      modal.className = 'expanded-modal';
      modal.innerHTML = `
        <div class="expanded-content">
          <button class="close-expanded" onclick="this.parentElement.parentElement.remove()">✕</button>
          <div class="expanded-text">${DOMPurify.sanitize(marked.parse(data.expanded))}</div>
        </div>
      `;
      document.body.appendChild(modal);
    }
  } catch (e) {
    console.error('Error loading expanded response:', e);
  }
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'typing-wrap';
  div.id = 'typing';
  div.innerHTML = `${botAvatar()}
    <div class="typing-bbl">
      <div class="td"></div>
      <div class="td"></div>
      <div class="td"></div>
    </div>`;
  msgsEl.appendChild(div);
  scrollToBottom();
}

function hideTyping() {
  const t = document.getElementById('typing');
  if (t) t.remove();
}

function scrollToBottom() {
  msgsEl.scrollTop = msgsEl.scrollHeight;
}

// ── Botones de enlace ─────────────────────────────────────────
function linkBtn(url, label) {
  return `<a class="url-btn" href="${url}" target="_blank" rel="noopener">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>${label}</a>`;
}

function outlineBtn(url, label) {
  return `<a class="url-btn-outline" href="${url}" target="_blank" rel="noopener">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>${label}</a>`;
}

// ── Enviar mensaje ────────────────────
async function sendMessage(text) {
  if (!text.trim()) return;

  addUserMsg(text);
  inpEl.value = '';
  inpEl.disabled = true;
  showTyping();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('text/event-stream')) {
      // Handle Streaming Response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      // Create a bot message bubble that we will update
      const div = document.createElement('div');
      div.className = 'msg';
      div.innerHTML = `${botAvatar()}<div class="bubble bot-b"></div>`;
      msgsEl.appendChild(div);
      const bubble = div.querySelector('.bubble');
      scrollToBottom();
      hideTyping();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            try {
              const data = JSON.parse(dataStr);
              if (data.chunk) {
                fullText += data.chunk;
                bubble.innerHTML = DOMPurify.sanitize(marked.parse(fullText));
                scrollToBottom();
              } else if (data.done) {
                // Stream finished
              }
            } catch (e) {
              console.error("Error parsing SSE chunk", e);
            }
          }
        }
      }
    } else {
      // Handle Standard Response
      const data = await response.json();
      hideTyping();

      if (data.error) {
        throw new Error(data.error);
      }

      try {
        const structuredData = JSON.parse(data.response);
        if (structuredData.text && structuredData.category) {
          addBotMsg(marked.parse(structuredData.text), structuredData.has_more, structuredData.category);
        } else {
          addBotMsg(marked.parse(data.response));
        }
      } catch {
        addBotMsg(marked.parse(data.response));
      }
    }
  } catch (error) {
    hideTyping();
    addBotMsg(`Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.
      <div class="btn-row">
        ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Visitar portal oficial')}
      </div>`);
  } finally {
    inpEl.disabled = false;
    inpEl.focus();
  }
}

function go() {
  const val = inpEl.value.trim();
  if (!val) return;
  sendMessage(val);
}

function sendQ(q) {
  inpEl.value = q;
  go();
}

// ── Modal asesor ──────────────────────────────────────────────
function openModal()  { document.getElementById('overlay').classList.add('open'); }
function closeModal() { document.getElementById('overlay').classList.remove('open'); }

async function submitModal() {
  const name = document.getElementById('advisorName').value;
  const email = document.getElementById('advisorEmail').value;
  const phone = document.getElementById('advisorPhone').value;
  const message = document.getElementById('advisorMessage').value;

  if (!name || !email || !message) {
    alert('Por favor completa los campos obligatorios');
    return;
  }

  closeModal();

  try {
    const response = await fetch('/api/advisor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, message })
    });

    if (response.ok) {
      setTimeout(() => {
        addBotMsg(`¡Gracias ${name}! Hemos recibido tu solicitud. Un asesor se pondrá en contacto contigo pronto al correo ${email}.
          <div class="btn-row">
            ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Visitar portal oficial')}
          </div>`);
      }, 500);
    } else {
      throw new Error('Error al enviar solicitud');
    }
  } catch (error) {
    alert('Hubo un error al enviar tu solicitud. Por favor intenta más tarde.');
  }
}

// ── Conexión inmediata con asesor ─────────────────────────
async function connectAdvisorNow() {
  const name = document.getElementById('advisorName')?.value || '';
  const email = document.getElementById('advisorEmail')?.value || '';
  const phone = document.getElementById('advisorPhone')?.value || '';

  showTyping();
  try {
    const response = await fetch('/api/advisor/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, message: 'Solicita conexión inmediata' })
    });

    hideTyping();
    if (!response.ok) throw new Error('No se pudo conectar con el servidor');
    const data = await response.json();

    if (data && data.contact) {
      const c = data.contact;
      let html = `<p>Conectando con un asesor ahora. Puedes usar estos canales:</p><div class="btn-row">`;
      if (c.chat_url) html += `${linkBtn(c.chat_url, 'Abrir chat')}`;
      if (c.phone) html += `${outlineBtn('tel:'+c.phone.replace(/\s+/g,''), 'Llamar al asesor')}`;
      if (c.email) html += `${outlineBtn('mailto:'+c.email, 'Enviar correo')}`;
      html += `</div><p>Si no contestan enseguida, hemos dejado tu solicitud en cola (ID ${data.id}).</p>`;
      addBotMsg(html);
      if (c.chat_url) window.open(c.chat_url, '_blank');
    } else {
      addBotMsg('Tu solicitud ha sido enviada. Un asesor te contactará lo antes posible.');
    }
  } catch (e) {
    hideTyping();
    addBotMsg('Hubo un error al intentar conectar con un asesor. Por favor intenta de nuevo más tarde.');
  }
}

// Focus input on load
if (inpEl) {
  inpEl.focus();
}
