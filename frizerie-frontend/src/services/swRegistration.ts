// Service Worker Registration

// Function to register the service worker
export const registerServiceWorker = async (): Promise<ServiceWorkerRegistration | null> => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('Service Worker registered with scope:', registration.scope);

      // Return the registration
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return null;
    }
  } else {
    console.warn('Service Workers are not supported in this browser');
    return null;
  }
};

// Function to check for service worker updates
export const checkForUpdates = async (): Promise<void> => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.update();
      console.log('Service Worker update check completed');
    } catch (error) {
      console.error('Service Worker update check failed:', error);
    }
  }
};

// Function to unregister service workers
export const unregisterServiceWorkers = async (): Promise<boolean> => {
  if ('serviceWorker' in navigator) {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      
      // Unregister each service worker
      await Promise.all(registrations.map(registration => registration.unregister()));
      
      console.log('All Service Workers unregistered');
      return true;
    } catch (error) {
      console.error('Failed to unregister Service Workers:', error);
      return false;
    }
  }
  
  return false;
};

// Function to show a notification when offline
export const showOfflineNotification = (): void => {
  if ('Notification' in window && Notification.permission === 'granted') {
    navigator.serviceWorker.ready.then(registration => {
      registration.showNotification('Frizerie - Offline Mode', {
        body: 'You are currently offline. Your changes will be synchronized when you reconnect.',
        icon: '/logo192.png',
        badge: '/logo192.png',
        tag: 'offline-notification',
        renotify: false
      });
    });
  }
};

// Function to check offline status and show UI indicators
export const checkOfflineStatus = (callback: (isOffline: boolean) => void): () => void => {
  // Initial check
  callback(!navigator.onLine);
  
  // Set up listeners
  const handleStatusChange = () => {
    callback(!navigator.onLine);
  };
  
  // Add event listeners
  window.addEventListener('online', handleStatusChange);
  window.addEventListener('offline', handleStatusChange);
  
  // Return a function to remove the listeners
  return () => {
    window.removeEventListener('online', handleStatusChange);
    window.removeEventListener('offline', handleStatusChange);
  };
};

// Function to request notification permission
export const requestNotificationPermission = async (): Promise<NotificationPermission> => {
  if (!('Notification' in window)) {
    console.warn('This browser does not support notifications');
    return 'denied';
  }
  
  if (Notification.permission === 'granted') {
    return 'granted';
  }
  
  if (Notification.permission !== 'denied') {
    return await Notification.requestPermission();
  }
  
  return 'denied';
};

// Export a default object with all functions
const swRegistration = {
  registerServiceWorker,
  checkForUpdates,
  unregisterServiceWorkers,
  showOfflineNotification,
  checkOfflineStatus,
  requestNotificationPermission
};

export default swRegistration; 