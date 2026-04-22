// ============================================================
//  CHATBOT UNIVERSIDAD DE MEDELLÍN — chatbot.js
// ============================================================

const msgsEl = document.getElementById('msgs');
const inpEl  = document.getElementById('inp');

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

setInterval(() => goSlide((currentSlide + 1) % galleryLabels.length), 3200);

// ── Avatares ─────────────────────────────────────────────────
function botAvatar() {
  return `<div class="av av-bot">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zm-2 10H6V7h12v12zm-9-6c-.83 0-1.5-.67-1.5-1.5S8.17 10 9 10s1.5.67 1.5 1.5S9.83 13 9 13zm7.5-1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zM8 15h8v2H8v-2z"/>
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
  div.innerHTML = `${userAvatar()}<div class="bubble user-b">${text}</div>`;
  msgsEl.appendChild(div);
  scrollToBottom();
}

function addBotMsg(html) {
  const div = document.createElement('div');
  div.className = 'msg';
  div.innerHTML = `${botAvatar()}<div class="bubble bot-b">${html}</div>`;
  msgsEl.appendChild(div);
  scrollToBottom();
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

// ── Respuestas del chatbot ────────────────────────────────────
function getReply(q) {
  const ql = q.toLowerCase();

  if (ql.includes('horario') || ql.includes('hora') || ql.includes('atención'))
    return `Nuestros horarios de atención son:<br><br>
      • <strong>Lun–Vie:</strong> 7:00 a.m. – 8:00 p.m.<br>
      • <strong>Sábados:</strong> 8:00 a.m. – 1:00 p.m.<br><br>
      Algunas dependencias manejan horarios propios. ¿Necesitas info de una oficina específica?`;

  if (ql.includes('ubic') || ql.includes('dónde') || ql.includes('queda') || ql.includes('dirección'))
    return `Estamos en <strong>Cra. 87 #30-65, Belén, Medellín</strong>.<br><br>
      Puedes llegar en Metro hasta <em>San Javier</em> y tomar una ruta alimentadora. También hay parqueadero en el campus.
      <div class="btn-row">
        ${linkBtn('https://maps.google.com/?q=Universidad+de+Medellin,+Belen', 'Ver en Google Maps')}
      </div>`;

  if (ql.includes('carrera') || ql.includes('program') || ql.includes('ofrec'))
    return `Ofrecemos programas en:<br>
      <ul>
        <li>Ingenierías y Ciencias Básicas</li>
        <li>Ciencias Económicas y Administrativas</li>
        <li>Ciencias Sociales y Humanas</li>
        <li>Derecho</li>
        <li>Comunicación</li>
      </ul>
      También tenemos <strong>especializaciones, maestrías y doctorados</strong>.
      <div class="btn-row">
        ${linkBtn('https://admisiones.udemedellin.edu.co', 'Ver todos los programas')}
        ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Portal de admisiones')}
      </div>`;

  if (ql.includes('inscri') || ql.includes('matrícula'))
    return `Para inscribirte puedes:<br><br>
      1. Diligenciar el formulario en línea<br>
      2. Adjuntar los documentos requeridos<br>
      3. Realizar el pago de inscripción<br><br>
      El proceso es rápido y puedes hacerlo desde casa.
      <div class="btn-row">
        ${linkBtn('https://admisiones.udemedellin.edu.co', 'Iniciar inscripción ahora')}
      </div>`;

  if (ql.includes('contact') || ql.includes('teléfono') || ql.includes('llamar'))
    return `Nuestros canales de contacto:<br><br>
      • <strong>Tel:</strong> (604) 340 5555<br>
      • <strong>Email:</strong> info@udem.edu.co<br>
      • <strong>WhatsApp:</strong> 300 000 0000<br>
      • Presencialmente en Belén
      <div class="btn-row">
        ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Portal de admisiones')}
      </div>`;

  if (ql.includes('beca') || ql.includes('ayuda') || ql.includes('económi') || ql.includes('financ') || ql.includes('descuento'))
    return `Contamos con varias formas de apoyo económico:<br>
      <ul>
        <li>Becas por mérito académico</li>
        <li>Becas deportivas y culturales</li>
        <li>Créditos ICETEX</li>
        <li>Descuentos para egresados y familias</li>
        <li>Auxilio socioeconómico</li>
      </ul>
      ¿Deseas conocer los requisitos y cómo aplicar?
      <div class="btn-row">
        ${linkBtn('https://admisiones.udemedellin.edu.co/becas-descuentos-y-financiacion-de-pregrado/', 'Ver becas y financiación')}
        ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Portal de admisiones')}
      </div>`;

  if (ql.includes('admis'))
    return `El proceso de admisión tiene estos pasos:<br><br>
      1. <strong>Inscripción</strong> en línea o presencial<br>
      2. <strong>Entrega</strong> de documentos requeridos<br>
      3. <strong>Prueba</strong> de aptitud (algunos programas)<br>
      4. <strong>Confirmación</strong> de admisión<br><br>
      ¿Te interesa algún programa específico?
      <div class="btn-row">
        ${linkBtn('https://admisiones.udemedellin.edu.co', 'Iniciar proceso de admisión')}
      </div>`;

  if (ql.includes('bibliote'))
    return `La <strong>Biblioteca Alfonso Mora Naranjo</strong> atiende:<br><br>
      • Lun–Vie: 7:00 a.m. – 9:00 p.m.<br>
      • Sábados: 8:00 a.m. – 5:00 p.m.<br><br>
      Ofrece bases de datos digitales, salas de estudio y préstamo de libros físicos y digitales.`;

  // Respuesta por defecto
  return `Gracias por tu mensaje. Para orientarte mejor, visita nuestro portal oficial o contáctanos directamente.
    <div class="btn-row">
      ${linkBtn('https://admisiones.udemedellin.edu.co', 'Visitar portal oficial')}
    </div>`;
}

// ── Enviar mensaje ────────────────────────────────────────────
function go() {
  const val = inpEl.value.trim();
  if (!val) return;
  addUserMsg(val);
  inpEl.value = '';
  showTyping();
  const delay = 900 + Math.random() * 400;
  setTimeout(() => {
    hideTyping();
    addBotMsg(getReply(val));
  }, delay);
}

// También permite enviar desde las pills y chips
function sendQ(q) {
  inpEl.value = q;
  go();
}

// ── Modal asesor ──────────────────────────────────────────────
function openModal()  { document.getElementById('overlay').classList.add('open'); }
function closeModal() { document.getElementById('overlay').classList.remove('open'); }

function submitModal() {
  closeModal();
  setTimeout(() => {
    addBotMsg(`¡Solicitud enviada con éxito! Un asesor se pondrá en contacto contigo pronto.
      <div class="btn-row">
        ${outlineBtn('https://admisiones.udemedellin.edu.co', 'Visitar portal mientras tanto')}
      </div>`);
  }, 200);
}
