import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/')
        setMessage(response.data.message)
      } catch (error) {
        console.error('Error fetching data:', error)
        setMessage('Error connecting to backend')
      }
    }
    fetchData()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-3xl mx-auto px-4">
        <div className="space-y-8">
          <h1 className="text-4xl font-bold text-center">FastAPI + React App</h1>
          <div className="p-6 bg-white rounded-md shadow-md w-full">
            <p className="text-lg">{message}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
