# 🚀 AskRocky - Quick Start (Updated for Vercel)

## ✅ What's Configured

Everything is set up for **Vercel-only deployment** (simpler than AWS):

- ✅ API keys configured
- ✅ All dependencies installed
- ✅ Vercel deployment files created (`vercel.json`, `api/index.py`)
- ✅ No Express server needed (simplified architecture)

---

## ⚠️ Complete These 2 Steps First

### 1. Create Pinecone Index (5 min)
   - Go to https://app.pinecone.io/
   - Create index: `bullbot`, dimensions: `384`, metric: `cosine`

### 2. Fix OpenAI API 
   - Add credits at https://platform.openai.com/account/billing
   - OR update key in `flaskServer/config.py`

### 3. Upload Data
```bash
python upload_to_pinecone.py
```

---

## 🏠 Local Development (2 terminals)

### Terminal 1: Flask API
```bash
cd /path/to/askrocky
python api/index.py
```

### Terminal 2: Vite Client
```bash
cd client
npm run dev
```

### Test
Open http://localhost:5173

---

## ☁️ Deploy to Vercel (Production)

### One-Time Setup
```bash
npm install -g vercel
vercel login
```

### Set API Keys in Vercel
```bash
vercel env add PINECONE_API
# Paste: pcsk_your_pinecone_key_here

vercel env add OPENAI_API_KEY
# Paste: your-openai-key

# Select: Production, Preview, Development (all)
```

### Deploy
```bash
vercel
```

That's it! You'll get a live URL like `https://askrocky.vercel.app`

---

## 📚 Documentation

- **VERCEL_DEPLOYMENT.md** - Complete Vercel deployment guide
- **SETUP_COMPLETE.md** - Original full setup documentation

---

## 🎯 Architecture Comparison

### Old (Complex):
```
Client → Express → Flask (3 servers, 3 platforms)
```

### New (Simple):
```
Client → Flask API (1 platform: Vercel)
```

### Benefits:
- ✅ Free hosting
- ✅ One command deployment
- ✅ Auto-scaling
- ✅ HTTPS included
- ✅ No server management

---

## 💰 Costs

- **Vercel:** Free
- **Pinecone:** Free tier (1 index)
- **OpenAI:** ~$0.002/request

**Total:** $0-5/month for MVP

---

## 🆘 Quick Troubleshooting

**"OpenAI quota exceeded"** → Add credits or new key  
**"Pinecone index not found"** → Create index first  
**"Port in use"** → Kill process: `lsof -i :8000`  
**Cold start slow** → Normal for first request (~10-30s)

---

## Ready to Deploy? 

1. ✅ Pinecone index created
2. ✅ OpenAI key working
3. ✅ Data uploaded to Pinecone
4. Run: `vercel`

🎉 **You'll have a live chatbot in 2 minutes!**
