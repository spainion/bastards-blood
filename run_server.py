#!/usr/bin/env python3
"""Script to run the RPG API server."""
import uvicorn
from api.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.api_title} v{settings.api_version}")
    print(f"Server running on http://{settings.host}:{settings.port}")
    print(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"Alternative Docs: http://{settings.host}:{settings.port}/redoc")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
