/**
 * PWA Manager - Maneja instalación, notificaciones y sincronización
 */

class PWAManager {
  constructor() {
    this.serviceWorkerReady = false;
    this.notificationsSupported = false;
    this.syncSupported = false;
  }

  /**
   * Inicializar PWA
   */
  async init() {
    console.log('🚀 Initializing PWA...');

    // 1. Registrar Service Worker
    await this.registerServiceWorker();

    // 2. Pedir permisos de notificación
    await this.requestNotificationPermission();

    // 3. Detectar soporte para Background Sync
    this.syncSupported = 'sync' in ServiceWorkerRegistration.prototype;
    console.log(`📡 Background Sync supported: ${this.syncSupported}`);

    // 4. Escuchar cambios de conexión
    this.setupConnectivityListener();

    // 5. Mostrar prompt de instalación
    this.setupInstallPrompt();

    console.log('✅ PWA initialized');
  }

  /**
   * Registrar Service Worker
   */
  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      console.warn('⚠️ Service Workers not supported');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('✅ Service Worker registered:', registration);
      this.serviceWorkerReady = true;

      // Escuchar updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('🔄 New Service Worker available');
            this.notifyUpdate();
          }
        });
      });

      return registration;
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  }

  /**
   * Pedir permisos de notificación
   */
  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      console.warn('⚠️ Notifications not supported');
      return;
    }

    if (Notification.permission === 'granted') {
      this.notificationsSupported = true;
      console.log('✅ Notifications already granted');
      return;
    }

    if (Notification.permission !== 'denied') {
      try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          this.notificationsSupported = true;
          console.log('✅ Notifications permission granted');
          this.sendTestNotification();
        }
      } catch (error) {
        console.error('❌ Error requesting notification permission:', error);
      }
    }
  }

  /**
   * Enviar notificación de prueba
   */
  sendTestNotification() {
    if (!this.notificationsSupported) return;

    const notification = new Notification('🎉 UdeMedellin App Instalada', {
      body: '¡Bienvenido! Ahora recibirás notificaciones en tiempo real.',
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      tag: 'welcome'
    });

    notification.addEventListener('click', () => {
      window.focus();
      notification.close();
    });
  }

  /**
   * Escuchar cambios de conectividad
   */
  setupConnectivityListener() {
    window.addEventListener('online', () => {
      console.log('🟢 Online');
      this.showNotification('Conectado', '✅ Volvimos en línea');
      this.triggerSync();
    });

    window.addEventListener('offline', () => {
      console.log('🔴 Offline');
      this.showNotification('Desconectado', '⚠️ Trabajando sin conexión');
    });
  }

  /**
   * Mostrar prompt de instalación
   */
  setupInstallPrompt() {
    let deferredPrompt;

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;

      // Mostrar botón de instalación
      const installBtn = document.getElementById('install-app-btn');
      if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.addEventListener('click', async () => {
          deferredPrompt.prompt();
          const { outcome } = await deferredPrompt.userChoice;
          console.log(`App installation ${outcome}`);
          deferredPrompt = null;
          installBtn.style.display = 'none';
        });
      }
    });

    window.addEventListener('appinstalled', () => {
      console.log('🎉 App installed');
      this.showNotification('¡Instalado!', '🎉 App instalada correctamente');
    });
  }

  /**
   * Mostrar notificación
   */
  async showNotification(title, body, options = {}) {
    if (!this.notificationsSupported) return;

    const defaultOptions = {
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      ...options
    };

    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'SHOW_NOTIFICATION',
        title,
        options: defaultOptions
      });
    } else {
      new Notification(title, { body, ...defaultOptions });
    }
  }

  /**
   * Disparar Background Sync
   */
  async triggerSync(tag = 'sync-messages') {
    if (!this.syncSupported || !navigator.serviceWorker.ready) return;

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register(tag);
      console.log(`📡 Sync queued: ${tag}`);
    } catch (error) {
      console.error('❌ Sync failed:', error);
    }
  }

  /**
   * Notificar actualización disponible
   */
  notifyUpdate() {
    if (!this.notificationsSupported) {
      console.log('📢 New app version available');
      return;
    }

    const notification = new Notification('🔄 Actualización Disponible', {
      body: 'Recarga la página para obtener las últimas mejoras',
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      tag: 'update',
      requireInteraction: true,
      actions: [
        { action: 'reload', title: '🔄 Recargar' },
        { action: 'dismiss', title: '❌ Después' }
      ]
    });

    notification.addEventListener('click', (event) => {
      if (event.action === 'reload') {
        window.location.reload();
      }
      notification.close();
    });
  }

  /**
   * Subscribirse a push notifications
   */
  async subscribeToPushNotifications(publicKey) {
    if (!this.serviceWorkerReady) {
      console.warn('⚠️ Service Worker not ready');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey)
      });

      console.log('✅ Subscribed to push notifications');

      // Enviar subscription al servidor
      await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
      });

      return subscription;
    } catch (error) {
      console.error('❌ Push subscription failed:', error);
    }
  }

  /**
   * Chequear estado de la app
   */
  getStatus() {
    return {
      serviceWorkerReady: this.serviceWorkerReady,
      notificationsSupported: this.notificationsSupported,
      notificationsEnabled: Notification.permission === 'granted',
      online: navigator.onLine,
      syncSupported: this.syncSupported,
      userAgent: navigator.userAgent,
      storage: this.getStorageStatus()
    };
  }

  /**
   * Estado de storage
   */
  getStorageStatus() {
    if (!navigator.storage) return { available: false };

    return {
      available: true,
      persistent: navigator.storage.persisted?.(),
      estimate: navigator.storage.estimate?.()
    };
  }

  /**
   * Hacer storage persistente
   */
  async makePersistent() {
    if (!navigator.storage?.persist) {
      console.warn('⚠️ Persistent storage not supported');
      return false;
    }

    try {
      const persistent = await navigator.storage.persist();
      console.log(`💾 Persistent storage: ${persistent}`);
      return persistent;
    } catch (error) {
      console.error('❌ Failed to make storage persistent:', error);
      return false;
    }
  }

  /**
   * Obtener información de device
   */
  getDeviceInfo() {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      onLine: navigator.onLine,
      deviceMemory: navigator.deviceMemory,
      cores: navigator.hardwareConcurrency,
      connection: navigator.connection?.effectiveType,
      saveData: navigator.connection?.saveData
    };
  }
}

/**
 * Converter para VAPID key
 */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

// Inicializar automáticamente
const pwaManager = new PWAManager();
document.addEventListener('DOMContentLoaded', () => {
  pwaManager.init();
});

// Exportar para uso global
window.PWAManager = pwaManager;
