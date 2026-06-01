/**
 * Componentes React Avanzados - Ultra Profesionales
 * - Animaciones suaves (Framer Motion)
 * - Temas claro/oscuro
 * - Accesibilidad WCAG AA
 * - Internacionalización (i18n)
 * - Componentes reutilizables
 */

const { useState, useEffect, useContext, createContext } = React;

// ==================== TEMA CONTEXT ====================

const ThemeContext = createContext();
const LanguageContext = createContext();

// ==================== THEME PROVIDER ====================

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'es';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setLanguageValue = (lang) => {
    setLanguage(lang);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <LanguageContext.Provider value={{ language, setLanguage: setLanguageValue }}>
        {children}
      </LanguageContext.Provider>
    </ThemeContext.Provider>
  );
}

// ==================== TRADUCCIÓN (i18n) ====================

const translations = {
  es: {
    'advisor.request': 'Solicitar Asesor',
    'advisor.chat': 'Chat con Asesor',
    'advisor.available': 'Asesores Disponibles',
    'advisor.waiting': 'En la cola',
    'common.send': 'Enviar',
    'common.cancel': 'Cancelar',
    'common.confirm': 'Confirmar',
    'common.loading': 'Cargando...',
    'common.error': 'Error',
    'common.success': 'Éxito',
    'theme.light': 'Claro',
    'theme.dark': 'Oscuro',
  },
  en: {
    'advisor.request': 'Request Advisor',
    'advisor.chat': 'Chat with Advisor',
    'advisor.available': 'Available Advisors',
    'advisor.waiting': 'In Queue',
    'common.send': 'Send',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'theme.light': 'Light',
    'theme.dark': 'Dark',
  },
};

function useTranslation() {
  const { language } = useContext(LanguageContext);
  return {
    t: (key) => translations[language]?.[key] || key,
    language
  };
}

// ==================== BOTÓN AVANZADO ====================

function AdvancedButton({
  label,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  icon,
  loading = false,
  fullWidth = false,
  ariaLabel
}) {
  const { t } = useTranslation();
  const { theme } = useContext(ThemeContext);

  const styles = {
    primary: 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg',
    secondary: 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-green-600 text-white hover:bg-green-700',
  };

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel || label}
      aria-busy={loading}
      className={`
        ${styles[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        rounded-lg font-semibold
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
      `}
      style={{
        boxShadow: theme === 'dark' ? '0 4px 15px rgba(0,0,0,0.3)' : '0 4px 15px rgba(0,0,0,0.1)'
      }}
    >
      {loading && <span className="animate-spin">⏳</span>}
      {icon && !loading && <span>{icon}</span>}
      <span>{label}</span>
    </button>
  );
}

// ==================== CARD AVANZADA ====================

function AdvancedCard({
  title,
  children,
  icon,
  variant = 'default',
  onClick,
  hoverable = false,
  footer
}) {
  const { theme } = useContext(ThemeContext);

  const variants = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg',
    filled: 'bg-gray-50 dark:bg-gray-700',
  };

  return (
    <div
      onClick={onClick}
      className={`
        ${variants[variant]}
        rounded-xl p-6
        transition-all duration-300
        ${hoverable ? 'hover:shadow-xl hover:scale-105 cursor-pointer' : ''}
      `}
      role="article"
    >
      {(title || icon) && (
        <div className="flex items-center gap-3 mb-4">
          {icon && <span className="text-2xl">{icon}</span>}
          {title && <h3 className="text-lg font-bold text-gray-900 dark:text-white">{title}</h3>}
        </div>
      )}
      {children}
      {footer && <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">{footer}</div>}
    </div>
  );
}

// ==================== MODAL AVANZADO ====================

