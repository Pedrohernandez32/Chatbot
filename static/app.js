// DOM Elements
const chatBody = document.getElementById('chatBody');
const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const quickActions = document.querySelectorAll('.quick-action-btn');
const userArea = document.getElementById('userArea');

// API Endpoint
const API_URL = 'http://localhost:5000';

// Current user state
let currentUser = null;

// Initialize on load
window.addEventListener('load', () => {
    checkAuth();
    userInput.focus();
});

/**
 * Modal functions
 */
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function switchModal(fromModalId, toModalId) {
    closeModal(fromModalId);
    openModal(toModalId);
}

// Close modal on backdrop click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

/**
 * Auth functions
 */
async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/api/auth/me`);
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            updateUserUI();
        }
    } catch (e) {
        currentUser = null;
    }
}

function updateUserUI() {
    if (currentUser) {
        userArea.innerHTML = `
            <span class="user-welcome">Bienvenido, ${currentUser.username}</span>
            ${currentUser.is_admin ? '<button class="admin-btn" onclick="openAdminPanel()">Admin</button>' : ''}
            <button class="logout-btn" onclick="logout()">Salir</button>
        `;
    } else {
        userArea.innerHTML = `
            <button class="login-btn" onclick="openModal('loginModal')">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                </svg>
                Iniciar Sesión
            </button>
        `;
    }
}

async function logout() {
    try {
        await fetch(`${API_URL}/api/auth/logout`, { method: 'POST' });
    } catch (e) {
        console.error('Logout error:', e);
    }
    currentUser = null;
    closeAdminPanel();
    updateUserUI();
}

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            closeModal('loginModal');
            updateUserUI();
        } else {
            const data = await response.json();
            alert(data.error || 'Error al iniciar sesión');
        }
    } catch (e) {
        alert('Error al iniciar sesión');
    }
});

// Register form handler
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            closeModal('registerModal');
            updateUserUI();
        } else {
            const data = await response.json();
            alert(data.error || 'Error al registrarse');
        }
    } catch (e) {
        alert('Error al registrarse');
    }
});

/**
 * Admin Panel functions
 */
function openAdminPanel() {
    document.getElementById('adminPanel').style.display = 'block';
    showAdminTab('unknown');
}

function closeAdminPanel() {
    document.getElementById('adminPanel').style.display = 'none';
}

function showAdminTab(tab) {
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    if (tab === 'unknown') {
        loadUnknownQuestions();
    } else {
        loadLearnedResponses();
    }
}

async function loadUnknownQuestions() {
    try {
        const response = await fetch(`${API_URL}/api/admin/unknown`);
        if (response.ok) {
            const data = await response.json();
            renderUnknownQuestions(data.questions);
        } else {
            document.getElementById('adminContent').innerHTML = '<p>No tienes acceso a esta información.</p>';
        }
    } catch (e) {
        document.getElementById('adminContent').innerHTML = '<p>Error al cargar preguntas.</p>';
    }
}

function renderUnknownQuestions(questions) {
    const content = document.getElementById('adminContent');
    if (questions.length === 0) {
        content.innerHTML = '<p class="no-data">No hay preguntas pendientes de revisión.</p>';
        return;
    }
    content.innerHTML = questions.map(q => `
        <div class="admin-item">
            <div class="admin-item-header">
                <span class="votes">👍 ${q.upvotes} 👎 ${q.downvotes}</span>
                <span class="date">${new Date(q.created_at).toLocaleDateString()}</span>
            </div>
            <p class="question"><strong>Pregunta:</strong> ${escapeHtml(q.question)}</p>
            <p class="answer"><strong>Respuesta anterior:</strong> ${escapeHtml(q.answer || 'Sin respuesta')}</p>
            <form class="learn-form" onsubmit="createLearnedResponse(event, ${q.id})">
                <input type="hidden" name="question" value="${escapeHtml(q.question)}">
                <input type="text" name="answer" placeholder="Nueva respuesta" required>
                <input type="text" name="keywords" placeholder="Palabras clave (separadas por coma)" value="${escapeHtml(q.question.toLowerCase())}" required>
                <button type="submit" class="create-btn">Crear respuesta aprendida</button>
            </form>
        </div>
    `).join('');
}

async function loadLearnedResponses() {
    try {
        const response = await fetch(`${API_URL}/api/admin/learn`);
        if (response.ok) {
            const data = await response.json();
            renderLearnedResponses(data.responses);
        }
    } catch (e) {
        document.getElementById('adminContent').innerHTML = '<p>Error al cargar respuestas aprendidas.</p>';
    }
}

function renderLearnedResponses(responses) {
    const content = document.getElementById('adminContent');
    if (responses.length === 0) {
        content.innerHTML = '<p class="no-data">No hay respuestas aprendidas.</p>';
        return;
    }
    content.innerHTML = responses.map(r => `
        <div class="admin-item">
            <div class="admin-item-header">
                <span class="usage">Usada ${r.usage_count} veces</span>
                <span class="date">${new Date(r.created_at).toLocaleDateString()}</span>
            </div>
            <p class="keywords"><strong>Palabras clave:</strong> ${escapeHtml(r.keywords)}</p>
            <p class="answer-text"><strong>Respuesta:</strong> ${escapeHtml(r.answer)}</p>
            <button class="delete-btn" onclick="deleteLearnedResponse(${r.id})">Eliminar</button>
        </div>
    `).join('');
}

async function createLearnedResponse(event, convId) {
    event.preventDefault();
    const form = event.target;
    const answer = form.answer.value;
    const keywords = form.keywords.value;
    const question = form.question.value;

    try {
        const response = await fetch(`${API_URL}/api/admin/learn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, answer, keywords })
        });

        if (response.ok) {
            alert('Respuesta aprendida creada');
            showAdminTab('learned');
        }
    } catch (e) {
        alert('Error al crear respuesta aprendida');
    }
}

