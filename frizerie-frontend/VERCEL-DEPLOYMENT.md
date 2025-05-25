# Frizerie Frontend - Vercel Deployment Guide

This guide explains how to deploy the Frizerie Frontend to Vercel.

## Prerequisites

1. A [Vercel](https://vercel.com) account
2. The Frizerie repository on GitHub

## Deployment Steps

### 1. Connect Repository to Vercel

1. Log in to your Vercel account
2. Click "Add New" > "Project"
3. Import your GitHub repository
4. Select the "frizerie-frontend" directory as the root directory

### 2. Configure Project Settings

1. Framework Preset: Select "Vite"
2. Build Command: `npm run build` (should be auto-detected)
3. Output Directory: `dist` (should be auto-detected)
4. Install Command: `npm install` (default)

### 3. Environment Variables

Add the following environment variable:

- `VITE_API_URL`: URL of your backend API
  - For testing, you can use a placeholder or mock API
  - For production, set to your actual backend URL (e.g., `https://frizerie-backend.example.com/api/v1`)

### 4. Deploy

Click "Deploy" and wait for the build to complete.

## Updating the Deployment

Any push to the main branch of your repository will trigger a new deployment on Vercel.

## Troubleshooting

- If you see API connection errors, check that your `VITE_API_URL` is correct
- If the build fails, check the build logs in the Vercel dashboard
- For routing issues, ensure the vercel.json file is properly configured

## Next Steps

After deploying the frontend, you'll need to:

1. Deploy the backend to a suitable platform (e.g., Render, Railway, Heroku)
2. Update the `VITE_API_URL` in Vercel to point to your deployed backend
3. Test the complete application flow 