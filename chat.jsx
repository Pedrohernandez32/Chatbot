/* ============================================================
   Chat — asistente virtual funcional (window.claude.complete)
   ============================================================ */
const { useState, useRef, useEffect, useCallback } = React;

const UDEM_CONTEXT = `Eres "Vivi", el asistente virtual oficial de la Universidad de Medellín (UdeMedellín), Colombia.
Hablas SIEMPRE en español, con tono cálido, cercano y profesional. Respuestas breves (2-5 frases), claras y útiles.
Usa la información institucional verificada:
- Universidad privada en Medellín, Antioquia, fundada el 1 de febrero de 1950.
- Lema actual: "Campus Vivo". Acreditada en Alta Calidad por el Ministerio de Educación Nacional (vigente hasta 2027).
- Más de 74.000 egresados. Ofrece 27 pregrados, 36 especializaciones, 21 maestrías y 6 doctorados.
- 7 facultades: Derecho; Ciencias Económicas y Administrativas; Ingenierías; Comunicación; Diseño; Ciencias Básicas; Ciencias Sociales y Humanas.
- Sede principal: Carrera 87 N° 30-65, Medellín. Sede Bogotá: Calle 57 # 9-52, Chapinero.
- Teléfono: +57 (604) 590 4500. Horario: lunes a viernes 8:00 a.m.-12:00 m. y 2:00 p.m.-6:00 p.m.
- Espacios destacados: Teatro Gabriel Obregón Botero (1.702 sillas), Biblioteca Eduardo Fernández Botero, Centro de Idiomas, coliseo y zonas verdes del campus.
- Tipos de aspirante: nuevo, reingreso, transferencia, doble titulación, posgrado.
Si te preguntan algo muy específico (un valor de matrícula exacto, un cupo puntual, una fecha del calendario), orienta y sugiere el canal oficial: udemedellin.edu.co o la línea +57 (604) 590 4500.
Nunca inventes datos. Si no sabes, dilo y remite al canal oficial. No respondas temas ajenos a la universidad.`;

const SUGGESTIONS = [
  { icon: "IconCap",   text: "¿Cómo me inscribo a un pregrado?" },
  { icon: "IconCoin",  text: "¿Qué becas y financiación hay?" },
  { icon: "IconGlobe", text: "Cuéntame del Centro de Idiomas" },
  { icon: "IconMap",   text: "¿Dónde queda el campus?" },
  { icon: "IconBook",  text: "¿Qué programas ofrecen?" },
];

/* --- Bot avatar (formas simples animadas) --- */
function BotAvatar({ size = 46, talking = false }) {
  return (
    <div className="bot-av" style={{ width: size, height: size }}>
      <div className="bot-face">
        <span className="bot-eye" />
        <span className="bot-eye" />
        <span className={"bot-mouth" + (talking ? " talk" : "")} />
      </div>
      <span className="bot-antenna" />
    </div>
  );
}

function CampusGallery() {
  const campusImages = [
    { url: 'https://images.unsplash.com/photo-1427427494494-07fc41aa27ca?w=500&h=300&fit=crop', label: 'Aulas Modernas' },
    { url: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=500&h=300&fit=crop', label: 'Biblioteca' },
    { url: 'https://images.unsplash.com/photo-1541339907198-e7682147d192?w=500&h=300&fit=crop', label: 'Laboratorios' },
    { url: 'https://images.unsplash.com/photo-1532496122399-5d06a7360e47?w=500&h=300&fit=crop', label: 'Deportes' }
  ];

  return (
    <div className="campus-gallery" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginTop: '12px' }}>
      {campusImages.map((img, i) => (
        <div key={i} className="campus-image" style={{ height: '120px', borderRadius: '6px', overflow: 'hidden', position: 'relative' }}>
          <img src={img.url} alt={img.label} style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={(e) => e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><rect fill="%23E53E3E" width="200" height="150"/><text x="50%" y="50%" fill="white" text-anchor="middle" dy=".3em" font-size="14">' + img.label + '</text></svg>'} />
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)', padding: '8px', color: 'white', fontSize: '12px' }}>{img.label}</div>
        </div>
      ))}
    </div>
  );
}

