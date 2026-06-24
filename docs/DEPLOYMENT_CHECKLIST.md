# Production Deployment Checklist

Use this checklist to ensure all systems are ready for production deployment of the Engineering OS.

## 1. Infrastructure Preparation
- [ ] Vercel account created and linked to GitHub.
- [ ] Supabase project created (Pro plan recommended for production).
- [ ] VPS / Docker Host provisioned (e.g., Render, Fly.io, or dedicated VPS).
- [ ] Dedicated AI Workstation set up with Ollama installed.

## 2. Supabase Configuration
- [ ] Executed `0001_initial_schema.sql` via SQL Editor.
- [ ] Executed `0002_storage_setup.sql` via SQL Editor.
- [ ] Verified Row Level Security (RLS) is enabled on `profiles`, `projects`, etc.
- [ ] Captured API URL, `anon_key`, and `service_role_key`.
- [ ] Captured Database Connection String (Transaction Pooler - port 6543).

## 3. Environment Variables
- [ ] Frontend `.env.production` populated in Vercel.
  - [ ] `NEXT_PUBLIC_SUPABASE_URL`
  - [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - [ ] `NEXT_PUBLIC_API_URL`
- [ ] Backend `production.env` populated on Host.
  - [ ] `DATABASE_URL`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_KEY`
  - [ ] `OLLAMA_URL`
  - [ ] `REDIS_URL`

## 4. Security & Networking
- [ ] Configured custom domains.
- [ ] Validated HTTPS/SSL certificates (via Vercel for frontend, Let's Encrypt / Nginx for backend).
- [ ] Configured CORS in backend to only allow frontend domain.
- [ ] Ensure AI Workstation is NOT publicly exposed without authentication (use a VPN or secure tunnel like Tailscale to connect it to the Backend).

## 5. Deployment Execution
- [ ] Pushed code to `main` branch.
- [ ] Verified GitHub Actions completed successfully.
- [ ] Vercel frontend deployed and reachable.
- [ ] Backend Docker container running and healthy (check `/api/health`).

## 6. Post-Deployment Verification
- [ ] Tested User Registration & Login.
- [ ] Tested File Upload to Supabase Storage.
- [ ] Tested Realtime Database updates.
- [ ] Tested AI Inference via the frontend (which routes through Backend -> AI Gateway -> Ollama).
- [ ] Verified backup scripts execute successfully.
