# Personal Engineering OS — Deployment Guide

## 1. Deploy the Backend to Render (Free!)

Render is a great free option for deploying the backend!

### Steps:
1. Go to [https://render.com/](https://render.com/) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repo `siddhpararudra2-debug/troyy.ai`
4. Configure the service:
   - Name: `personal-engineering-os-backend`
   - Branch: `main`
   - Runtime: `Docker`
   - Plan: `Free`
5. Click "Create Web Service"
6. Wait for the deployment to finish! It should give you a URL like `https://personal-engineering-os-backend.onrender.com`

## 2. Update the Frontend to Point to the Deployed Backend

Once your backend is deployed:
1. Go to your GitHub repo's Settings
2. Go to Secrets and Variables → Actions
3. Add a Repository Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-render-backend-url.onrender.com/api/v1`
4. Re-run your GitHub Pages deployment (push a new commit to trigger it)

## 3. You're Done! 🚀

Your full Personal Engineering OS is now deployed!
- Frontend: `https://siddhpararudra2-debug.github.io/troyy.ai/`
- Backend: Your Render URL

## Optional: Deploy to Fly.io instead

1. Install Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Run:
   ```bash
   fly launch
   fly deploy
   ```