function Bubble({ role, children, animate = true }) {
  const isBot = role === "bot";
  return (
    <div className={"msg " + (isBot ? "msg-bot" : "msg-user")} style={animate ? { animation: "msgIn .4s cubic-bezier(.2,.8,.2,1)" } : null}>
      {isBot && <div className="msg-ava"><BotAvatar size={34} /></div>}
      <div className="msg-bubble">
        {typeof children === 'string' ? (
          <div dangerouslySetInnerHTML={{ __html: children }} />
        ) : (
          children
        )}
      </div>
    </div>
  );
}

function Typing() {
  return (
    <div className="msg msg-bot" style={{ animation: "msgIn .3s ease" }}>
      <div className="msg-ava"><BotAvatar size={34} talking /></div>
      <div className="msg-bubble typing"><span /><span /><span /></div>
    </div>
  );
}

function Chat() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "¡Hola! 👋 Soy Vivi, tu asistente del Campus Vivo. Pregúntame sobre admisiones, programas, becas, el campus o cualquier trámite. ¿En qué te ayudo hoy?" },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showSugg, setShowSugg] = useState(true);
  const [sessionId] = useState(() => Date.now().toString());
  const [savedChats, setSavedChats] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [mostrarEscalada, setMostrarEscalada] = useState(false);
  const scrollRef = useRef(null);

  // Guardar conversación en localStorage
  useEffect(() => {
    if (messages.length > 1) {
      const chats = JSON.parse(localStorage.getItem('chat_history') || '[]');
      const updatedChats = chats.filter(c => c.id !== sessionId);
      updatedChats.push({
        id: sessionId,
        date: new Date().toLocaleString('es-CO'),
        preview: messages[1]?.text?.substring(0, 50) || 'Chat sin título',
        messages: messages.slice(1),
      });
      localStorage.setItem('chat_history', JSON.stringify(updatedChats.slice(-10)));
      setSavedChats(updatedChats.slice(-10));
    }
  }, [messages]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  const send = useCallback(async (text) => {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setShowSugg(false);
    setInput("");
    const next = [...messages, { role: "user", text: q }];
    setMessages(next);
    setBusy(true);
    try {
      const history = next.slice(-8).map(m => `${m.role === "bot" ? "Asistente" : "Usuario"}: ${m.text}`).join("\n");

      // Primero intentar con backend Flask (información local)
      let reply = null;
      let shouldShowGallery = false;
      try {
        const flaskRes = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: q })
        });
        const flaskData = await flaskRes.json();
        if (flaskData.response) {
          try {
            const parsed = JSON.parse(flaskData.response);
            reply = parsed.text || flaskData.response;
            // Mostrar galería si pregunta sobre campus
            if (q.toLowerCase().includes('campus') || q.toLowerCase().includes('instalacion')) {
              shouldShowGallery = true;
            }
          } catch {
            reply = flaskData.response;
          }
        }
      } catch (e) {
        console.log("Backend local no disponible, intentando Claude API");
      }

      // Si no hay respuesta del backend local o es muy genérica, usar Claude API
      if (!reply || reply.length < 30) {
        try {
          if (window.claude && window.claude.complete) {
            const claudeReply = await window.claude.complete({
              messages: [{
                role: "user",
                content: `${UDEM_CONTEXT}\n\nConversación hasta ahora:\n${history}\n\nResponde como Vivi al último mensaje del usuario.`,
              }],
            });
            reply = claudeReply || reply || "Disculpa, no pude procesar eso. ¿Lo intentamos de nuevo?";
          }
        } catch (e) {
          console.log("Claude API no disponible");
        }
      }

      // Convertir markdown a HTML básico
      let htmlReply = (reply || "").trim()
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br/>');

      const botMessage = { role: "bot", text: htmlReply, showGallery: shouldShowGallery };
      setMessages(m => [...m, botMessage]);
    } catch (e) {
      setMessages(m => [...m, { role: "bot", text: "Ups, tuve un problema de conexión. Puedes escribirnos al <strong>+57 (604) 590 4500</strong> o intentar de nuevo en un momento. 🙏" }]);
    } finally {
      setBusy(false);
    }
  }, [input, busy, messages]);

  const onKey = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  const loadChat = (chat) => {
    setMessages(chat.messages);
    setShowHistory(false);
  };

  const clearHistory = () => {
    if (confirm('¿Eliminar todo el historial?')) {
      localStorage.removeItem('chat_history');
      setSavedChats([]);
    }
  };

  const newChat = () => {
    setMessages([
      { role: "bot", text: "¡Hola! 👋 Soy Vivi, tu asistente del Campus Vivo. ¿En qué te ayudo hoy?" },
    ]);
    setInput("");
    setShowSugg(true);
  };

  // Permite que tarjetas/FAQ envíen una pregunta al chat
  useEffect(() => {
    const h = (e) => send(e.detail);
    window.addEventListener("vivi-ask", h);
    return () => window.removeEventListener("vivi-ask", h);
  }, [send]);

  return (
    <div className="chat">
      <div className="chat-head">
        <div className="chat-head-l">
          <BotAvatar size={44} talking={busy} />
          <div>
            <div className="chat-name">Vivi · Asistente Virtual</div>
            <div className="chat-status"><span className="dot-live" />En línea · responde al instante</div>
          </div>
        </div>
        <div className="chat-head-actions">
          <button
            className="chat-btn-icon chat-btn-asesor"
            onClick={() => setMostrarEscalada(true)}
            title="Hablar con un asesor por WhatsApp"
          >
            💬
          </button>
          <button
            className="chat-btn-icon"
            onClick={() => setShowHistory(!showHistory)}
            title="Historial de chats"
          >
            <IconCalendar s={18} />
          </button>
          <button
            className="chat-btn-icon"
            onClick={newChat}
            title="Nuevo chat"
          >
            <IconChat s={18} />
          </button>
          <div className="chat-badge"><IconShield s={14} /> Oficial</div>
        </div>
      </div>

      {showHistory && (
        <div className="chat-history">
          <div className="history-header">
            <h4>📜 Historial</h4>
            <button className="btn-small" onClick={clearHistory}>Limpiar</button>
          </div>
          {savedChats.length === 0 ? (
            <p className="history-empty">Sin conversaciones guardadas</p>
          ) : (
            <div className="history-list">
              {savedChats.reverse().map((chat, i) => (
                <button
                  key={i}
                  className="history-item"
                  onClick={() => loadChat(chat)}
                  title={chat.preview}
                >
                  <div className="history-preview">{chat.preview}</div>
                  <div className="history-date">{chat.date}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="chat-scroll" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i}>
            <Bubble role={m.role} animate={i > 0}>{m.text}</Bubble>
            {m.showGallery && <div style={{ paddingLeft: '50px', paddingRight: '20px' }}><CampusGallery /></div>}
          </div>
        ))}
        {busy && <Typing />}

        {showSugg && (
          <div className="sugg-wrap">
            <div className="sugg-label">Prueba preguntar:</div>
            <div className="sugg-grid">
              {SUGGESTIONS.map((s, i) => {
                const Ic = window[s.icon];
                return (
                  <button key={i} className="sugg" style={{ animationDelay: `${i * 60}ms` }} onClick={() => send(s.text)}>
                    <Ic s={16} /> <span>{s.text}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Escribe tu pregunta…"
          aria-label="Escribe tu pregunta"
        />
        <button className="chat-send" onClick={() => send()} disabled={busy || !input.trim()} aria-label="Enviar">
          <IconSend s={19} />
        </button>
      </div>

      {mostrarEscalada === true && (
        <div className="modal-overlay-asesor" onClick={() => setMostrarEscalada(false)}>
          <div className="modal-asesor" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setMostrarEscalada(false)}>×</button>
            <h3>📞 Habla con un asesor</h3>
            <div className="asesores-grid">
              <button className="asesor-btn" onClick={() => {
                const msg = encodeURIComponent('Hola, tengo una consulta sobre admisiones en UdeMedellin.');
                window.open('https://wa.me/573113610649?text=' + msg, '_blank');
                setMostrarEscalada(false);
              }}>
                <span className="asesor-emoji">📋</span>
                <span className="asesor-nombre">Admisiones</span>
              </button>
              <button className="asesor-btn" onClick={() => {
                const msg = encodeURIComponent('Hola, tengo una consulta sobre becas en UdeMedellin.');
                window.open('https://wa.me/573113610649?text=' + msg, '_blank');
                setMostrarEscalada(false);
              }}>
                <span className="asesor-emoji">💰</span>
                <span className="asesor-nombre">Becas</span>
              </button>
              <button className="asesor-btn" onClick={() => {
                const msg = encodeURIComponent('Hola, necesito soporte técnico en UdeMedellin.');
                window.open('https://wa.me/573113610649?text=' + msg, '_blank');
                setMostrarEscalada(false);
              }}>
                <span className="asesor-emoji">🆘</span>
                <span className="asesor-nombre">Soporte</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { Chat, BotAvatar });
