import { useState, useEffect } from 'react';
import { checkOfflineStatus } from '../services/swRegistration';

const OfflineIndicator = () => {
  const [isOffline, setIsOffline] = useState(false);
  
  useEffect(() => {
    // Set up offline status checker and clean up on unmount
    const cleanup = checkOfflineStatus(setIsOffline);
    return cleanup;
  }, []);
  
  if (!isOffline) return null;
  
  return (
    <div className="fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded-md shadow-lg z-50 flex items-center space-x-2">
      <span className="inline-block w-3 h-3 bg-white rounded-full animate-pulse"></span>
      <span>You're offline. Data will sync when connection is restored.</span>
    </div>
  );
};

export default OfflineIndicator; 