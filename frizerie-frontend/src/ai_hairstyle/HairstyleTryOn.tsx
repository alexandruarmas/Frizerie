import { useState, useRef, useEffect } from 'react';
import useAuth from '../auth/useAuth';

// Define hairstyle options
const HAIRSTYLE_OPTIONS = [
  { id: 1, name: 'Classic Fade', image: '/hairstyles/classic-fade.png', description: 'Clean and professional look with gradual fade' },
  { id: 2, name: 'Pompadour', image: '/hairstyles/pompadour.png', description: 'Voluminous style with short sides and back' },
  { id: 3, name: 'Buzz Cut', image: '/hairstyles/buzz-cut.png', description: 'Short and low-maintenance all around' },
  { id: 4, name: 'Textured Crop', image: '/hairstyles/textured-crop.png', description: 'Modern style with textured top and clean sides' },
  { id: 5, name: 'Long Layers', image: '/hairstyles/long-layers.png', description: 'Shoulder length with layered texture' },
];

// Model type for face landmarks
interface FaceLandmarks {
  points: { x: number, y: number }[];
  boundingBox: { x: number, y: number, width: number, height: number };
}

const HairstyleTryOn = () => {
  const { user } = useAuth();
  const [selectedHairstyle, setSelectedHairstyle] = useState<number | null>(null);
  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [isFaceDetected, setIsFaceDetected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [faceLandmarks, setFaceLandmarks] = useState<FaceLandmarks | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);

  // Start webcam
  const startWebcam = async () => {
    setIsWebcamActive(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Error accessing webcam:', err);
      setIsWebcamActive(false);
    }
  };

  // Stop webcam
  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsWebcamActive(false);
      setIsFaceDetected(false);
    }
  };

  // Detect face (simulated - would use actual face detection API in production)
  const detectFace = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    setIsProcessing(true);
    
    // Draw current video frame to canvas
    const context = canvasRef.current.getContext('2d');
    if (context) {
      context.drawImage(
        videoRef.current, 
        0, 0, 
        canvasRef.current.width, 
        canvasRef.current.height
      );
      
      // In a real implementation, we would call a face detection API here
      // For this demo, we'll simulate detection after a delay
      setTimeout(() => {
        // Simulate face detection with mock data
        const mockLandmarks: FaceLandmarks = {
          points: Array(68).fill(0).map(() => ({ 
            x: Math.random() * canvasRef.current!.width, 
            y: Math.random() * canvasRef.current!.height 
          })),
          boundingBox: { 
            x: canvasRef.current!.width * 0.25, 
            y: canvasRef.current!.height * 0.2, 
            width: canvasRef.current!.width * 0.5, 
            height: canvasRef.current!.height * 0.6 
          }
        };
        
        setFaceLandmarks(mockLandmarks);
        setIsFaceDetected(true);
        setIsProcessing(false);
        
        // Capture the current frame
        setCapturedImage(canvasRef.current!.toDataURL('image/png'));
        
        // Apply hairstyle overlay if one is selected
        if (selectedHairstyle !== null) {
          applyHairstyleOverlay(mockLandmarks, selectedHairstyle);
        }
      }, 1500);
    }
  };

  // Apply hairstyle overlay
  const applyHairstyleOverlay = (landmarks: FaceLandmarks, hairstyleId: number) => {
    if (!overlayCanvasRef.current) return;
    
    const context = overlayCanvasRef.current.getContext('2d');
    if (!context) return;
    
    // Clear previous overlay
    context.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
    
    // Get selected hairstyle
    const hairstyle = HAIRSTYLE_OPTIONS.find(h => h.id === hairstyleId);
    if (!hairstyle) return;
    
    // Load hairstyle image
    const hairstyleImg = new Image();
    hairstyleImg.onload = () => {
      // Position and scale based on face landmarks
      const { boundingBox } = landmarks;
      const scale = boundingBox.width * 1.5 / hairstyleImg.width;
      
      // Draw hairstyle positioned relative to face
      context.drawImage(
        hairstyleImg,
        boundingBox.x - boundingBox.width * 0.25,
        boundingBox.y - boundingBox.height * 0.5,
        hairstyleImg.width * scale,
        hairstyleImg.height * scale
      );
    };
    
    // Handle errors
    hairstyleImg.onerror = () => {
      console.error(`Failed to load hairstyle image: ${hairstyle.image}`);
    };
    
    // Set source to load image
    hairstyleImg.src = hairstyle.image;
  };

  // Select hairstyle
  const selectHairstyle = (hairstyleId: number) => {
    setSelectedHairstyle(hairstyleId);
    
    // Apply overlay if face is already detected
    if (faceLandmarks) {
      applyHairstyleOverlay(faceLandmarks, hairstyleId);
    }
  };

  // Take photo with current hairstyle
  const takePhoto = () => {
    if (!canvasRef.current || !overlayCanvasRef.current) return;
    
    // Create a composite image of webcam + hairstyle overlay
    const finalCanvas = document.createElement('canvas');
    finalCanvas.width = canvasRef.current.width;
    finalCanvas.height = canvasRef.current.height;
    
    const context = finalCanvas.getContext('2d');
    if (context) {
      // Draw base image
      context.drawImage(canvasRef.current, 0, 0);
      
      // Draw overlay
      context.drawImage(overlayCanvasRef.current, 0, 0);
      
      // Convert to data URL
      const dataUrl = finalCanvas.toDataURL('image/png');
      
      // Save photo (in a real app, this would save to user's account)
      savePhoto(dataUrl);
    }
  };
  
  // Save photo to user's collection (simulated)
  const savePhoto = (dataUrl: string) => {
    // In a real implementation, this would call an API to save the image
    console.log('Saving photo to user account:', user?.email);
    
    // Show success message or navigate to saved photos
    alert('Photo saved to your account!');
  };
  
  // Clean up on component unmount
  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Virtual Hairstyle Try-On</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left panel - Webcam and controls */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-4">
          <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden mb-4">
            {/* Video element (hidden when processing) */}
            <video 
              ref={videoRef}
              className={`absolute inset-0 w-full h-full object-cover ${isProcessing ? 'opacity-50' : ''}`}
              autoPlay
              playsInline
              muted
            />
            
            {/* Canvas for captured image */}
            <canvas 
              ref={canvasRef}
              className="absolute inset-0 w-full h-full object-cover hidden"
              width={640}
              height={480}
            />
            
            {/* Canvas for hairstyle overlay */}
            <canvas 
              ref={overlayCanvasRef}
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
              width={640}
              height={480}
            />
            
            {/* Placeholder when webcam is off */}
            {!isWebcamActive && (
              <div className="absolute inset-0 flex items-center justify-center text-white">
                <p>Click "Start Camera" to begin</p>
              </div>
            )}
            
            {/* Processing indicator */}
            {isProcessing && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>
            )}
          </div>
          
          {/* Control buttons */}
          <div className="flex flex-wrap gap-3 justify-center">
            {!isWebcamActive ? (
              <button
                onClick={startWebcam}
                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
              >
                Start Camera
              </button>
            ) : (
              <>
                <button
                  onClick={detectFace}
                  disabled={isProcessing}
                  className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md"
                >
                  Detect Face
                </button>
                
                <button
                  onClick={takePhoto}
                  disabled={!isFaceDetected || !selectedHairstyle}
                  className="bg-secondary-600 hover:bg-secondary-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md"
                >
                  Save Look
                </button>
                
                <button
                  onClick={stopWebcam}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md"
                >
                  Stop Camera
                </button>
              </>
            )}
          </div>
        </div>
        
        {/* Right panel - Hairstyle options */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-xl font-semibold mb-4">Choose a Hairstyle</h2>
          
          <div className="flex flex-col gap-3">
            {HAIRSTYLE_OPTIONS.map(style => (
              <button
                key={style.id}
                onClick={() => selectHairstyle(style.id)}
                className={`flex items-center p-3 rounded-lg border ${
                  selectedHairstyle === style.id 
                    ? 'border-primary-600 bg-primary-50' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="w-16 h-16 bg-gray-200 rounded-md overflow-hidden">
                  <img 
                    src={style.image} 
                    alt={style.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      // Fallback for missing images
                      (e.target as HTMLImageElement).src = 'https://via.placeholder.com/64?text=Style';
                    }}
                  />
                </div>
                <div className="ml-3 text-left">
                  <h3 className="font-medium">{style.name}</h3>
                  <p className="text-sm text-gray-600">{style.description}</p>
                </div>
              </button>
            ))}
          </div>
          
          {isFaceDetected && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800 text-sm">
                Face detected! Select a hairstyle to see how it looks on you.
              </p>
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-8 bg-white rounded-lg shadow-md p-4">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-3 border border-gray-200 rounded-lg">
            <div className="text-3xl mb-2">📷</div>
            <h3 className="font-medium mb-1">Step 1</h3>
            <p className="text-sm text-gray-600">Allow camera access and position your face in the frame</p>
          </div>
          <div className="p-3 border border-gray-200 rounded-lg">
            <div className="text-3xl mb-2">🔍</div>
            <h3 className="font-medium mb-1">Step 2</h3>
            <p className="text-sm text-gray-600">Click "Detect Face" to identify your facial features</p>
          </div>
          <div className="p-3 border border-gray-200 rounded-lg">
            <div className="text-3xl mb-2">💇</div>
            <h3 className="font-medium mb-1">Step 3</h3>
            <p className="text-sm text-gray-600">Try different hairstyles and save your favorites</p>
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-center text-sm text-gray-500">
        <p>This is a simulation of AI-powered hairstyle try-on. In a production environment, it would use advanced face detection and AR technologies.</p>
      </div>
    </div>
  );
};

export default HairstyleTryOn; 