import { useState, useEffect } from 'react';
import useAuth from '../auth/useAuth';
import aiHairstyleService, { SavedHairstyle } from '../services/aiHairstyle';

const SavedHairstyles = () => {
  const { user } = useAuth();
  const [savedHairstyles, setSavedHairstyles] = useState<SavedHairstyle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedHairstyle, setSelectedHairstyle] = useState<SavedHairstyle | null>(null);
  
  // Load saved hairstyles on component mount
  useEffect(() => {
    const loadSavedHairstyles = async () => {
      if (!user?.id) return;
      
      setIsLoading(true);
      try {
        const hairstyles = await aiHairstyleService.getUserHairstyles(user.id);
        setSavedHairstyles(hairstyles);
      } catch (error) {
        console.error('Error loading saved hairstyles:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadSavedHairstyles();
  }, [user?.id]);
  
  // Delete a hairstyle
  const handleDelete = async (hairstyleId: string) => {
    if (window.confirm('Are you sure you want to delete this saved hairstyle?')) {
      try {
        const success = await aiHairstyleService.deleteHairstyle(hairstyleId);
        if (success) {
          setSavedHairstyles(prevHairstyles => 
            prevHairstyles.filter(h => h.id !== hairstyleId)
          );
          
          if (selectedHairstyle?.id === hairstyleId) {
            setSelectedHairstyle(null);
          }
        }
      } catch (error) {
        console.error('Error deleting hairstyle:', error);
      }
    }
  };
  
  // View a hairstyle in detail
  const handleViewDetail = (hairstyle: SavedHairstyle) => {
    setSelectedHairstyle(hairstyle);
  };
  
  // Close detail view
  const handleCloseDetail = () => {
    setSelectedHairstyle(null);
  };
  
  // Render empty state when no hairstyles
  if (!isLoading && savedHairstyles.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">My Saved Hairstyles</h1>
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-5xl mb-4">💇</div>
          <h2 className="text-2xl font-semibold mb-2">No saved hairstyles yet</h2>
          <p className="text-gray-600 mb-6">Try on some virtual hairstyles and save your favorites!</p>
          <a 
            href="/hairstyle-try-on" 
            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-md inline-block"
          >
            Try Hairstyles Now
          </a>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">My Saved Hairstyles</h1>
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* Grid of saved hairstyles */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {savedHairstyles.map(hairstyle => (
              <div 
                key={hairstyle.id}
                className="bg-white rounded-lg shadow-md overflow-hidden"
              >
                <div 
                  className="h-48 bg-gray-200 cursor-pointer"
                  onClick={() => handleViewDetail(hairstyle)}
                >
                  <img 
                    src={hairstyle.imageUrl} 
                    alt={hairstyle.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-3">
                  <h3 className="font-medium">{hairstyle.name}</h3>
                  <p className="text-xs text-gray-500">
                    {new Date(hairstyle.createdAt).toLocaleDateString()}
                  </p>
                  <div className="flex justify-between mt-2">
                    <button
                      onClick={() => handleViewDetail(hairstyle)}
                      className="text-primary-600 hover:text-primary-800 text-sm"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(hairstyle.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Link to try more hairstyles */}
          <div className="text-center">
            <a 
              href="/hairstyle-try-on" 
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-md inline-block"
            >
              Try More Hairstyles
            </a>
          </div>
          
          {/* Hairstyle detail modal */}
          {selectedHairstyle && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full overflow-hidden">
                <div className="flex justify-between items-center p-4 border-b">
                  <h2 className="text-xl font-semibold">{selectedHairstyle.name}</h2>
                  <button 
                    onClick={handleCloseDetail}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>
                <div className="p-4">
                  <div className="aspect-video bg-gray-200 rounded-md overflow-hidden mb-4">
                    <img 
                      src={selectedHairstyle.imageUrl} 
                      alt={selectedHairstyle.name}
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      Saved on {new Date(selectedHairstyle.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex justify-end space-x-3">
                    <button
                      onClick={() => handleDelete(selectedHairstyle.id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
                    >
                      Delete
                    </button>
                    <button
                      onClick={handleCloseDetail}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SavedHairstyles; 