/* ============================================================
   Login / Acceso — diferenciado Usuario vs Administrador
   ============================================================ */
const { useState } = React;

/* ============================================================
   CONEXIÓN CON TU BACKEND - Universidad de Medellín
   ============================================================ */
const AUTH_API = "http://localhost:9999/api";  // Backend Flask en puerto 9999
const DEMO_MODE = true;                         // DEMO MODE ACTIVO - Conectado al servidor real

async function authenticate({ role, id, pass, code }) {
  const payload = {
    email: id,
    password: pass,
  };

  // Si es admin, agregar la clave de admin
  if (role === "admin") {
    payload.isAdmin = true;
    payload.adminKey = code;
  }

  const res = await fetch(`${AUTH_API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.message || "Usuario o contraseña incorrectos.");
  }

  const data = await res.json();
  return {
    name: data.user?.username || id.split("@")[0],
    role: data.user?.is_admin ? "admin" : "user",
    token: data.token,
  };
}

const USER_ACTIONS = [
  { Ic: IconBook, t: "Mis cursos", d: "Materias y contenidos" },
  { Ic: IconStar, t: "Notas", d: "Calificaciones del semestre" },
  { Ic: IconCalendar, t: "Horario", d: "Tu agenda de clases" },
  { Ic: IconCoin, t: "Pagos y matrícula", d: "Estado financiero" },
];
const ADMIN_ACTIONS = [
  { Ic: IconUsers, t: "Gestión de usuarios", d: "Altas, bajas y roles" },
  { Ic: IconDoc, t: "Reportes", d: "Métricas del asistente" },
  { Ic: IconCampus, t: "Contenido del sitio", d: "Editar secciones y fotos" },
  { Ic: IconShield, t: "Seguridad", d: "Permisos y auditoría" },
];

function Dashboard({ session, logout }) {
  const admin = session.role === "admin";
  const actions = admin ? ADMIN_ACTIONS : USER_ACTIONS;
  return (
    <div className={"dash" + (admin ? " dash-admin" : "")}>
      <div className="dash-top">
        <div className="dash-ava">{admin ? <IconShield s={24} /> : <IconUsers s={24} />}</div>
        <div className="dash-id">
          <span className="dash-role">{admin ? "Administrador" : "Estudiante"}</span>
          <h3>Hola, {session.name} 👋</h3>
        </div>
        <span className="dash-badge">{admin ? "Panel admin" : "Sesión activa"}</span>
      </div>
      <p className="dash-sub">
        {admin
          ? "Tienes acceso completo a la gestión del portal y del asistente Vivi."
          : "Estos son tus accesos rápidos para hoy. ¡Que tengas un buen día!"}
      </p>
      <div className="dash-grid">
        {actions.map((a, i) => (
          <button key={i} className="dash-act">
            <span className="dash-act-ic"><a.Ic s={20} /></span>
            <span className="dash-act-tx"><strong>{a.t}</strong><small>{a.d}</small></span>
            <IconArrow s={16} />
          </button>
        ))}
      </div>
      <button className="dash-logout" onClick={logout}>Cerrar sesión</button>
    </div>
  );
}

async function register({ email, username, password }) {
  const res = await fetch(`${AUTH_API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, username, password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || data.message || "No se pudo crear la cuenta.");
  }

  return res.json();
}

