/* ============================================================
   Sections 3 — Testimonios, Noticias, Vida Estudiantil
   ============================================================ */
const { useState, useRef, useEffect } = React;

/* ---- Testimonios de estudiantes ---- */
const TESTIMONIOS = [
  {
    autor: "María García",
    carrera: "Ingeniería de Sistemas",
    texto: "Mi experiencia en UdeM cambió mi vida. Los profesores son excepcionales y el campus ofrece todas las herramientas para triunfar.",
    foto: "👩‍🎓",
    año: "2023"
  },
  {
    autor: "Carlos López",
    carrera: "Administración de Empresas",
    texto: "Las becas y el apoyo financiero me permitieron estudiar sin preocupaciones. La universidad invierte en sus estudiantes.",
    foto: "👨‍🎓",
    año: "2022"
  },
  {
    autor: "Sofia Rodríguez",
    carrera: "Psicología",
    texto: "El ambiente estudiantil es increíble. Hice amigos de por vida y aprendí mucho más que en las aulas.",
    foto: "👩‍🎓",
    año: "2024"
  },
  {
    autor: "Juan Martínez",
    carrera: "Derecho",
    texto: "La infraestructura y tecnología del campus son de clase mundial. Vale cada peso invertido en mi educación.",
    foto: "👨‍🎓",
    año: "2023"
  },
];

function TestimoniosCarousel() {
  const [index, setIndex] = useState(0);
  const t = TESTIMONIOS[index];

  const next = () => setIndex((index + 1) % TESTIMONIOS.length);
  const prev = () => setIndex((index - 1 + TESTIMONIOS.length) % TESTIMONIOS.length);

  return (
    <section className="sec testimonios" id="testimonios">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <div className="eyebrow reveal">Lo que dicen nuestros estudiantes</div>
            <h2 className="reveal d1">Historias de éxito</h2>
          </div>
          <p className="sec-head-p reveal d2">Mira cómo UdeM transformó sus vidas académicas y profesionales.</p>
        </div>

        <div className="testimonios-carousel reveal d3">
          <div className="testimonios-content">
            <div className="testimonios-quote">"{t.texto}"</div>
            <div className="testimonios-author">
              <div className="testimonios-avatar">{t.foto}</div>
              <div>
                <div className="testimonios-name">{t.autor}</div>
                <div className="testimonios-career">{t.carrera} · {t.año}</div>
              </div>
            </div>
          </div>

          <div className="testimonios-nav">
            <button className="carousel-btn" onClick={prev}><IconArrow s={18} style={{transform: 'scaleX(-1)'}} /></button>
            <div className="carousel-dots">
              {TESTIMONIOS.map((_, i) => (
                <button
                  key={i}
                  className={"carousel-dot" + (i === index ? " active" : "")}
                  onClick={() => setIndex(i)}
                  aria-label={`Testimonio ${i + 1}`}
                />
              ))}
            </div>
            <button className="carousel-btn" onClick={next}><IconArrow s={18} /></button>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---- Noticias y Eventos ---- */
const NOTICIAS = [
  {
    titulo: "Abierto proceso de inscripción 2026-1",
    fecha: "31 de mayo 2026",
    categoria: "Admisiones",
    icono: IconCap,
    imagen: "🎓"
  },
  {
    titulo: "Nuevas becas de excelencia deportiva",
    fecha: "28 de mayo 2026",
    categoria: "Becas",
    icono: IconCoin,
    imagen: "⚽"
  },
  {
    titulo: "Inauguración de nuevo laboratorio de IA",
    fecha: "25 de mayo 2026",
    categoria: "Infraestructura",
    icono: IconBolt,
    imagen: "🤖"
  },
  {
    titulo: "Egresados UdeM lidera en empleabilidad",
    fecha: "22 de mayo 2026",
    categoria: "Logros",
    icono: IconUsers,
    imagen: "🏆"
  },
];

function Noticias() {
  return (
    <section className="sec noticias" id="noticias">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <div className="eyebrow reveal">Últimas actualizaciones</div>
            <h2 className="reveal d1">Noticias y eventos</h2>
          </div>
          <p className="sec-head-p reveal d2">Mantente informado de lo que ocurre en UdeM.</p>
        </div>

        <div className="noticias-grid">
          {NOTICIAS.map((n, i) => (
            <div key={i} className={"noticia-card reveal d" + ((i % 3) + 1)}>
              <div className="noticia-img">{n.imagen}</div>
              <div className="noticia-badge">{n.categoria}</div>
              <h3 className="noticia-titulo">{n.titulo}</h3>
              <p className="noticia-fecha">{n.fecha}</p>
              <a href="#" className="noticia-link">
                Leer más <IconArrow s={14} />
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---- Vida estudiantil ---- */
const VIDA_UDEM = [
  {
    titulo: "Vida estudiantil vibrante",
    descripcion: "Más de 50 organizaciones estudiantiles te esperan",
    icono: IconTheater,
    color: "blue"
  },
  {
    titulo: "Deporte y recreación",
    descripcion: "Equipos competitivos y actividades para todos",
    icono: IconFlame,
    color: "red"
  },
  {
    titulo: "Oportunidades internacionales",
    descripcion: "Intercambios, pasantías y convenios globales",
    icono: IconGlobe,
    color: "green"
  },
  {
    titulo: "Desarrollo profesional",
    descripcion: "Talleres, seminarios y mentoría continua",
    icono: IconBook,
    color: "gold"
  },
];

function VidaUdem() {
  return (
    <section className="sec vida-udem" id="vida-udem">
      <div className="wrap">
        <div className="sec-head">
          <div>
            <div className="eyebrow reveal">Más que aulas</div>
            <h2 className="reveal d1">La vida en UdeM</h2>
          </div>
          <p className="sec-head-p reveal d2">Una experiencia completa de crecimiento personal y profesional.</p>
        </div>

        <div className="vida-grid">
          {VIDA_UDEM.map((item, i) => (
            <div key={i} className={"vida-card reveal d" + ((i % 2) + 1)}>
              <div className="vida-icon">
                <item.icono s={32} />
              </div>
              <h3>{item.titulo}</h3>
              <p>{item.descripcion}</p>
              <button className="btn btn-outline">Saber más</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { TestimoniosCarousel, Noticias, VidaUdem });
