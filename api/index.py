from app.main import app

# This is the handler that Vercel will use
def handler(request):
    return app

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
