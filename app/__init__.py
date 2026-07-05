"""Flask application factory for the Grimmorium backend."""

from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS
from flask import request
from app.models import db
from app.data_sync import seed_backend_from_frontend_json, export_backend_to_frontend_json
import os

def create_app():
    """Create and configure the Flask application."""

    # Resolve the repository root so OpenAPI can locate shared assets.
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
    root_path = os.path.dirname(backend_dir)  # raiz do projeto

    # API metadata shown in Swagger/OpenAPI.
    info = Info(
        title='Grimmorium API',
        version='2.0.0',
        description='API para gerenciamento de fichas D&D 5e (wizard, play mode e economia)'
    )

    # Build the OpenAPI-enabled Flask app.
    app = OpenAPI(
        __name__,
        info=info,
        template_folder=os.path.join(root_path, 'frontend'),
        static_folder=os.path.join(root_path, 'frontend'),
        static_url_path='/'
    )

    # Allow the React frontend to reach the API during development.
    CORS(
        app,
        resources={r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False,
        }}
    )

    # Keep the documented server list explicit for local development.
    app.api_doc['servers'] = [
        {"url": "http://127.0.0.1:5000", "description": "Development server"}
    ]

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grimmorium.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Bootstrap database tables and seed/export the local JSON snapshots.
    with app.app_context():
        db.create_all()
        seed_backend_from_frontend_json()
        export_backend_to_frontend_json()

    # Order Swagger actions to keep the docs readable.
    from flask_openapi3_swagger.templates import swagger_html_string
    custom_swagger = swagger_html_string.replace(
        '...swagger_config\n        })',
        '...swagger_config,\n        operationsSorter: function(a, b) {'
        '\n            var order = {get: 1, post: 2, put: 3, delete: 4};'
        '\n            return (order[a.get("method")] || 5) - (order[b.get("method")] || 5);'
        '\n        }\n        })'
    )
    app.config['SWAGGER_HTML_STRING'] = custom_swagger

    # Register API routes.
    from app.api_routes import init_api_routes
    init_api_routes(app)

    @app.after_request
    def sync_json_after_mutation(response):
        # Persist successful data mutations back to the frontend JSON files.
        should_sync = (
            request.path.startswith('/api/')
            and request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}
            and response.status_code < 400
        )

        if should_sync:
            try:
                export_backend_to_frontend_json()
            except Exception as exc:
                app.logger.warning('Failed to sync local JSON after mutation: %s', exc)

        return response

    # Generate the OpenAPI specification after route registration.
    app.generate_spec_json()

    return app
