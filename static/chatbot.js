// FAQ Database - Based on ai_plugin.py
const FAQ = {
    horario: "La universidad atiende de lunes a viernes de 9 a 18 hs.",
    ubicacion: "La universidad se encuentra en Cra. 87 #30-65, Medellín, Belén, Medellín, Antioquia.",
    carrera: "Ofrecemos Ingeniería, Administración y Psicología.",
    inscripcion: "La inscripción para el próximo cuatrimestre comienza en marzo.",
    contacto: "Puedes escribir a info@udem.edu.co o llamar al (011) 1234-5678.",
    titulo: "El título que entregamos es de grado universitario.",
    aulas: "Las clases se dictan en el edificio principal y en el anexo de Ciencias Sociales.",
    biblioteca: "La biblioteca abre de lunes a viernes de 8 a 20 hs y sábados de 9 a 14 hs.",
    becas: "Las becas y ayudas económicas se gestionan en Secretaría Estudiantil.",
    profesores: "Los datos de los profesores se publican en la plataforma académica y el sitio web de la universidad.",
    materias: "Las materias disponibles están en el plan de estudios y en la oferta académica del cuatrimestre.",
    admision: "La admisión se realiza con un examen de ingreso; consulta fechas y requisitos en el sitio oficial."
};

// Synonyms for flexible matching
const SYNONYMS = {
    horario: [
        "horario", "cuando abre", "cuando cierra", "a que hora",
        "que hora", "jornada", "horas", "atencion", "abren", "cierran"
    ],
    ubicacion: [
        "donde", "ubicacion", "direccion", "localizacion",
        "sitio", "direccion exacta", "queda", "ubicada", "lugar"
    ],
    carrera: [
        "carrera", "programa", "oferta academica", "especialidad",
        "estudio", "grado", "carreras", "estudiar", "profesion"
    ],
    inscripcion: [
        "inscripcion", "matricula", "registro", "inscribirme",
        "preinscripcion", "inscribirse", "plazo", "inscribir", "requisitos"
    ],
    contacto: [
        "contacto", "telefono", "email", "correo",
        "llamar", "telefonos", "contactar", "escribir", "comunicar"
    ],
    titulo: [
        "titulo", "grado", "certificado", "diploma",
        "titulacion", "certifica", "recibo"
    ],
    aulas: [
        "aula", "salon", "edificio", "clase",
        "sala", "aulas", "salones", "donde dan clases"
    ],
    biblioteca: [
        "biblioteca", "libros", "sala de lectura",
        "prestamo", "libreria", "leer", "estudiar biblioteca"
    ],
    becas: [
        "becas", "ayuda economica", "subsidio",
        "financiacion", "descuento", "beca", "pago", "costo"
    ],
    profesores: [
        "profesores", "docentes", "catedraticos",
        "maestros", "jefes de catedra", "profesor", "docente"
    ],
    materias: [
        "materias", "asignaturas", "curso",
        "cursos", "clases", "materia", "asignatura", "ver materias"
    ],
    admision: [
        "admision", "ingreso", "examen",
        "prueba", "requisitos", "entrar", "admitir", "ingresar"
    ]
};

/**
 * Normalize text: remove accents, lowercase, remove special chars
 */
function normalizeText(text) {
    return text
        .normalize('NFKD')
        .replace(/[\u0300-\u036f]/g, '')
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

    const promptNorm = normalizeText(prompt);
    const keywords = ['universidad', 'pregunta', 'informacion', 'profesor', 'campus', 'hola', 'ayuda'];

    if (keywords.some(word => promptNorm.includes(word))) {
        return "Sobre la universidad puedo decirte horarios, ubicación, inscripciones, carreras y más. Prueba preguntando sobre algo específico como horarios, ubicación o becas.";
    }

    return "No estoy seguro de entender tu pregunta. Puedo ayudarte con información sobre horarios, ubicación, carreras, inscripciones, becas, biblioteca y más. ¿Podrías reformular tu pregunta?";
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