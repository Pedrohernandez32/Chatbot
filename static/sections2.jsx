/* ============================================================
   Sections 2 — Stats, Campus, FAQ, Footer
   ============================================================ */
const { useState, useEffect, useRef } = React;


/* ---- Count-up stat ---- */
function Stat({ value, suffix = "", label, Ic }) {
  const [n, setN] = useState(0);
  const ref = useRef(null);
  const done = useRef(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver((es) => {
      es.forEach(e => {
        if (e.isIntersecting && !done.current) {
          done.current = true;
          const dur = 1400, t0 = performance.now();
          const tick = (t) => {
            const p = Math.min((t - t0) / dur, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            setN(Math.round(value * eased));
            if (p < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      });
    }, { threshold: .4 });
    io.observe(el);
    return () => io.disconnect();
  }, [value]);
  return (
    <div className="stat reveal" ref={ref}>
      <div className="stat-ic"><Ic s={22} /></div>
      <div className="stat-n">{n.toLocaleString("es-CO")}<em>{suffix}</em></div>
      <div className="stat-l">{label}</div>
    </div>
  );
}

function Stats() {
  return (
    <section className="sec stats-sec">
      <div className="wrap">
        <div className="stats-band">
          <Stat value={1950} label="Año de fundación" Ic={IconFlame} />
          <Stat value={74000} suffix="+" label="Egresados en el mundo" Ic={IconUsers} />
          <Stat value={27} label="Programas de pregrado" Ic={IconCap} />
          <Stat value={7} label="Facultades" Ic={IconBook} />
        </div>
      </div>
    </section>
  );
}

/* ---- Campus gallery (fotos reales del campus) ---- */
const CAMPUS = [
  { img: "assets/campus-monumento.jpg", Ic: IconFlame, t: "Campus Vivo", d: "La entrada de nuestro campus, donde la comunidad se encuentra cada día.", big: true },
  { img: "assets/campus-aereo.jpg", Ic: IconCampus, t: "Nuestros bloques", d: "Aulas, auditorios y zonas verdes integradas en un solo lugar." },
  { img: "assets/biblioteca.webp", Ic: IconBook, t: "Biblioteca", d: "Biblioteca Eduardo Fernández Botero · Bloque 13." },
];

function Campus() {
  return (
    <section className="sec campus" id="campus">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <div className="eyebrow reveal">Conoce el lugar</div>
            <h2 className="reveal d1">Un campus que se siente vivo</h2>
          </div>
          <p className="sec-head-p reveal d2">Espacios para aprender, crear y vivir la universidad.</p>
        </div>
        <div className="campus-grid">
          {CAMPUS.map((c, i) => (
            <figure key={i} className={"campus-card reveal d" + ((i % 3) + 1) + (c.big ? " campus-big" : "")}>
              <img className="campus-img" src={c.img} alt={c.t} loading="lazy" />
              <figcaption>
                <span className="campus-chip"><c.Ic s={16} /> {c.t}</span>
                <p>{c.d}</p>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---- FAQ accordion ---- */
const FAQS = [
  { q: "¿Quién es Vivi y cómo funciona?", a: "Vivi es el asistente virtual de la Universidad de Medellín. Responde tus dudas sobre admisiones, programas, becas, trámites y la vida en el campus al instante, las 24 horas." },
  { q: "¿La información del chat es oficial?", a: "Vivi se basa en información institucional de la Universidad de Medellín. Para valores exactos, fechas y trámites puntuales, siempre te remite a los canales oficiales: udemedellin.edu.co y la línea +57 (604) 590 4500." },
  { q: "¿Cómo inicio mi proceso de admisión?", a: "Identifica tu tipo de aspirante (nuevo, reingreso, transferencia o posgrado), elige tu programa y completa la inscripción en línea. Pregúntale a Vivi y te guía paso a paso según tu caso." },
  { q: "¿Atienden en sede Bogotá?", a: "Sí. La sede principal está en Medellín (Carrera 87 N° 30-65) y hay sede en Bogotá (Calle 57 # 9-52, Chapinero). Horario: lunes a viernes, 8:00 a.m.–12:00 m. y 2:00 p.m.–6:00 p.m." },
  { q: "¿Puedo preguntar en cualquier momento?", a: "¡Claro! El asistente está disponible siempre. Escribe tu pregunta en el chat de arriba o toca una de las sugerencias para empezar." },
];

function Faq({ onAsk }) {
  const [open, setOpen] = useState(0);
  return (
    <section className="sec faq" id="faq">
      <div className="wrap faq-in">
        <div className="faq-side reveal">
          <div className="eyebrow">Resuelve rápido</div>
          <h2>Preguntas<br />frecuentes</h2>
          <p>¿No encuentras lo que buscas? Vivi responde cualquier cosa sobre la UdeMedellín.</p>
          <button className="btn btn-primary" onClick={() => onAsk("Tengo una pregunta sobre la Universidad de Medellín")}>
            <IconChat s={17} /> Preguntar al asistente
          </button>
        </div>
        <div className="faq-list">
          {FAQS.map((f, i) => (
            <div key={i} className={"faq-item reveal d" + ((i % 3) + 1) + (open === i ? " open" : "")}>
              <button className="faq-q" onClick={() => setOpen(open === i ? -1 : i)}>
                <span><span className="faq-num">{String(i + 1).padStart(2, "0")}</span>{f.q}</span>
                <span className="faq-plus"><IconArrow s={18} /></span>
              </button>
              <div className="faq-a"><p>{f.a}</p></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---- Footer ---- */
function Footer() {
  return (
    <footer className="footer" id="contacto">
      <div className="footer-cta wrap">
        <div className="footer-cta-card">
          <div className="fc-bot"><BotAvatar size={60} /></div>
          <div className="fc-txt">
            <h3>¿Listo para empezar tu camino?</h3>
            <p>Vivi te acompaña en cada paso de tu vida universitaria.</p>
          </div>
          <a href="#asistente" className="btn btn-green"><IconSpark s={18} /> Hablar con Vivi</a>
        </div>
      </div>
      <div className="wrap footer-grid">
        <div className="footer-brand">
          <Brand light />
          <p>Institución de educación superior sujeta a inspección y vigilancia del Ministerio de Educación Nacional. Acreditada en Alta Calidad.</p>
        </div>
        <div className="footer-col">
          <h4>Contacto</h4>
          <a href="tel:+576045904500"><IconPhone s={15} /> +57 (604) 590 4500</a>
          <a href="#"><IconMail s={15} /> info@udemedellin.edu.co</a>
          <a href="#"><IconMap s={15} /> Carrera 87 N° 30-65, Medellín</a>
          <span><IconClock s={15} /> Lun a Vie · 8:00–12:00 / 14:00–18:00</span>
        </div>
        <div className="footer-col">
          <h4>Accesos</h4>
          <a href="#asistente">Asistente Virtual</a>
          <a href="#acceso">Iniciar sesión</a>
          <a href="#servicios">Becas y financiación</a>
          <a href="#campus">Campus Vivo</a>
        </div>
        <div className="footer-col">
          <h4>Síguenos</h4>
          <div className="socials">
            <a key="ig" className="social" href="https://www.instagram.com/udemedellin/" target="_blank" rel="noopener noreferrer" title="Instagram"><IconIG s={20} /></a>
            <a key="fb" className="social" href="https://www.facebook.com/UniversidaddeMedellin/" target="_blank" rel="noopener noreferrer" title="Facebook"><IconFB s={20} /></a>
            <a key="x" className="social" href="https://twitter.com/udemedellin" target="_blank" rel="noopener noreferrer" title="X (Twitter)"><IconX s={20} /></a>
            <a key="yt" className="social" href="https://www.youtube.com/channel/UCd5xI3f8rKqiqN_-5dJmyZg" target="_blank" rel="noopener noreferrer" title="YouTube"><IconYT s={20} /></a>
            <a key="in" className="social" href="https://www.linkedin.com/school/universidad-de-medellin/" target="_blank" rel="noopener noreferrer" title="LinkedIn"><IconIN s={20} /></a>
          </div>
          <p className="footer-note">Demo conversacional · diseño no afiliado oficialmente. Reemplaza textos y fotos con material institucional.</p>
        </div>
      </div>
      <div className="footer-bottom wrap">
        <span>© 2026 Universidad de Medellín · Campus Vivo</span>
        <span>Hecho con <IconLeaf s={13} /> para la comunidad UdeM</span>
      </div>
    </footer>
  );
}

Object.assign(window, { Stats, Campus, Faq, Footer, Stat });
