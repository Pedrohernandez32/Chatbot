/* ============================================================
   App — composición + reveal on scroll + ask bridge + advisor integration
   ============================================================ */
const { useEffect, useState } = React;

function useReveal() {
  useEffect(() => {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          // Usamos estilos en línea (no una clase) para que la revelación
          // sobreviva a los re-render de React en componentes con estado.
          e.target.style.opacity = "1";
          e.target.style.transform = "none";
          io.unobserve(e.target);
        }
      });
    }, { threshold: .14, rootMargin: "0px 0px -8% 0px" });
    const run = () => document.querySelectorAll(".reveal").forEach(el => {
      if (el.style.opacity !== "1") io.observe(el);
    });
    run();
    const t = setTimeout(run, 400);
    return () => { io.disconnect(); clearTimeout(t); };
  }, []);
}

function askVivi(text) {
  const el = document.getElementById("asistente");
  if (el) {
    const y = el.getBoundingClientRect().top + window.scrollY - 90;
    window.scrollTo({ top: y, behavior: "smooth" });
  }
  setTimeout(() => window.dispatchEvent(new CustomEvent("vivi-ask", { detail: text })), 420);
}

function App() {
  useReveal();
  const [advisorRequestData, setAdvisorRequestData] = useState(null);

  const handleAdvisorRequest = (data) => {
    console.log('✅ Solicitud de asesor creada:', data);
    setAdvisorRequestData(data);
  };

  return (
    <React.Fragment>
      <Nav />
      <main>
        <Hero />
        <Services onAsk={askVivi} />
        <Stats />
        <Campus />
        <TestimoniosCarousel />
        <Noticias />
        <VidaUdem />
        <Faq onAsk={askVivi} />
        <Login />
      </main>
      <Footer />

      {/* Componente de Asesor en Línea - Integrado */}
      <AdvisorRequestIntegrado
        onRequestCreated={handleAdvisorRequest}
        theme="light"
      />
    </React.Fragment>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