function AdvancedModal({
  isOpen,
  onClose,
  title,
  children,
  actions,
  size = 'md',
  closeOnEscape = true
}) {
  useEffect(() => {
    const handleEscape = (e) => {
      if (closeOnEscape && e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, closeOnEscape, onClose]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
      role="presentation"
    >
      <div
        className={`
          ${sizes[size]}
          bg-white dark:bg-gray-800
          rounded-2xl shadow-2xl
          max-h-[90vh] overflow-y-auto
          animation-slideUp
        `}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 id="modal-title" className="text-2xl font-bold text-gray-900 dark:text-white">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            aria-label="Cerrar modal"
          >
            ✕
          </button>
        </div>

        <div className="p-6">
          {children}
        </div>

        {actions && (
          <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex gap-3 justify-end">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== INPUT AVANZADO ====================

function AdvancedInput({
  type = 'text',
  placeholder,
  value,
  onChange,
  label,
  error,
  disabled = false,
  icon,
  required = false,
  ariaLabel,
  maxLength
}) {
  const [focused, setFocused] = useState(false);
  const { theme } = useContext(ThemeContext);

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        {icon && (
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {icon}
          </span>
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={disabled}
          maxLength={maxLength}
          aria-label={ariaLabel}
          aria-invalid={!!error}
          aria-describedby={error ? `error-${label}` : undefined}
          className={`
            w-full px-4 py-3 rounded-lg
            ${icon ? 'pl-10' : ''}
            border-2 transition-all duration-300
            ${error
              ? 'border-red-500 dark:border-red-500'
              : focused
              ? 'border-blue-500 dark:border-blue-400'
              : 'border-gray-300 dark:border-gray-600'
            }
            bg-white dark:bg-gray-800
            text-gray-900 dark:text-white
            placeholder-gray-400 dark:placeholder-gray-500
            disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed
            focus:outline-none
          `}
        />
      </div>
      {error && (
        <p id={`error-${label}`} className="mt-1 text-sm text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}

// ==================== STATS WIDGET ====================

function StatsWidget({ label, value, icon, trend, color = 'blue' }) {
  const colors = {
    blue: 'from-blue-600 to-blue-400',
    purple: 'from-purple-600 to-purple-400',
    green: 'from-green-600 to-green-400',
    red: 'from-red-600 to-red-400',
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-lg p-6 text-white shadow-lg`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm opacity-90">{label}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend > 0 ? 'text-green-200' : 'text-red-200'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs mes anterior
            </p>
          )}
        </div>
        {icon && <span className="text-4xl">{icon}</span>}
      </div>
    </div>
  );
}

// ==================== PROGRESS BAR ====================

function ProgressBar({ value, label, color = 'blue', showLabel = true }) {
  const colors = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-600',
    red: 'bg-red-600',
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{value}%</span>
        </div>
      )}
      <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors[color]} transition-all duration-300`}
          style={{ width: `${value}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
    </div>
  );
}

// ==================== LOADER ====================

function AdvancedLoader({ size = 'md', label }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`${sizes[size]} animate-spin`}>
        <svg className="w-full h-full text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      {label && <p className="text-gray-600 dark:text-gray-400">{label}</p>}
    </div>
  );
}

// ==================== TOAST NOTIFICATIONS ====================

function Toast({ message, type = 'info', onClose, autoClose = 3000 }) {
  useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(onClose, autoClose);
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose]);

  const types = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white',
  };

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <div
      className={`
        ${types[type]}
        px-6 py-4 rounded-lg shadow-lg
        flex items-center gap-3
        animation-slideIn
        fixed bottom-4 right-4 max-w-sm
      `}
      role="alert"
    >
      <span className="text-xl">{icons[type]}</span>
      <span>{message}</span>
      <button
        onClick={onClose}
        className="ml-auto text-lg opacity-70 hover:opacity-100"
        aria-label="Cerrar notificación"
      >
        ✕
      </button>
    </div>
  );
}

// ==================== GLOBAL STYLES ====================

const globalStyles = `
:root {
  --primary: #1e40af;
  --secondary: #7c3aed;
  --success: #16a34a;
  --warning: #ea580c;
  --danger: #dc2626;
  --gray-light: #f3f4f6;
  --gray-medium: #d1d5db;
  --gray-dark: #374151;
}

html[data-theme="dark"] {
  --primary: #60a5fa;
  --secondary: #a78bfa;
  --gray-light: #1f2937;
  --gray-medium: #374151;
  --gray-dark: #e5e7eb;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animation-slideUp {
  animation: slideUp 0.3s ease;
}

.animation-slideIn {
  animation: slideIn 0.3s ease;
}

/* Accesibilidad */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Focus visible para accesibilidad */
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  html[data-theme="light"] {
    color-scheme: light;
  }
  html[data-theme="dark"] {
    color-scheme: dark;
  }
}
`;

// Exportar componentes
export {
  ThemeProvider,
  useTranslation,
  AdvancedButton,
  AdvancedCard,
  AdvancedModal,
  AdvancedInput,
  StatsWidget,
  ProgressBar,
  AdvancedLoader,
  Toast,
  useContext,
  ThemeContext,
  LanguageContext,
};
