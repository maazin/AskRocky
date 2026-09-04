# 🚀 Deploy AskRocky to Vercel (Frontend-only)

This project deploys the frontend to Vercel as a static site. The Flask backend runs outside of Vercel (Render/Railway/your server or a temporary tunnel), and the client calls it via the `VITE_SERVER` URL.

---

## Prerequisites

Before deploying, ensure you have:

1. ✅ **Pinecone Index Created**
   - Index name: `bullbot`
   - Dimensions: 384
   - Metric: cosine
   - Already populated with data

2. ✅ **OpenAI API Key Working**
   - Has available credits
   - Tested successfully

3. ✅ **Vercel Account**
   - Sign up at https://vercel.com (free)
   - Can use GitHub login

4. ✅ **Vercel CLI Installed**
   ```bash
   npm install -g vercel
   ```

---

## Local Testing (Simplified Setup)

Before deploying, test locally with the new simplified architecture:

### Start the Flask API (No Express needed!)

```bash
cd /path/to/askrocky
python api/index.py
```

Server will run on `http://localhost:8000`

### Start the Vite Client

```bash
cd client
npm run dev
```

Client will run on `http://localhost:5173`

### Test It

Open http://localhost:5173 and ask "What is USF?"

---

## Deploy the Frontend to Vercel

### Step 1: Login to Vercel

```bash
cd /path/to/askrocky
vercel login
```

### Step 2: Provide the backend URL to the frontend

Set an environment variable named `VITE_SERVER` in your Vercel Project (Settings → Environment Variables) to your backend URL, e.g.:

```
VITE_SERVER=https://your-backend.example.com/api/chat
```

Notes:
- `client/.env.production` is intentionally blank; Vercel injects `VITE_SERVER` at build time.
- For local dev you already have `client/.env` → `VITE_SERVER=http://localhost:8000/api/chat`.

### Step 3: Deploy

```bash
vercel
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name?** → askrocky (or your choice)
- **Directory with code?** → ./ (current directory)
- **Override settings?** → No

Vercel will build the frontend and give you a live URL (e.g., `https://askrocky.vercel.app`).

### Step 4: Verify Deployment

Once deployed, Vercel will give you a URL. Test it:

1. Open the URL in your browser
2. Try asking questions about USF
3. Check the Vercel logs if there are issues:
   ```bash
   vercel logs
   ```

---

## Backend deployment (Render/Railway)

Host the Flask API on a platform designed for Python services, then point `VITE_SERVER` at it.

Minimal requirements:
- Python 3.11
- Start command: `python api/index.py`
- Env vars: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX`

Once deployed, copy the public URL (e.g., `https://your-backend.onrender.com/api/chat`) into the Vercel `VITE_SERVER` variable and redeploy the frontend.

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Check that `requirements.txt` is in the root directory with all dependencies.

### Issue: "Pinecone connection failed"

**Solution:** 
1. Verify your Pinecone API key is set correctly in Vercel
2. Check that the index name is exactly `bullbot`
3. Ensure the index has data uploaded

### Issue: "OpenAI quota exceeded"

**Solution:** 
1. Add credits to your OpenAI account
2. Update the API key in Vercel environment variables

### Issue: Backend timeouts / cold starts on Vercel

The Flask backend is not deployed on Vercel in this setup to avoid serverless limitations (package size, startup time). Use a dedicated Python host.

### Issue: Function timeout

**Solution:** Vercel free tier has a 10-second timeout. If needed:
1. Upgrade to Pro plan ($20/month) for 60-second timeout
2. Or optimize by pre-loading models (already done in the code)

---

## Architecture

```
Client (Vercel Static) → Flask API (Render/Railway/Your server)
```

Benefits:
- ✅ Simple, reliable frontend hosting
- ✅ Flexible backend hosting without serverless limits

---

## Project Structure for Vercel

```
askrocky/
├── api/
│   └── index.py              # Flask API (Vercel serverless function)
├── client/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── package.json
│   └── .env.production       # Points to /api/chat
├── flaskServer/
│   └── config.py             # Config imported by api/index.py
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
└── VERCEL_DEPLOYMENT.md      # This file
```

---

## Monitoring & Logs

### View Logs
```bash
vercel logs --follow
```

### View Deployment in Dashboard
```bash
vercel open
```

Or go to: https://vercel.com/dashboard

---

## Costs

### Free Tier Includes:
- ✅ Unlimited static deployments
- ✅ 100GB bandwidth/month
- ✅ Serverless function execution (fair use)
- ✅ Automatic HTTPS
- ✅ Preview deployments for Git branches

### You Pay For:
- OpenAI API usage (~$0.002 per request with GPT-3.5-turbo)
- Pinecone (free tier: 1 index, 100K vectors)

**Estimated cost for MVP:** $0-5/month depending on usage

---

## Next Steps After Deployment

1. **Custom Domain** (Optional)
   ```bash
   vercel domains add yourdomain.com
   ```

2. **Analytics** (Optional)
   - Enable Vercel Analytics in dashboard
   - Track page views and performance

3. **Continuous Deployment**
   - Push to GitHub
   - Connect repo to Vercel
   - Auto-deploy on every push

4. **Monitor Usage**
   - Check Vercel dashboard for function invocations
   - Monitor OpenAI usage at platform.openai.com
   - Check Pinecone dashboard for query counts

---

## Quick Reference

### Deploy Updates (frontend)
```bash
vercel --prod
```

### Rollback to Previous Deployment
```bash
vercel rollback
```

### View All Deployments
```bash
vercel ls
```

### Remove Project (frontend)
```bash
vercel remove askrocky
```

---

## Summary

With Vercel-only deployment, you get:
- 🚀 **Simple deployment:** One command
- 💰 **Free hosting:** No AWS bills
- ⚡ **Fast performance:** Global CDN
- 🔒 **Secure:** Automatic HTTPS
- 📊 **Easy monitoring:** Vercel dashboard

Perfect for MVP and can scale to production!
