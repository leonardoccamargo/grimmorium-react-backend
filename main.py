# Entry point for the development server.
import os

from app import create_app

if __name__ == '__main__':
    app = create_app()

    # Expose the API on all interfaces for local development.
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
        host='0.0.0.0',
        port=5000,
    )
