# Engineering OS Deployment Guide

This guide walks you through deploying the Vercel + Supabase + Self-Hosted AI stack.

## Phase 1: Database Setup (Supabase)

1. Create a new project in [Supabase](https://supabase.com).
2. Navigate to the SQL Editor.
3. Open `supabase/migrations/0001_initial_schema.sql` and run it. This creates the user profiles, projects, and enables Vector extensions.
4. Open `supabase/migrations/0002_storage_setup.sql` and run it. This creates the necessary file storage buckets with correct security policies.
5. Go to **Project Settings -> API** to copy your `Project URL` and `anon public` key.
6. Go to **Project Settings -> Database** and copy the Connection String (use the Transaction connection pool, typically port 6543).

## Phase 2: Frontend Deployment (Vercel)

1. Commit your codebase to GitHub.
2. Log into [Vercel](https://vercel.com) and click **Add New -> Project**.
3. Import your GitHub repository.
4. Set the Framework Preset to **Next.js**.
5. Set the Root Directory to `frontend`.
6. Add the following Environment Variables:
   - `NEXT_PUBLIC_SUPABASE_URL`: (from Phase 1)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (from Phase 1)
   - `NEXT_PUBLIC_API_URL`: (The URL where your backend will be hosted, e.g., `https://api.yourdomain.com/api`)
7. Click **Deploy**.

## Phase 3: AI Workstation Setup

1. On your dedicated GPU machine, install [Ollama](https://ollama.ai).
2. Pull the required models:
   ```bash
   ollama run qwen2.5:32b
   ollama run gemma2:9b
   ```
3. By default, Ollama only listens on localhost. To allow your backend to access it, set the `OLLAMA_HOST` environment variable to `0.0.0.0:11434` before starting the Ollama service.
4. **Security Note:** Do not expose Ollama directly to the public internet. Use a secure tunnel (like Tailscale, Cloudflare Tunnels, or Wireguard) between your AI Workstation and your Backend VPS.

## Phase 4: Backend Deployment (Docker / VPS)

1. On your VPS or container host, clone the repository.
2. Navigate to the `backend` directory.
3. Copy `production.env` to `.env` and fill in the values:
   - `DATABASE_URL` (from Supabase)
   - `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
   - `OLLAMA_URL` (IP of your AI workstation or the secure tunnel IP, e.g., `http://100.x.y.z:11434`)
4. Run docker-compose to start the backend and Redis:
   ```bash
   docker-compose up -d
   ```
5. Configure your DNS to point `api.yourdomain.com` to your VPS IP address.
6. (Optional but recommended) Run Let's Encrypt Certbot to generate SSL certificates for the Nginx proxy configured in `docker-compose.yml`.

## Phase 5: Verification

- Visit your Vercel frontend URL.
- Create a new account.
- The system will create an auth user, trigger the database function to create a profile, and log you in.
- Test uploading a file to verify storage policies.
- Test an AI prompt to verify the backend can communicate with your local Ollama instance.