async function deleteLearnedResponse(id) {
    if (!confirm('¿Estás seguro de eliminar esta respuesta aprendida?')) return;

    try {
        const response = await fetch(`${API_URL}/api/admin/learn/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadLearnedResponses();
        }
    } catch (e) {
        alert('Error al eliminar respuesta');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * SVG Icons
 */
function getBotAvatar() {
    return `<svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.07 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
    </svg>`;
}

function getUserAvatar() {
    return `<svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>`;
}

function getSparkleIcon() {
    return `<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
        <path d="M12 2L13.09 8.26L19.63 6.64L15.56 11.56L21.09 15.27L14.55 14.64L13.09 22L11.64 14.64L5.09 15.27L10.63 11.56L6.56 6.64L13.09 8.26L12 2Z"/>
    </svg>`;
}

/**
 * Create a message element
 */
function createMessage(content, isUser = false, isAI = false, convId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = isUser ? getUserAvatar() : getBotAvatar();

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = `<p>${formatMessage(content)}</p>`;

    contentDiv.appendChild(textDiv);

    // Add AI badge for AI responses
    if (isAI && !isUser) {
        const badge = document.createElement('div');
        badge.className = 'ai-badge';
        badge.innerHTML = `${getSparkleIcon()} IA`;
        contentDiv.appendChild(badge);
    }

    // Add feedback buttons for bot messages (only if convId provided)
    if (!isUser && convId) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons';
        feedbackDiv.innerHTML = `
            <button class="feedback-btn up" onclick="submitFeedback(${convId}, 'up', this)" title="Me gusta">👍</button>
            <button class="feedback-btn down" onclick="submitFeedback(${convId}, 'down', this)" title="No me gusta">👎</button>
        `;
        contentDiv.appendChild(feedbackDiv);
    }

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

async function submitFeedback(convId, vote, button) {
    // Disable buttons
    const buttons = button.parentElement.querySelectorAll('button');
    buttons.forEach(b => b.disabled = true);

    try {
        await fetch(`${API_URL}/api/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conv_id: convId, vote })
        });

        // Show thank you
        button.parentElement.innerHTML = '<span class="feedback-thanks">¡Gracias!</span>';
    } catch (e) {
        // Re-enable buttons on error
        buttons.forEach(b => b.disabled = false);
    }
}

/**
 * Format message content
 */
function formatMessage(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

/**
 * Create typing indicator
 */
function createTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typingIndicator';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = getBotAvatar();

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';

    textDiv.appendChild(indicator);
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Scroll to bottom of chat
 */
function scrollToBottom() {
    chatBody.scrollTo({
        top: chatBody.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Send message to API
 */
async function sendMessage(text) {
    if (!text.trim()) return;

    // Add user message
    const userMessage = createMessage(text, true);
    messagesContainer.appendChild(userMessage);
    scrollToBottom();

    // Clear input
    userInput.value = '';
    userInput.disabled = true;

    // Show typing indicator
    const typingIndicator = createTypingIndicator();
    messagesContainer.appendChild(typingIndicator);
    scrollToBottom();

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text }),
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.error) {
            throw new Error(data.error);
        }

        // Add bot response with convId for feedback
        const botMessage = createMessage(data.response, false, data.ai, data.conv_id);
        messagesContainer.appendChild(botMessage);
        scrollToBottom();

    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();

        const errorMessage = createMessage(
            'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
            false,
            false
        );
        messagesContainer.appendChild(errorMessage);
        scrollToBottom();
    } finally {
        userInput.disabled = false;
        userInput.focus();
    }
}

/**
 * Handle quick action buttons
 */
function handleQuickAction(question) {
    sendMessage(question);
}

// Event Listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

quickActions.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.dataset.question;
        sendMessage(question);
    });
});

// Handle Enter key
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Handle visibility change
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        userInput.focus();
    }
});