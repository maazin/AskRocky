# Bull Bot
Bull Bot – a chatbot designed to comprehend natural language queries and respond with precise answers, accompanied by the most relevant website links. Live at [BullBot.tech](https://www.bullbot.tech)

## Tech Stack
- Vite.js / Node.js / Python / langchain / 
- Database: Pinecone
- Embedding Model: [BAAI/bge-small-en](https://huggingface.co/BAAI/bge-small-en)
- Large Language Model: OpenAI API
- Deployment: Vercel / Cyclic / AWS EC2

## Description
- The client hosted on Vercel is a web app that allows users to ask questions and get answers from the server.
- The server hosted on Cyclic, which is an Express app, makes request to the Flask server to get answers to questions.
- The Flask server hosted on AWS EC2 hosts the embedding model and makes calls to OpenAI API to generate answers to questions.
- The dataset is automatically generated and uploaded to Pinecone database by the dataset pipeline.
  
### Client - Vite App - Vercel
[Client server](client) is a web app that allows users to ask questions and get answers from the server.

### Server - Express App - Azure Web App
[Express server](server) get requests from the client and make calls to the Flask server to get answers to questions.

### Flask App - AWS EC2 
[Server](flaskServer) hosts the embedding model and make calls to OpenAI API to generate answers to questions.

### Dataset Pineline
[Dataset Pipeline](datasetPipeline) is pineline to generate dataset by srapping raw data from the University of South Florida website, processing the raw data to generate the final dataset, and uploading the dataset to Pinecone database.

## Environment Variables

Configure secrets via environment variables (do not hardcode keys in source code). Copy `.env.example` to `.env` and set the following:

- OPENAI_API_KEY
- PINECONE_API
- PINECONE_ENV (optional, default: `us-east-1`)
- PINECONE_INDEX (optional, default: `bullbot`)

Client build expects `VITE_SERVER` at build time (see `client/.env.example`).

## Deploy backend on Render (one-click)

Option A: Use the Render Blueprint in `render.yaml`:

1. Push this repo to GitHub (done).
2. Go to Render → New → Blueprint → select this repo.
3. Set secret env vars on the service:
	- `OPENAI_API_KEY`
	- `PINECONE_API`
4. Deploy. Render will expose a URL like `https://askrocky-backend.onrender.com`.

Option B: Manual web service
1. New Web Service → Connect repo.
2. Build: `pip install -r requirements.txt`
3. Start: `python api/index.py`
4. Add env vars as above; deploy.

Then set Vercel `VITE_SERVER` to `https://<your-render-url>/api/chat` and redeploy the client.

## Deploy backend on Railway

1. Add this repo in Railway and create a service from it.
2. Railway will detect the `Procfile` and run `web: python api/index.py`.
3. Set env vars: `OPENAI_API_KEY`, `PINECONE_API`, `PINECONE_ENV`, `PINECONE_INDEX`.
4. Deploy and copy the public URL.
5. Update Vercel `VITE_SERVER` to `https://<your-railway-url>/api/chat` and redeploy the client.