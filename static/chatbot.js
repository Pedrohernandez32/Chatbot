// FAQ Database - Universidad de Medellín
const FAQ = {
    horario: "Horario de atención: Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.",

    ubicacion: "Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.",

    carreras: `<strong>Carreras disponibles:</strong><br>
• Administración de Empresas (SNIES: 1514)<br>
• Ciencia Política (SNIES: 105770)<br>
• Computación Científica (SNIES: 103268)<br>
• Comunicación Gráfica Publicitaria (SNIES: 11128)<br>
• Comunicación y Entretenimiento Digital (SNIES: 103763)<br>
• Comunicación y Lenguajes Audiovisuales (SNIES: 14880)<br>
• Comunicación y Relaciones Corporativas (SNIES: 3136)<br>
• Derecho (SNIES: 1512)<br>
• Diseño y Gestión de Espacios (SNIES: 105470)<br>
• Diseño y Gestión de la Moda y el Textil (SNIES: 105469)<br>
• Diseño y Gestión del Producto (SNIES: 105468)<br>
• Economía (SNIES: 1513)<br>
• Ingeniería Ambiental (SNIES: 3193)<br>
• Ingeniería Civil (SNIES: 1516)<br>
• Ingeniería de Sistemas (SNIES: 3134)<br>
• Ingeniería Financiera (SNIES: 7255)<br>
• Ingeniería Industrial (SNIES: 103149)<br>
• Investigación Criminal (SNIES: 90781)<br>
• Mercadeo (SNIES: 52403)<br>
• Negocios Internacionales (SNIES: 15243)<br>
• Psicología`,

    inscripcion: "Para inscribirte, debes contactar a la universidad por teléfono o visitar su sede. El proceso de inscripción se realiza directamente en la universidad.",

    contacto: `Contacto Universidad de Medellín:<br>
• Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999<br>
• Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia<br>
• Sede Bogotá: Calle 57 # 9-52, Chapinero<br>
• Notificaciones judiciales: corresrec@udemedellin.edu.co`,

    becas: `<strong>Becas y Estímulos disponibles:</strong><br>
• BECA SOCIAL<br>
• BECA DE HONOR<br>
• BECA DE EXCELENCIA<br>
• BECA MEJORES SABER PRO<br>
• ESTÍMULOS MONITORÍAS ACADÉMICAS<br>
• ESTÍMULOS ACTIVIDADES DEPORTIVAS<br>
• ESTÍMULOS ACTIVIDADES CULTURALES Y ARTÍSTICAS<br>
• ESTÍMULO PARA PARTICIPACIONES DESTACADAS EN EVENTOS ACADÉMICOS EXTRACURRICULARES DE RECONOCIDO PRESTIGIO NACIONAL E INTERNACIONAL<br>
• ESTÍMULO MULTILINGÜISMO`,

    admision: "La institución es de educación superior sujeta a la inspección y vigilancia del Ministerio de Educación Nacional. Para información sobre admisión, contacta a la universidad directamente.",

    biblioteca: "Para información sobre la biblioteca, contacta a la universidad por teléfono o visita su sede principal.",

    general: "Universidad de Medellín - Puedo ayudarte con información sobre carreras, contacto, horarios, becas e inscripciones. ¿Qué te gustaría saber?"
};

// Synonyms for flexible matching
const SYNONYMS = {
    horario: [
        "horario", "cuando abre", "cuando cierra", "a que hora",
        "que hora", "jornada", "horas", "atencion", "abren", "cierran",
        "lunes", "viernes", "8:00", "12:00", "2:00", "18:00"
    ],
    ubicacion: [
        "donde", "ubicacion", "direccion", "localizacion",
        "sitio", "direccion exacta", "queda", "ubicada", "lugar",
        "medellin", "bogota", "sede", "carrera 87", "chapinero"
    ],
    carrera: [
        "carrera", "programa", "oferta academica", "especialidad",
        "estudio", "grado", "carreras", "estudiar", "profesion",
        "administracion", "ingenieria", "comunicacion", "derecho",
        "psicologia", "economia", "diseno", "mercadeo", "negocios",
        "snies", "carreras disponibles", "que carreras"
    ],
    inscripcion: [
        "inscripcion", "matricula", "registro", "inscribirme",
        "preinscripcion", "inscribirse", "plazo", "inscribir", "requisitos",
        "como me inscribo", "inscribir"
    ],
    contacto: [
        "contacto", "telefono", "email", "correo", "llamar",
        "telefonos", "contactar", "escribir", "comunicar", "whatsapp",
        "notificaciones judiciales", "corresrec"
    ],
    becas: [
        "becas", "ayuda economica", "subsidio", "financiacion",
        "descuento", "beca", "pago", "costo", "estímulos", "monitorias",
        "beca social", "beca honor", "beca excelencia", "becas y estimulos"
    ],
    admision: [
        "admision", "ingreso", "examen", "prueba", "requisitos",
        "entrar", "admitir", "ingresar", "ministerio de educacion"
    ],
    biblioteca: [
        "biblioteca", "libros", "sala de lectura", "préstamo",
        "libreria", "leer", "estudiar biblioteca"
    ]
};

