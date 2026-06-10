# Deploying the AURA backend to Hugging Face Spaces (Docker, free)

The frontend goes to Vercel; the FastAPI backend goes to a free HF Docker Space.
The image bakes Playwright/Chromium so the PDF report works cold.

---

## 0. Prereqs (one-time)
- A free Hugging Face account: https://huggingface.co/join (confirm your email!)
- A **free Groq key** (no card): https://console.groq.com/keys → copy the `gsk_...`

## 1. Create the Space
1. https://huggingface.co/new-space
2. **Owner:** you · **Space name:** `aura-backend`
3. **SDK:** **Docker** → template **Blank**
4. **Hardware:** CPU basic (free) · **Visibility:** Public → **Create Space**

## 2. Push the backend (assembled for you)
Claude assembles a clean Space working copy (`Dockerfile` + `AURA-BACKEND/` + the
Space README with `app_port: 7860`). Then you push with a **write token**
(https://huggingface.co/settings/tokens → New token → Write):

```bash
cd <assembled-space-dir>
git push origin main        # username: <you> · password: the hf_… token
```
HF builds the Dockerfile automatically (a few minutes — CPU torch is gone now,
so it's fast).

## 3. Space secrets / variables
Space → **Settings → Variables and secrets**:

| Type | Key | Value |
|---|---|---|
| 🔒 Secret | `GROQ_API_KEY` | your free `gsk_...` key |
| Variable | `PORT` | `7860` |
| Variable | `ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app,http://localhost:3000` |

(Optional paid upgrades: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.)

## 4. Verify
`https://<you>-aura-backend.hf.space/health` → `{"status":"ok","version":"5.0.0"}`
`https://<you>-aura-backend.hf.space/api/ai/providers` → groq `configured: true`

## 5. Frontend → Vercel
1. Import the repo, set **root directory** to `AURA-FRONTEND`
2. Env var: `NEXT_PUBLIC_API_URL = https://<you>-aura-backend.hf.space`
3. Deploy (NEXT_PUBLIC_* is baked at build time — a change needs a redeploy)
4. Add the resulting Vercel URL to the Space's `ALLOWED_ORIGINS`, restart the Space.

## 6. Smoke-test live
Open the Vercel URL → Try with sample data → clean → explore → AI chat (free Groq)
→ Docs → Generate the Data Intelligence Report.
