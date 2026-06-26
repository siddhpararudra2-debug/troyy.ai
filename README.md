# Personal Engineering OS (troyy.ai)

A complete engineering operating system for personal use!

## 🚀 Deployed

- **Frontend**: https://siddhpararudra2-debug.github.io/troyy.ai/
- **Backend**: [Set up on Render]

## 🛠️ Deploy Backend to Render (3 Easy Steps!)

1. **Create a Web Service**:
   - Go to: https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Select your repo `siddhpararudra2-debug/troyy.ai`
   - Click "Continue"

2. **Configure Service**:
   - Name: `personal-engineering-os`
   - Root Directory: (leave blank, it'll use repo root)
   - Runtime: `Docker`
   - Instance Type: `Free`
   - Click "Create Web Service"

3. **Get Secrets for Auto-Deploy**:
   - Once the service is created, copy its **Service ID** from the URL
   - Go to your Render account → Settings → API Keys → Create API Key
   - In your GitHub repo, go to **Settings → Secrets and Variables → Actions**
   - Add these Repository Secrets:
     - `RENDER_SERVICE_ID`: (your Render Service ID from step 3)
     - `RENDER_API_KEY`: (your Render API Key from step 3)
     - `NEXT_PUBLIC_API_URL`: (your Render URL once deployed, e.g., `https://your-service.onrender.com/api/v1`)

That's it! Now every time you push to main, both frontend and backend auto-deploy! 🚀

## Local Development

1. Backend:
   ```bash
   python minimal_main.py
   # or using Docker
   docker build -t peos-backend . && docker run -p 8000:8000 peos-backend
   ```
2. Frontend:
   ```bash
   cd frontend && npm install && npm run dev
   ```