/**
 * Normalize text: remove accents, lowercase, remove special chars
 */
function normalizeText(text) {
    return text
        .normalize('NFKD')
        .replace(/[̀-ͯ]/g, '')
        .toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

/**
 * Tokenize text into a Set of words
 */
function tokenize(text) {
    return new Set(normalizeText(text).split(' ').filter(w => w.length > 0));
}

/**
 * Find the best matching topic for a given prompt
 */
function bestTopicForPrompt(prompt) {
    const promptNorm = normalizeText(prompt);
    const promptTokens = tokenize(promptNorm);

    // Direct phrase matching
    for (const [topic, phrases] of Object.entries(SYNONYMS)) {
        for (const phrase of phrases) {
            if (promptNorm.includes(normalizeText(phrase))) {
                return topic;
            }
        }
    }

    // Token-based matching with scoring
    let bestTopic = null;
    let bestScore = 0;

    for (const [topic, phrases] of Object.entries(SYNONYMS)) {
        const keywordTokens = new Set();
        for (const phrase of phrases) {
            tokenize(phrase).forEach(t => keywordTokens.add(t));
        }

        // Calculate intersection
        const common = [...promptTokens].filter(t => keywordTokens.has(t));
        if (common.length === 0) continue;

        const score = common.length / Math.max(1, keywordTokens.size);
        if (score > bestScore) {
            bestScore = score;
            bestTopic = topic;
        }
    }

    return bestScore >= 0.15 ? bestTopic : null;
}

/**
 * Main handler for generating responses
 */
function getResponse(prompt) {
    const topic = bestTopicForPrompt(prompt);

    if (topic !== null) {
        return FAQ[topic];
    }

    return FAQ.general;
}

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const quickButtons = document.querySelectorAll('.quick-btn');

// Advisor Modal Elements
const advisorModal = document.getElementById('advisorModal');
const advisorModalClose = document.getElementById('advisorModalClose');
const advisorForm = document.getElementById('advisorForm');

// API Endpoint
const API_URL = window.location.origin;

// Track failed attempts for this conversation
let failedAttempts = 0;
const MAX_ATTEMPTS_BEFORE_ADVISOR = 2;

/**
 * Create a message element
 */
function createMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = isUser
        ? '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.07 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<p>${content}</p>`;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message bot-message typing';
    indicator.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.07 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return indicator;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.remove();
    }
}

/**
 * Create advisor offer message element
 */
function createAdvisorOffer() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message advisor-offer';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.07 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
        </div>
        <div class="message-content">
            <p>¿Necesitas más ayuda? Puedo conectarte con un asesor humano que podrá resolver tu consulta.</p>
            <button class="contact-advisor-btn" id="contactAdvisorBtn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
                Contactar asesor
            </button>
        </div>
    `;

    // Add click handler for the button
    setTimeout(() => {
        const btn = document.getElementById('contactAdvisorBtn');
        if (btn) {
            btn.addEventListener('click', () => {
                advisorModal.classList.add('active');
            });
        }
    }, 100);

    return messageDiv;
}

/**
 * Send a message
 */
async function sendMessage(text) {
    if (!text.trim()) return;

    // Add user message
    const userMessage = createMessage(text, true);
    chatMessages.appendChild(userMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Clear input
    userInput.value = '';
    userInput.disabled = true;

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        removeTypingIndicator(typingIndicator);

        if (data.error) {
            throw new Error(data.error);
        }

        const botMessage = createMessage(data.response);
        chatMessages.appendChild(botMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Check if bot couldn't understand (fallback response)
        if (!data.ai && (data.response.includes("No tengo") || data.response.includes("Lo siento"))) {
            failedAttempts++;
            if (failedAttempts >= MAX_ATTEMPTS_BEFORE_ADVISOR) {
                failedAttempts = 0;
                setTimeout(() => {
                    const advisorOffer = createAdvisorOffer();
                    chatMessages.appendChild(advisorOffer);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 1000);
            }
        }
    } catch (error) {
        removeTypingIndicator(typingIndicator);
        const botMessage = createMessage("Lo siento, hubo un error. Por favor intenta de nuevo.");
        chatMessages.appendChild(botMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
        userInput.disabled = false;
        userInput.focus();
    }
}

// Event Listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

quickButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.dataset.question;
        sendMessage(question);
    });
});

// Focus input on load
userInput.focus();

// Advisor Modal Events
advisorModalClose.addEventListener('click', () => {
    advisorModal.classList.remove('active');
});

advisorModal.addEventListener('click', (e) => {
    if (e.target === advisorModal) {
        advisorModal.classList.remove('active');
    }
});

advisorForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('advisorName').value;
    const email = document.getElementById('advisorEmail').value;
    const phone = document.getElementById('advisorPhone').value;
    const message = document.getElementById('advisorMessage').value;

    // Show success message in chat
    advisorModal.classList.remove('active');

    const successMessage = createMessage(`¡Gracias ${name}! Hemos recibido tu solicitud. Un asesor se comunicará contigo pronto a ${email}.`, false);
    chatMessages.appendChild(successMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Reset form
    advisorForm.reset();

    // Log data (in real app, send to server)
    console.log('Advisor request:', { name, email, phone, message });
});
