/* ============================================================
   Icons — simple stroke line icons (Lucide-style)
   ============================================================ */
const I = ({ children, s = 22, sw = 1.7, fill = "none", ...p }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill={fill} stroke="currentColor"
    strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" {...p}>{children}</svg>
);

const IconSpark   = (p) => <I {...p}><path d="M12 3v4M12 17v4M5 12H1M23 12h-4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" /><circle cx="12" cy="12" r="3" /></I>;
const IconSend    = (p) => <I {...p}><path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z" /></I>;
const IconChat    = (p) => <I {...p}><path d="M21 11.5a8.38 8.38 0 0 1-9 8.5 9.4 9.4 0 0 1-4-1L3 20l1.5-4.5A8.38 8.38 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5z" /></I>;
const IconCap     = (p) => <I {...p}><path d="M22 10 12 5 2 10l10 5 10-5z" /><path d="M6 12v5c0 1 2.7 2.5 6 2.5s6-1.5 6-2.5v-5" /></I>;
const IconCoin    = (p) => <I {...p}><circle cx="12" cy="12" r="9" /><path d="M14.8 9.3A3 3 0 0 0 12 8c-1.7 0-3 .9-3 2.2 0 3 6 1.5 6 4.6 0 1.3-1.3 2.2-3 2.2a3 3 0 0 1-2.8-1.3M12 6.5v1.5M12 16v1.5" /></I>;
const IconCampus  = (p) => <I {...p}><path d="M3 21h18M5 21V8l7-4 7 4v13M9 21v-5h6v5M9 11h0M15 11h0" /></I>;
const IconBook    = (p) => <I {...p}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 0 6.5 22H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13z" /></I>;
const IconDoc     = (p) => <I {...p}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M9 13h6M9 17h6" /></I>;
const IconGlobe   = (p) => <I {...p}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z" /></I>;
const IconCalendar= (p) => <I {...p}><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></I>;
const IconMap     = (p) => <I {...p}><path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></I>;
const IconPhone   = (p) => <I {...p}><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z" /></I>;
const IconMail    = (p) => <I {...p}><rect x="2" y="4" width="20" height="16" rx="2" /><path d="m2 7 10 6 10-6" /></I>;
const IconClock   = (p) => <I {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></I>;
const IconArrow   = (p) => <I {...p}><path d="M5 12h14M13 6l6 6-6 6" /></I>;
const IconCheck   = (p) => <I {...p}><path d="M20 6 9 17l-5-5" /></I>;
const IconStar    = (p) => <I {...p}><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17.8 5.9 21.4l1.4-6.8L2.2 9.9l6.9-.8L12 2z" /></I>;
const IconShield  = (p) => <I {...p}><path d="M12 2 4 5v6c0 5 3.4 9 8 11 4.6-2 8-6 8-11V5l-8-3z" /><path d="m9 12 2 2 4-4" /></I>;
const IconUsers   = (p) => <I {...p}><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" /></I>;
const IconFlame   = (p) => <I {...p}><path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-1.2.4-2 1-3-.2 2 1 3 1 3M12 2c-1 3-4 4-4 9a4 4 0 0 0 8 0c0-3-2-6-4-9z" /></I>;
const IconLeaf    = (p) => <I {...p}><path d="M11 20A7 7 0 0 1 4 13c0-6 7-9 16-9 0 9-3 16-9 16z" /><path d="M4 20c2-4 5-7 9-9" /></I>;
const IconTheater = (p) => <I {...p}><path d="M2 10s2-2 5-2 5 2 5 2 2-2 5-2 5 2 5 2M4 10v2a6 6 0 0 0 6 6M20 10v2a6 6 0 0 1-6 6M8 13h0M16 13h0" /></I>;
const IconMic     = (p) => <I {...p}><rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 10a7 7 0 0 0 14 0M12 19v3" /></I>;
const IconMenu    = (p) => <I {...p}><path d="M3 6h18M3 12h18M3 18h18" /></I>;
const IconClose   = (p) => <I {...p}><path d="M18 6 6 18M6 6l12 12" /></I>;
const IconHat     = (p) => IconCap(p);
const IconHelp    = (p) => <I {...p}><circle cx="12" cy="12" r="9" /><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h0" /></I>;
const IconBolt    = (p) => <I {...p}><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z" /></I>;

// Redes sociales
const IconIG      = (p) => <I {...p}><rect x="2" y="2" width="20" height="20" rx="4.18" /><path d="M12 6.5a5.5 5.5 0 1 0 5.5 5.5" /><circle cx="12" cy="12" r="3.5" /><circle cx="17.5" cy="6.5" r="1.5" /></I>;
const IconFB      = (p) => <I {...p}><path d="M18 2h-3a6 6 0 0 0-6 6v4h-4v4h4v8h4v-8h3l1-4h-4V8a2 2 0 0 1 2-2h2z" /></I>;
const IconX       = (p) => <I {...p}><path d="M4 4l16 16M20 4L4 20" /></I>;
const IconYT      = (p) => <I {...p}><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z" /><path d="M10 15l5.5-3.5L10 8v7z" /></I>;
const IconIN      = (p) => <I {...p}><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z" /><circle cx="4" cy="4" r="2" /></I>;

Object.assign(window, {
  IconSpark, IconSend, IconChat, IconCap, IconCoin, IconCampus, IconBook, IconDoc,
  IconGlobe, IconCalendar, IconMap, IconPhone, IconMail, IconClock, IconArrow,
  IconCheck, IconStar, IconShield, IconUsers, IconFlame, IconLeaf, IconTheater,
  IconMic, IconMenu, IconClose, IconHat, IconHelp, IconBolt,
  IconIG, IconFB, IconX, IconYT, IconIN,
});
