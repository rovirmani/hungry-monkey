# Hungry Monkey 🍽️

A restaurant discovery and recommendation application that helps users find their next favorite dining spot.

## 🚀 Features

- Restaurant discovery and search
- User authentication with Clerk
- Restaurant recommendations
- Supabase database integration
- Modern React frontend with TypeScript
- FastAPI backend with Python

## 📋 Prerequisites

- Python 3.9+ (3.9.18 recommended)
- Node.js 16+
- npm (Node package manager)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hungry-monkey.git
   cd hungry-monkey
   ```

2. **Install backend dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## 🔑 Environment Setup

The project uses two separate `.env` files. Example files (`.env.example`) are provided for both:

1. **Root `.env` (Backend)**
   ```bash
   # Copy the example env file
   cp .env.example .env
   # Then edit .env with your actual values
   ```

   Required variables:
   ```plaintext
   # API Keys
   YELP_API_KEY=your_yelp_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # API Base URLs
   YELP_API_BASE_URL=https://api.yelp.com/v3
   ANTHROPIC_API_BASE_URL=https://api.anthropic.com

   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key

   # VAPI Configuration
   VAPI_API_KEY=your_vapi_key
   VAPI_ASSISTANT_ID=your_vapi_assistant_id
   VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id

   # Google Custom Search
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

   # Clerk Configuration
   CLERK_SECRET_KEY=your_clerk_secret_key
   CLERK_JWT_ISSUER=your_clerk_jwt_issuer
   ```

2. **Frontend `.env`**
   ```bash
   # Copy the example env file
   cp frontend/.env.example frontend/.env
   # Then edit .env with your actual values
   ```

   Required variables:
   ```plaintext
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   ```

See the `.env.example` files for additional configuration variables.

## 🚀 Running the Application

### Development Mode (Both Frontend and Backend)
```bash
npm run dev
```

### Backend Only
```bash
npm run dev:backend
```

### Frontend Only
```bash
npm run dev:frontend
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
hungry-monkey/
├── app/                    # Backend application
│   ├── routers/           # API route handlers
│   ├── auth/              # Authentication logic
│   └── main.py           # FastAPI application entry point
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layers
│   │   └── pages/        # Page components
│   └── package.json      # Node.js dependencies and scripts
│   │   
│   └── .env              # Frontend Environment variables
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables (global)
```

## 🧪 Testing

```bash
# bro fr thought we were gonna run tests
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.