function Login() {
  const [role, setRole] = useState("user");
  const [form, setForm] = useState({ id: "", pass: "", code: "", username: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(null);
  const [isRegister, setIsRegister] = useState(false);
  const admin = role === "admin";

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const switchRole = (r) => { setRole(r); setError(""); };

  const submit = async (e) => {
    e.preventDefault();
    if (loading) return;

    // Validaciones
    if (!form.id.trim() || !form.pass.trim()) {
      setError("Ingresa tu email y contraseña para continuar.");
      return;
    }
    if (isRegister && !form.username.trim()) {
      setError("Ingresa tu nombre de usuario.");
      return;
    }
    if (admin && !form.code.trim()) {
      setError("El acceso administrativo requiere el código de seguridad.");
      return;
    }

    setError("");
    setLoading(true);
    try {
      let data;
      if (isRegister) {
        // Registro
        await register({ email: form.id, username: form.username, password: form.pass });
        // Después de registrar, hacer login automático
        data = await authenticate({ role: "user", id: form.id, pass: form.pass });
        setSession({ role: "user", name: form.username });
      } else {
        // Login
        data = await authenticate({ role, id: form.id, pass: form.pass, code: form.code });
        if (data.token) localStorage.setItem("udem_token", data.token);
        setSession({ role: data.role, name: data.name });
      }
    } catch (err) {
      setError(err.message || "No se pudo conectar con el servidor. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("udem_token");
    setSession(null);
    setForm({ id: "", pass: "", code: "", username: "" });
    setError("");
    setIsRegister(false);
  };

  return (
    <section className="sec access" id="acceso">
      <div className="wrap access-in">
        <aside className="access-aside reveal">
          <div className="eyebrow">Tu portal UdeMedellín</div>
          <h2>Un solo acceso,<br />toda tu vida<br />universitaria.</h2>
          <ul className="access-bullets">
            <li><span className="ab-ic"><IconCheck s={15} /></span> Consulta notas, horarios y pagos</li>
            <li><span className="ab-ic"><IconCheck s={15} /></span> Habla con Vivi con tu información</li>
            <li><span className="ab-ic"><IconShield s={15} /></span> Acceso seguro y diferenciado por rol</li>
          </ul>
          <div className="access-img"><img src="assets/campus-aereo.jpg" alt="Campus UdeMedellín" loading="lazy" /></div>
        </aside>

        <div className={"access-card reveal d2" + (admin ? " is-admin" : "")}>
          {!session ? (
            <React.Fragment>
              {!isRegister && (
                <div className="role-toggle" role="tablist">
                  <button className={!admin ? "on" : ""} onClick={() => switchRole("user")}><IconUsers s={17} /> Usuario</button>
                  <button className={admin ? "on" : ""} onClick={() => switchRole("admin")}><IconShield s={17} /> Administrador</button>
                  <span className={"role-pill" + (admin ? " right" : "")} />
                </div>
              )}

              <div className="access-head">
                <h3>{isRegister ? "Crear cuenta" : admin ? "Acceso administrativo" : "Iniciar sesión"}</h3>
                <p>{isRegister ? "Regístrate para acceder al portal estudiantil." : admin ? "Panel restringido para personal autorizado." : "Ingresa con tu cuenta de estudiante o egresado."}</p>
              </div>

              <form onSubmit={submit} className="access-form">
                {isRegister && (
                  <label className="field">
                    <span>Nombre de usuario</span>
                    <input type="text" value={form.username} onChange={set("username")} placeholder="Tu nombre completo" autoComplete="off" />
                  </label>
                )}
                <label className="field">
                  <span>{isRegister ? "Correo institucional" : admin ? "Usuario corporativo" : "Correo institucional"}</span>
                  <input type="text" value={form.id} onChange={set("id")} placeholder={admin ? "admin.nombre" : "tu.correo@udemedellin.edu.co"} autoComplete="username" />
                </label>
                <label className="field">
                  <span>Contraseña</span>
                  <input type="password" value={form.pass} onChange={set("pass")} placeholder="••••••••" autoComplete={isRegister ? "new-password" : "current-password"} />
                </label>
                {admin && (
                  <label className="field">
                    <span>Código de seguridad</span>
                    <input type="text" value={form.code} onChange={set("code")} placeholder="Ej. 6 dígitos" inputMode="numeric" />
                  </label>
                )}

                {error && <div className="access-error"><IconHelp s={15} /> {error}</div>}

                {!isRegister && (
                  <div className="access-row">
                    <label className="chk"><input type="checkbox" /> <span>Recordarme</span></label>
                    <a href="#acceso" onClick={(e) => e.preventDefault()}>¿Olvidaste tu contraseña?</a>
                  </div>
                )}

                <button type="submit" disabled={loading} className={"btn access-submit " + (admin && !isRegister ? "btn-admin" : "btn-primary")}>
                  {loading
                    ? <React.Fragment><span className="spin" /> Procesando…</React.Fragment>
                    : <React.Fragment>
                        {isRegister ? <IconArrow s={18} /> : admin ? <IconShield s={18} /> : <IconArrow s={18} />}
                        {" "}
                        {isRegister ? "Crear cuenta" : admin ? "Entrar al panel" : "Ingresar"}
                      </React.Fragment>}
                </button>

                {isRegister ? (
                  <p className="access-foot">¿Ya tienes cuenta? <a href="#acceso" onClick={(e) => { e.preventDefault(); setIsRegister(false); setError(""); }}>Inicia sesión aquí</a></p>
                ) : admin ? (
                  <p className="access-foot secure"><IconShield s={14} /> Conexión segura · acceso monitoreado</p>
                ) : (
                  <p className="access-foot">¿Aún no tienes cuenta? <a href="#acceso" onClick={(e) => { e.preventDefault(); setIsRegister(true); setError(""); }}>Regístrate aquí</a></p>
                )}
              </form>
            </React.Fragment>
          ) : session.role === "admin" ? (
            <AdminPanel user={session} logout={logout} />
          ) : (
            <Dashboard session={session} logout={logout} />
          )}
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { Login });
