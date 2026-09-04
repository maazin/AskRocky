# AskRocky

> AskRocky is an independent student project. It is not affiliated with,
> endorsed by, or an official service of the University of South Florida.
> Answers are AI-generated and can be wrong -- always confirm against the
> linked usf.edu pages.

## Tech Stack
- Vite.js / Node.js / Python / langchain / 
- Database: Pinecone
- Embedding Model: [BAAI/bge-small-en](https://huggingface.co/BAAI/bge-small-en)
- Large Language Model: OpenAI API
- Deployment: Vercel / Cyclic

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

## Local development

### Prereqs
- **Python 3.11** — required, not optional. The pinned dependency set
  (`sentence-transformers==2.2.2`, `transformers==4.26.0`,
  `huggingface-hub==0.12.0`) does not install on 3.13.
- Node.js 18+

### Setup
1. Python env and deps

   ```bash
   python3.11 -m venv .venv311
   ./.venv311/bin/pip install -r requirements.txt
   ```

2. Node deps

   ```bash
   cd client && npm install
   cd ../server && npm install   # optional Express proxy
   ```

3. Environment variables — copy `.env.example` to `.env` and fill in:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX` — the live index is named `bullbot`. Renaming it in the
     Pinecone console would orphan the 3,575 indexed vectors, so it keeps the
     old name even though the project is now AskRocky.
   - `PINECONE_HOST` — the serverless host URL (optional; the client can
     resolve it, but setting it skips a lookup on boot)

### Start

```bash
./run_local.sh
```

- Frontend: http://localhost:5173
- Backend:  http://localhost:8000 (readiness at `/health`)

Both ports are configurable, which matters if something else on your machine
already holds 8000:

```bash
PORT=8010 CLIENT_PORT=5174 ./run_local.sh
```

`run_local.sh` refuses to start on an occupied port and waits for `/health`
before declaring success, so a backend that fails to boot is reported instead
of silently ignored. Use `./start.sh` for the same thing detached, with output
in `flask.log` and `vite.log`.

To run the pieces separately:

```bash
PORT=8000 ./.venv311/bin/python api/index.py
```

```bash
cd client && VITE_SERVER=http://localhost:8000/api/chat npm run dev
```

### First-request behaviour

The embedding model (~130 MB) downloads and loads in a background thread at
startup. Until it finishes, `/health` reports `"ready": false` and the API
answers from the LLM alone with no USF sources. The client shows this as
"Loading knowledge base…" in the header. Warm-up usually takes 30-60s on a cold
cache.

## Deployment

The frontend is a static Vite build; the backend is a Flask app served by
gunicorn.

- **Frontend (Vercel):** builds `client/` per `vercel.json`. Set `VITE_SERVER`
  in the Vercel project's environment variables to the deployed backend's
  `/api/chat` URL, or the built client will have no backend to call.
- **Backend (Render):** `render.yaml` is a working blueprint — Python 3.11,
  gunicorn, health check on `/health`. Set `OPENAI_API_KEY`, `PINECONE_API_KEY`
  and `PINECONE_HOST` as secrets in the dashboard.
- **Heroku / Railway:** use the `Procfile`.

Run one worker with several threads (as the Procfile and blueprint do). Each
worker loads its own copy of the embedding model, so extra workers multiply
memory rather than throughput.

### Railway

1. Add this repo in Railway and create a service from it.
2. Railway detects the `Procfile` and runs the gunicorn entry from it.
3. Set env vars: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_HOST`,
   `PINECONE_ENVIRONMENT`, `PINECONE_INDEX`.
4. Deploy and copy the public URL.
5. Update Vercel `VITE_SERVER` to `https://<your-railway-url>/api/chat` and
   redeploy the client.
