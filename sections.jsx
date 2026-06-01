/* ============================================================
   Sections — Nav, Hero, Quick links
   ============================================================ */
const { useState, useEffect, useRef, useCallback } = React;


/* Brand — logo oficial provisto por la universidad */
function Brand({ light = false }) {
  return (
    <a href="#top" className={"brand" + (light ? " brand-light" : "")}>
      <img className="brand-logo" src={light ? "assets/logo-blanco-trim.png" : "assets/logo-color-trim.png"} alt="Universidad de Medellín" />
      <span className="brand-div" aria-hidden="true"></span>
      <span className="brand-sub">Asistente<br />Virtual</span>
    </a>
  );
}

function Nav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const f = () => setScrolled(window.scrollY > 28);
    window.addEventListener("scroll", f); f();
    return () => window.removeEventListener("scroll", f);
  }, []);
  const links = [
    ["Asistente", "#asistente"],
    ["Servicios", "#servicios"],
    ["Campus", "#campus"],
    ["Preguntas", "#faq"],
    ["Acceso", "#acceso"],
  ];
  return (
    <header className={"nav" + (scrolled ? " nav-on" : "")}>
      <div className="wrap nav-in">
        <Brand />
        <nav className="nav-links">
          {links.map(([t, h]) => <a key={h} href={h}>{t}</a>)}
        </nav>
        <div className="nav-cta">
          <a href="#asistente" className="btn btn-primary"><IconChat s={17} /> Abrir chat</a>
        </div>
        <button className="nav-burger" onClick={() => setOpen(o => !o)} aria-label="Menú">
          {open ? <IconClose /> : <IconMenu />}
        </button>
      </div>
      {open && (
        <div className="nav-mobile">
          {links.map(([t, h]) => <a key={h} href={h} onClick={() => setOpen(false)}>{t}</a>)}
          <a href="#asistente" className="btn btn-primary" onClick={() => setOpen(false)}><IconChat s={17} /> Abrir chat</a>
        </div>
      )}
    </header>
  );
}

/* ---- Hero ---- */
function Hero() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const move = (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      el.style.setProperty("--mx", x.toFixed(3));
      el.style.setProperty("--my", y.toFixed(3));
    };
    el.addEventListener("mousemove", move);
    return () => el.removeEventListener("mousemove", move);
  }, []);

  const chips = [
    { Ic: IconCap, t: "Admisiones", d: 1.4, x: "2%", y: "13%" },
    { Ic: IconGlobe, t: "Idiomas", d: 1.9, x: "30%", y: "8%" },
    { Ic: IconLeaf, t: "Campus Vivo", d: 2.4, x: "1%", y: "90%" },
    { Ic: IconCoin, t: "Becas", d: 1.7, x: "24%", y: "95%" },
    { Ic: IconBook, t: "Biblioteca", d: 2.1, x: "45%", y: "92%" },
  ];

  return (
    <section className="hero" id="top" ref={ref}>
      <div className="hero-bg">
        <span className="blob blob-1" /><span className="blob blob-2" /><span className="blob blob-3" />
        <div className="hero-grid-lines" />
      </div>

      {chips.map((c, i) => (
        <div key={i} className="float-chip-wrap" style={{
          left: c.x, top: c.y,
          transform: `translate(calc(var(--mx,0)*${c.d * -38}px), calc(var(--my,0)*${c.d * -38}px))`,
        }}>
          <div className="float-chip" style={{ animationDelay: `${i * .6}s` }}>
            <c.Ic s={17} /> <span>{c.t}</span>
          </div>
        </div>
      ))}

      <div className="wrap hero-in">
        <div className="hero-copy">
          <div className="eyebrow reveal in">Universidad de Medellín · desde 1950</div>
          <h1 className="reveal in d1">
            Tu <span className="hl">Campus Vivo</span><br />resuelve en segundos.
          </h1>
          <p className="hero-sub reveal in d2">
            Vivi, el asistente virtual de la UdeMedellín, te orienta sobre admisiones,
            programas, becas, trámites y la vida en el campus. Pregunta lo que quieras,
            cuando quieras.
          </p>
          <div className="hero-actions reveal in d3">
            <a href="#asistente" className="btn btn-primary"><IconSpark s={18} /> Hablar con Vivi</a>
            <a href="#servicios" className="btn btn-light"><IconBolt s={17} /> Ver servicios</a>
          </div>
          <div className="hero-trust reveal in d4">
            <span><IconShield s={16} /> Acreditada en Alta Calidad</span>
            <span><IconUsers s={16} /> +74.000 egresados</span>
          </div>
        </div>

        <div className="hero-chat reveal in d2" id="asistente">
          <div className="hero-chat-glow" />
          <Chat />
        </div>
      </div>

      <div className="hero-marquee">
        <div className="marquee-track">
          {[...Array(2)].map((_, k) => (
            <React.Fragment key={k}>
              {["27 Pregrados","36 Especializaciones","21 Maestrías","6 Doctorados","7 Facultades","Sede Medellín & Bogotá","Centro de Idiomas","Teatro Gabriel Obregón Botero"].map((t, i) => (
                <span key={k + "-" + i} className="mq-item"><IconStar s={13} /> {t}</span>
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---- Quick links / Servicios ---- */
const SERVICES = [
  { Ic: IconCap, t: "Admisiones e inscripción", d: "Pregrado, posgrado, reingreso y transferencia. Te guiamos paso a paso según tu perfil.", tag: "Aspirantes", c: "blue", q: "¿Cómo me inscribo a un pregrado en la UdeMedellín?" },
  { Ic: IconCoin, t: "Becas y financiación", d: "Apoyos, descuentos y opciones de crédito para que estudies sin freno.", tag: "Apoyo", c: "green", q: "¿Qué becas y opciones de financiación ofrecen?" },
  { Ic: IconBook, t: "Programas académicos", d: "27 pregrados y más de 60 posgrados en 7 facultades.", tag: "Oferta", c: "blue", q: "¿Qué programas de pregrado ofrecen?" },
  { Ic: IconDoc, t: "Trámites y certificados", d: "Certificados, paz y salvo, horarios y solicitudes en línea.", tag: "Estudiantes", c: "gold", q: "¿Cómo solicito un certificado de estudios?" },
  { Ic: IconGlobe, t: "Centro de Idiomas", d: "Cursos de inglés y más para potenciar tu perfil global.", tag: "Bilingüismo", c: "green", q: "Cuéntame sobre el Centro de Idiomas" },
  { Ic: IconMap, t: "Vida en el campus", d: "Bienestar, deporte, cultura y rutas del Campus Vivo.", tag: "Bienestar", c: "blue", q: "¿Qué puedo hacer en el campus?" },
];

function Services({ onAsk }) {
  return (
    <section className="sec services" id="servicios">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <div className="eyebrow reveal">Todo en un solo lugar</div>
            <h2 className="reveal d1">¿Con qué te ayuda Vivi?</h2>
          </div>
          <p className="sec-head-p reveal d2">Toca cualquier tarjeta y el asistente abrirá la conversación por ti.</p>
        </div>
        <div className="serv-grid">
          {SERVICES.map((s, i) => (
            <button key={i} className={"serv-card reveal d" + ((i % 3) + 1) + " c-" + s.c} onClick={() => onAsk(s.q)}>
              <div className="serv-ic"><s.Ic s={24} /></div>
              <span className="serv-tag">{s.tag}</span>
              <h3>{s.t}</h3>
              <p>{s.d}</p>
              <span className="serv-go">Preguntar <IconArrow s={16} /></span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { Nav, Hero, Services, Brand });
