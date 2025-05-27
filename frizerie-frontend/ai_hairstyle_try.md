┌────────────────────┐
│    Frontend (Web)  │
│  - Webcam capture  │
│  - Base64 encode   │
│  - Send via WS     │
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────┐
│ FastAPI Backend (WebSocket) │
│  /ws/ai_hairstyle_try        │
│  - Receive base64 frame      │
│  - Decode image (OpenCV)     │
│  - Segment hair (BiSeNet)    │
│  - Overlay hairstyle (PNG)   │
│  - Encode image to base64    │
│  - Return via WebSocket      │
└────────┬─────────────────────┘
         │
         ▼
┌────────────────────┐
│   Frontend (Web)   │
│ - Receive frame    │
│ - Display styled   │
└────────────────────┘
┌────────────────────┐
│    Frontend (Web)  │
│  - Webcam capture  │
│  - Base64 encode   │
│  - Send via WS     │
└────────┬───────────┘
         │
         ▼
┌──────────────────────────────┐
│ FastAPI Backend (WebSocket) │
│  /ws/ai_hairstyle_try        │
│  - Receive base64 frame      │
│  - Decode image (OpenCV)     │
│  - Segment hair (BiSeNet)    │
│  - Overlay hairstyle (PNG)   │
│  - Encode image to base64    │
│  - Return via WebSocket      │
└────────┬─────────────────────┘
         │
         ▼
┌────────────────────┐
│   Frontend (Web)   │
│ - Receive frame    │
│ - Display styled   │
└────────────────────┘
You're building a real-time AI hairstyle try-on module using FastAPI and WebSocket. Here's how the flow works:

The frontend opens a WebSocket and sends webcam frames as base64 strings.

The backend receives each frame via the /ws/ai_hairstyle_try WebSocket endpoint.

The image is decoded using OpenCV, passed through a BiSeNet hair segmentation model, and a selected hairstyle PNG is overlaid based on alignment logic.

The final image is encoded back to base64 and sent to the frontend, which renders it on a live preview element.

This architecture prioritizes speed and responsiveness. Further improvements could include MediaPipe for facial landmarks or GANs for more realistic synthesis.

