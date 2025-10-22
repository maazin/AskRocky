# Bull Bot - Setup Complete! 🎉

## ✅ What's Been Done

I've configured your Bull Bot application with your API keys and set up all the necessary components:

### 1. **API Keys Configured**
   - ✅ Pinecone API key added to `flaskServer/config.py`
   - ✅ OpenAI API key added to `flaskServer/config.py`

### 2. **Environment Files Created**
   - ✅ `server/.env` - Express server configuration
   - ✅ `client/.env` - Vite client configuration

### 3. **Dependencies Installed**
   - ✅ Python packages (Flask, LangChain, Pinecone, etc.)
   - ✅ Node.js packages for Express server
   - ✅ Node.js packages for Vite client

### 4. **Server URLs Configured**
   - ✅ Flask server → `http://localhost:8000`
   - ✅ Express server → `http://localhost:3000`
   - ✅ Vite client → `http://localhost:5173`

### 5. **Data Files Ready**
   - ✅ `Dataset-Pineline/cleaned_data.json` exists and is ready to upload

---

## ⚠️ ACTION REQUIRED - Complete These Steps

### Step 1: Set Up Pinecone Index

Your Pinecone API key is configured, but you need to manually create the index:

1. Go to https://app.pinecone.io/
2. Log in with your account
3. Click **"Create Index"**
4. Configure as follows:
   - **Index Name:** `bullbot`
   - **Dimensions:** `384`
   - **Metric:** `cosine`
   - **Cloud:** `AWS`
   - **Region:** `us-east-1`
5. Click **Create**

### Step 2: Fix OpenAI API Quota

Your OpenAI API key has exceeded its quota. You have two options:

**Option A: Add Credits to Existing Account**
1. Go to https://platform.openai.com/account/billing
2. Add a payment method
3. Add credits to your account

**Option B: Use a Different API Key**
1. Get a new API key from https://platform.openai.com/api-keys
2. Update `flaskServer/config.py` with the new key

### Step 3: Upload Data to Pinecone

Once Steps 1 & 2 are complete:

```bash
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot
python upload_to_pinecone.py
```

This will:
- Connect to your Pinecone index
- Load the cleaned USF data
- Generate embeddings using the BGE-small model
- Upload approximately 100+ documents to Pinecone

---

## 🚀 Running the Application

After completing all the above steps, start the application with these commands in **3 separate terminal windows**:

### Terminal 1: Flask Server (AI Backend)
```bash
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot/flaskServer
python app.py
```

Should display:
```
* Running on http://127.0.0.1:8000
```

### Terminal 2: Express Server (API Middleware)
```bash
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot/server
npm start
```

Should display:
```
Server is running on port 3000
```

### Terminal 3: Vite Client (Frontend)
```bash
cd /Users/maazinshaikh/Desktop/Mac/Programs/AskRocky/bullbot/client
npm run dev
```

Should display:
```
Local: http://localhost:5173/
```

### Access the App
Open your browser and navigate to: **http://localhost:5173**

---

## 📁 Project Structure

```
bullbot/
├── client/                 # React + Vite frontend
│   ├── .env               # ✅ Created - contains VITE_SERVER URL
│   └── src/
├── server/                # Express.js API server
│   ├── .env               # ✅ Created - contains Flask URL
│   └── server.js          # ✅ Updated - points to localhost:8000
├── flaskServer/           # Python Flask + AI backend
│   ├── config.py          # ✅ Updated - contains your API keys
│   ├── app.py             # Main Flask application
│   └── requirements.txt
├── Dataset-Pineline/      # Data processing notebooks
│   ├── cleaned_data.json  # ✅ Ready to upload
│   └── ...
├── upload_to_pinecone.py  # ✅ Created - upload script
└── SETUP_INSTRUCTIONS.sh  # ✅ Created - quick reference
```

---

## 🧪 Testing the Setup

### Test Individual Components

**Test Flask Server:**
```bash
curl http://localhost:8000/
```
Expected: `{"message": "Flask server is running"}`

**Test Express Server:**
```bash
curl -X POST http://localhost:3000/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is USF?"}'
```

**Test Full Chat:**
Open http://localhost:5173 and ask: "What is USF?" or "Tell me about USF programs"

---

## 🔧 Troubleshooting

### Issue: "OpenAI quota exceeded"
**Solution:** Add credits at https://platform.openai.com/account/billing or use a different API key

### Issue: "Pinecone index not found"
**Solution:** Create the index manually in Pinecone console (see Step 1 above)

### Issue: "Port already in use"
**Solution:** 
```bash
# Find and kill the process using the port
lsof -i :8000  # or :3000 or :5173
kill -9 <PID>
```

### Issue: "Module not found"
**Solution:** Reinstall dependencies:
```bash
# Python
cd flaskServer && pip install -r requirements.txt

# Node.js
cd server && npm install
cd client && npm install
```

---

## 📊 How It Works

1. **User** enters a question in the web interface (Vite/React)
2. **Client** sends the question to Express server (`localhost:3000`)
3. **Express** forwards the request to Flask server (`localhost:8000`)
4. **Flask** processes the question:
   - Generates embedding for the question
   - Searches Pinecone for relevant USF content
   - Sends context to OpenAI GPT-3.5
   - Returns answer with sources
5. **Response** flows back through Express to the Client
6. **User** sees the answer with source links

---

## 🎯 Next Steps After Setup

Once everything is running:

1. **Test with various questions:**
   - "What programs does USF offer?"
   - "How do I apply to USF?"
   - "What are the admission requirements?"

2. **Deploy to production** (optional):
   - Client → Vercel
   - Express Server → Railway/Render
   - Flask Server → AWS EC2 (see `flaskServer/SETUP.md`)

---

## 📞 Need Help?

If you encounter issues:

1. Check that all 3 servers are running
2. Check browser console for errors (F12)
3. Check terminal outputs for error messages
4. Verify API keys are correct in `flaskServer/config.py`
5. Verify Pinecone index exists and has data

---

## Summary of Remaining Tasks

- [ ] Create Pinecone index at https://app.pinecone.io/
- [ ] Fix OpenAI API quota/key
- [ ] Run `python upload_to_pinecone.py`
- [ ] Start all 3 servers
- [ ] Test the application!

**Good luck with your Bull Bot! 🐂🤖**
