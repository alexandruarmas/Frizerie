// IndexedDB wrapper for offline storage
const DB_NAME = 'frizerie-offline-db';
const DB_VERSION = 1;

// Add the SyncManager interface for TypeScript
interface SyncManager {
  register(tag: string): Promise<void>;
}

// Extend ServiceWorkerRegistration interface with sync property
interface ExtendedServiceWorkerRegistration extends ServiceWorkerRegistration {
  sync: SyncManager;
}

interface DBSchema {
  [key: string]: {
    keyPath: string;
    indexes?: { name: string; keyPath: string; options?: IDBIndexParameters }[];
  };
}

// Define database schema
const dbSchema: DBSchema = {
  'pending-bookings': {
    keyPath: 'id',
    indexes: [
      { name: 'createdAt', keyPath: 'createdAt' }
    ]
  },
  'pending-profile-updates': {
    keyPath: 'id'
  },
  'cached-bookings': {
    keyPath: 'id',
    indexes: [
      { name: 'userId', keyPath: 'userId' },
      { name: 'date', keyPath: 'date' }
    ]
  },
  'cached-user': {
    keyPath: 'id'
  }
};

// Open database connection
const openDB = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = () => {
      console.error('Error opening IndexedDB');
      reject(new Error('Could not open IndexedDB'));
    };
    
    request.onsuccess = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      resolve(db);
    };
    
    // Create object stores on database initialization/upgrade
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      
      // Create object stores based on schema
      Object.entries(dbSchema).forEach(([storeName, storeSchema]) => {
        if (!db.objectStoreNames.contains(storeName)) {
          const objectStore = db.createObjectStore(storeName, { keyPath: storeSchema.keyPath });
          
          // Create indexes if defined
          storeSchema.indexes?.forEach(index => {
            objectStore.createIndex(index.name, index.keyPath, index.options);
          });
        }
      });
    };
  });
};

// Generic add item to store
const addItem = async <T>(storeName: string, item: T): Promise<T> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.add(item);
    
    request.onsuccess = () => {
      resolve(item);
    };
    
    request.onerror = () => {
      reject(new Error(`Error adding item to ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Generic update item in store
const updateItem = async <T>(storeName: string, item: T): Promise<T> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.put(item);
    
    request.onsuccess = () => {
      resolve(item);
    };
    
    request.onerror = () => {
      reject(new Error(`Error updating item in ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Generic get item by id
const getItem = async <T>(storeName: string, id: string | number): Promise<T | null> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.get(id);
    
    request.onsuccess = () => {
      resolve(request.result || null);
    };
    
    request.onerror = () => {
      reject(new Error(`Error getting item from ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Generic get all items
const getAllItems = async <T>(storeName: string): Promise<T[]> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    
    request.onsuccess = () => {
      resolve(request.result || []);
    };
    
    request.onerror = () => {
      reject(new Error(`Error getting all items from ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Generic delete item
const deleteItem = async (storeName: string, id: string | number): Promise<void> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);
    
    request.onsuccess = () => {
      resolve();
    };
    
    request.onerror = () => {
      reject(new Error(`Error deleting item from ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Clear all items from a store
const clearStore = async (storeName: string): Promise<void> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.clear();
    
    request.onsuccess = () => {
      resolve();
    };
    
    request.onerror = () => {
      reject(new Error(`Error clearing ${storeName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Query by index
const queryByIndex = async <T>(
  storeName: string, 
  indexName: string, 
  value: string | number
): Promise<T[]> => {
  const db = await openDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const index = store.index(indexName);
    const request = index.getAll(value);
    
    request.onsuccess = () => {
      resolve(request.result || []);
    };
    
    request.onerror = () => {
      reject(new Error(`Error querying ${storeName} by ${indexName}`));
    };
    
    transaction.oncomplete = () => {
      db.close();
    };
  });
};

// Schedule background sync
const scheduleSync = (syncTag: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      navigator.serviceWorker.ready
        .then(registration => {
          // Cast to extended interface with sync property
          return (registration as ExtendedServiceWorkerRegistration).sync.register(syncTag);
        })
        .then(() => {
          console.log(`Background sync scheduled: ${syncTag}`);
          resolve();
        })
        .catch(error => {
          console.error(`Error scheduling background sync: ${error}`);
          reject(error);
        });
    } else {
      const error = new Error('Background sync not supported');
      console.error(error);
      reject(error);
    }
  });
};

// Check if online
const isOnline = (): boolean => {
  return navigator.onLine;
};

// Add event listeners for online/offline status
const setupConnectivityListeners = (
  onlineCallback: () => void,
  offlineCallback: () => void
): void => {
  window.addEventListener('online', onlineCallback);
  window.addEventListener('offline', offlineCallback);
};

// Remove event listeners
const removeConnectivityListeners = (
  onlineCallback: () => void,
  offlineCallback: () => void
): void => {
  window.removeEventListener('online', onlineCallback);
  window.removeEventListener('offline', offlineCallback);
};

// Export the offline database service
const offlineDb = {
  addItem,
  updateItem,
  getItem,
  getAllItems,
  deleteItem,
  clearStore,
  queryByIndex,
  scheduleSync,
  isOnline,
  setupConnectivityListeners,
  removeConnectivityListeners
};

export default offlineDb; 