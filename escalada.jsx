/* Componente de escalada a operadores por WhatsApp */
const { useState } = React;

const OPERADORES = {
    admisiones: { nombre: 'Asesor de Admisiones', numero: '+573113610649', emoji: '📋' },
    becas: { nombre: 'Asesor de Becas', numero: '+573113610649', emoji: '💰' },
    soporte: { nombre: 'Soporte General', numero: '+573113610649', emoji: '🆘' }
};

function EscaladaWhatsApp({ mostrar, tema, onCerrar }) {
    const [mensaje, setMensaje] = useState('Hola, tengo una consulta sobre UdeMedellin.');

    if (!mostrar) return null;

    const operador = OPERADORES[tema] || OPERADORES.soporte;
    const numeroLimpio = operador.numero.replace('+', '');
    const mensajeCodificado = encodeURIComponent(mensaje);
    const enlaceWhatsApp = `https://wa.me/${numeroLimpio}?text=${mensajeCodificado}`;

    return (
        <div className="modal-overlay" onClick={onCerrar}>
            <div className="modal-escalada" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onCerrar}>×</button>

                <div className="escalada-header">
                    <span className="escalada-emoji">{operador.emoji}</span>
                    <h3>Habla con un operador real</h3>
                    <p>Tu consulta será atendida por {operador.nombre}</p>
                </div>

                <div className="escalada-content">
                    <label>
                        <strong>Tu mensaje:</strong>
                        <textarea
                            value={mensaje}
                            onChange={(e) => setMensaje(e.target.value)}
                            placeholder="Cuéntanos tu pregunta..."
                            maxLength="500"
                        />
                        <small>{mensaje.length}/500</small>
                    </label>

                    <div className="escalada-info">
                        <strong>📞 Contacto WhatsApp:</strong>
                        <p className="numero-whatsapp">{operador.numero}</p>
                        <p className="info-texto">Se abrirá WhatsApp en tu celular o computadora</p>
                    </div>

                    <a href={enlaceWhatsApp} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                        💬 Abrir WhatsApp
                    </a>

                    <button className="btn-cancelar" onClick={onCerrar}>Cancelar</button>
                </div>
            </div>
        </div>
    );
}

Object.assign(window, { EscaladaWhatsApp });
