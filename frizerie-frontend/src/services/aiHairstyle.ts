import api from './api';

// Types
export interface SavedHairstyle {
  id: string;
  userId: string;
  imageUrl: string;
  hairstyleId: number;
  createdAt: string;
  name: string;
}

export interface HairstyleOption {
  id: number;
  name: string;
  image: string;
  description: string;
}

// Service for AI hairstyle operations
const aiHairstyleService = {
  // Get all available hairstyle options
  getHairstyleOptions: async (): Promise<HairstyleOption[]> => {
    try {
      // In a real implementation, this would fetch from an API
      // For now, we'll return mock data
      return [
        { id: 1, name: 'Classic Fade', image: '/hairstyles/classic-fade.png', description: 'Clean and professional look with gradual fade' },
        { id: 2, name: 'Pompadour', image: '/hairstyles/pompadour.png', description: 'Voluminous style with short sides and back' },
        { id: 3, name: 'Buzz Cut', image: '/hairstyles/buzz-cut.png', description: 'Short and low-maintenance all around' },
        { id: 4, name: 'Textured Crop', image: '/hairstyles/textured-crop.png', description: 'Modern style with textured top and clean sides' },
        { id: 5, name: 'Long Layers', image: '/hairstyles/long-layers.png', description: 'Shoulder length with layered texture' },
      ];
      
      // API implementation would be:
      // const response = await api.get('/hairstyles/options');
      // return response.data;
    } catch (error) {
      console.error('Error fetching hairstyle options:', error);
      return [];
    }
  },
  
  // Save a tried hairstyle to user's collection
  saveHairstyle: async (userId: string, hairstyleId: number, imageData: string): Promise<SavedHairstyle | null> => {
    try {
      // In a real implementation, this would send the data to an API
      // For now, we'll save to local storage and return a mock response
      
      // Create a mock saved hairstyle
      const savedHairstyle: SavedHairstyle = {
        id: `hairstyle_${Date.now()}`,
        userId,
        imageUrl: imageData,
        hairstyleId,
        createdAt: new Date().toISOString(),
        name: `Hairstyle ${hairstyleId}`,
      };
      
      // Get existing saved hairstyles from local storage
      const savedHairstylesJson = localStorage.getItem('savedHairstyles');
      const savedHairstyles: SavedHairstyle[] = savedHairstylesJson 
        ? JSON.parse(savedHairstylesJson) 
        : [];
      
      // Add new hairstyle and save back to local storage
      savedHairstyles.push(savedHairstyle);
      localStorage.setItem('savedHairstyles', JSON.stringify(savedHairstyles));
      
      return savedHairstyle;
      
      // API implementation would be:
      // const formData = new FormData();
      // formData.append('userId', userId);
      // formData.append('hairstyleId', hairstyleId.toString());
      // formData.append('image', imageData);
      // const response = await api.post('/hairstyles/save', formData);
      // return response.data;
    } catch (error) {
      console.error('Error saving hairstyle:', error);
      return null;
    }
  },
  
  // Get all saved hairstyles for a user
  getUserHairstyles: async (userId: string): Promise<SavedHairstyle[]> => {
    try {
      // In a real implementation, this would fetch from an API
      // For now, we'll retrieve from local storage
      
      // Get saved hairstyles from local storage
      const savedHairstylesJson = localStorage.getItem('savedHairstyles');
      const allSavedHairstyles: SavedHairstyle[] = savedHairstylesJson 
        ? JSON.parse(savedHairstylesJson) 
        : [];
      
      // Filter to only include the current user's hairstyles
      const userHairstyles = allSavedHairstyles.filter(
        hairstyle => hairstyle.userId === userId
      );
      
      return userHairstyles;
      
      // API implementation would be:
      // const response = await api.get(`/hairstyles/user/${userId}`);
      // return response.data;
    } catch (error) {
      console.error('Error fetching user hairstyles:', error);
      return [];
    }
  },
  
  // Delete a saved hairstyle
  deleteHairstyle: async (hairstyleId: string): Promise<boolean> => {
    try {
      // In a real implementation, this would send a delete request to an API
      // For now, we'll remove from local storage
      
      // Get saved hairstyles from local storage
      const savedHairstylesJson = localStorage.getItem('savedHairstyles');
      const savedHairstyles: SavedHairstyle[] = savedHairstylesJson 
        ? JSON.parse(savedHairstylesJson) 
        : [];
      
      // Filter out the hairstyle to delete
      const updatedHairstyles = savedHairstyles.filter(
        hairstyle => hairstyle.id !== hairstyleId
      );
      
      // Save back to local storage
      localStorage.setItem('savedHairstyles', JSON.stringify(updatedHairstyles));
      
      return true;
      
      // API implementation would be:
      // await api.delete(`/hairstyles/${hairstyleId}`);
      // return true;
    } catch (error) {
      console.error('Error deleting hairstyle:', error);
      return false;
    }
  }
};

export default aiHairstyleService; 