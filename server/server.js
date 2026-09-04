import express from 'express'
import * as dotenv from 'dotenv'
import cors from 'cors'
import axios from 'axios'
dotenv.config()

// Configurable so this works in deployment, not just against a local Flask on 8000.
const PORT = process.env.PORT || 3000
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:8000/api/chat'

const app = express()
app.use(cors())
app.use(express.json())

app.get('/', async (req, res) => {
  res.status(200).send({
    message: 'Hello from Hieu!'
  })
})

app.post('/', async (req, res) => {
  try {
    const prompt = req.body.prompt;

    // Proxy to Python API (api/index.py) unified chat endpoint
    const response = await axios.post(FLASK_API_URL, {
      prompt,
    });

    res.status(200).send(response.data);

  } catch (error) {
    console.error(error)
    res.status(500).send('Something went wrong!');
  }
})

app.listen(PORT, () => console.log(`AI server started on http://localhost:${PORT}`))