import express from 'express'
import * as dotenv from 'dotenv'
import cors from 'cors'
import axios from 'axios'
dotenv.config()

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

    const response = await axios.post('http://localhost:8000/prediction', {
      input: prompt,
    });

    res.status(200).send({
      bot: response.data
    });

  } catch (error) {
    console.error(error)
    res.status(500).send('Something went wrong!');
  }
})

app.listen(3000, () => console.log('AI server started on http://localhost:3000'))