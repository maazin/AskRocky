# 🚀 Deploy Bull Bot to Vercel

## Why Vercel Only?

Instead of the complex AWS + Cyclic + Vercel setup, we can deploy **everything** to Vercel:
- ✅ Frontend (Vite/React) → Vercel Static
- ✅ Backend (Flask API) → Vercel Serverless Functions
- ✅ No need for Express server
- ✅ No need for AWS EC2
- ✅ 100% free for MVP/development

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
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot
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

## Deploy to Vercel

### Step 1: Login to Vercel

```bash
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot
vercel login
```

### Step 2: Set Environment Variables

You need to add your API keys as environment secrets in Vercel:

```bash
# Add Pinecone API key
vercel env add PINECONE_API

# When prompted, paste your key (example placeholder):
# pcsk_your_pinecone_key_here

# Add OpenAI API key
vercel env add OPENAI_API_KEY

# When prompted, paste your key (example placeholder):
# sk-your-openai-key-here
```

For each variable, when asked which environments:
- Select: **Production, Preview, and Development** (press Space to select all, Enter to confirm)

### Step 3: Deploy!

```bash
vercel
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name?** → bullbot (or your choice)
- **Directory with code?** → ./ (current directory)
- **Override settings?** → No

Vercel will:
1. Build your frontend
2. Deploy your Flask backend as serverless functions
3. Give you a live URL (e.g., `https://bullbot.vercel.app`)

### Step 4: Verify Deployment

Once deployed, Vercel will give you a URL. Test it:

1. Open the URL in your browser
2. Try asking questions about USF
3. Check the Vercel logs if there are issues:
   ```bash
   vercel logs
   ```

---

## Environment Variables Configuration

The following environment variables are read from `flaskServer/config.py`:

- `PINECONE_API` - Your Pinecone API key
- `PINECONE_ENV` - Set to `us-east-1` (in config.py)
- `PINECONE_INDEX` - Set to `bullbot` (in config.py)
- `OPENAI_API_KEY` - Your OpenAI API key

You only need to set `PINECONE_API` and `OPENAI_API_KEY` in Vercel, the others are hardcoded in config.py.

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

### Issue: Cold start is slow

**Solution:** This is normal for Vercel serverless functions. First request may take 10-30 seconds as it:
- Loads the embedding model
- Connects to Pinecone
- Initializes OpenAI

Subsequent requests will be much faster (1-3 seconds).

### Issue: Function timeout

**Solution:** Vercel free tier has a 10-second timeout. If needed:
1. Upgrade to Pro plan ($20/month) for 60-second timeout
2. Or optimize by pre-loading models (already done in the code)

---

## What Changed From Original Architecture?

### Old (3-server setup):
```
Client (Vercel) → Express Server (Cyclic) → Flask Server (AWS EC2)
```

### New (Vercel-only):
```
Client (Vercel Static) → Flask API (Vercel Serverless)
```

### Benefits:
- ✅ Simpler deployment
- ✅ No server management
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Auto-scaling

---

## Project Structure for Vercel

```
bullbot/
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

### Deploy Updates
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

### Remove Project
```bash
vercel remove bullbot
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
