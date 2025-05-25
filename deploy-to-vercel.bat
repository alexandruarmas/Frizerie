@echo off
echo Preparing to deploy Frizerie frontend to Vercel...

:: Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Vercel CLI not found. Installing...
  npm install -g vercel
) else (
  echo Vercel CLI already installed.
)

:: Navigate to frontend directory
cd frizerie-frontend

:: Deploy to Vercel
echo Deploying to Vercel...
vercel

echo.
echo If deployment was successful, your app should now be available on Vercel!
echo You can view your deployments at https://vercel.com/dashboard
echo.
echo Don't forget to set the VITE_API_URL environment variable in your Vercel project settings.
pause 