# Importações necessárias para configurar a aplicação Flask
from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS
from app.models import db
import os

def create_app():
    """
    Factory function para criar a aplicação Flask.
    Usa o padrão Application Factory para melhor organização e testabilidade.
    Configura OpenAPI, CORS, banco de dados e registra as rotas.
    """

    # Calcula os caminhos corretos para templates e static files
    # Como estamos em backend/app/__init__.py, precisamos subir dois níveis para chegar na raiz
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
    root_path = os.path.dirname(backend_dir)  # raiz do projeto

    info = Info(
        title='Grimmorium API',
        version='2.0.0',
        description='API para gerenciamento de fichas D&D 5e (wizard, play mode e economia)'
    )

    # Cria a aplicação usando OpenAPI (que estende Flask com documentação automática)
    app = OpenAPI(
        __name__,  # Nome do módulo atual
        info=info,
        template_folder=os.path.join(root_path, 'frontend'),  # Pasta de templates (HTML)
        static_folder=os.path.join(root_path, 'frontend'),    # Pasta de arquivos estáticos (CSS, JS)
        static_url_path='/'  # URL para acessar arquivos estáticos
    )

    # ✅ CONFIGURAÇÃO CORS - Permite que o frontend (em outra porta/origem) faça requisições
    CORS(app,
         resources={r"/api/*": {  # Aplica apenas para rotas que começam com /api/
             "origins": ["*"],  # Permite qualquer origem (em produção, especifique o domínio do frontend)
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Métodos HTTP permitidos
             "allow_headers": ["Content-Type"],  # Headers permitidos
             "supports_credentials": False  # Não usa cookies/autenticação
         }}
    )

    # Configura informações adicionais da documentação OpenAPI/Swagger
    app.api_doc['servers'] = [  # Lista de servidores onde a API roda
        {"url": "http://127.0.0.1:5000", "description": "Development server"}
    ]

    # Configuração do banco de dados SQLite dedicado ao Grimmorium v2
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grimmorium.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desabilita tracking (melhor performance)

    # Inicializa o SQLAlchemy com a aplicação Flask
    db.init_app(app)

    # Cria todas as tabelas do banco de dados dentro do contexto da aplicação
    with app.app_context():
        db.create_all()  # Cria tabelas baseadas nos modelos definidos

    # Customiza o HTML do Swagger UI para ordenar rotas: GET → POST → PUT → DELETE
    from flask_openapi3_swagger.templates import swagger_html_string
    custom_swagger = swagger_html_string.replace(
        '...swagger_config\n        })',
        '...swagger_config,\n        operationsSorter: function(a, b) {'
        '\n            var order = {get: 1, post: 2, put: 3, delete: 4};'
        '\n            return (order[a.get("method")] || 5) - (order[b.get("method")] || 5);'
        '\n        }\n        })'
    )
    app.config['SWAGGER_HTML_STRING'] = custom_swagger

    # Importa e registra todas as rotas da API
    from app.api_routes import init_api_routes
    init_api_routes(app)

    # Gera o OpenAPI JSON com os caminhos registrados via decorators
    app.generate_spec_json()

    # Retorna a aplicação configurada e pronta para uso
    return app
