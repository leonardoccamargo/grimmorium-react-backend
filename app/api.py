from flask import jsonify, request
from flask_openapi3 import APIBlueprint
from app.models import db, Personagens
from app.schemas import (
    PersonagemSchema,
    PersonagemResponseSchema,
    ErrorSchema
)

# Cria blueprint OpenAPI
api_bp = APIBlueprint('api', __name__, url_prefix='/api')

# Tags para organizar documentação
from flask_openapi3 import Tag
tag_health = Tag(name='Health', description='Health check endpoints')
tag_personagens = Tag(name='Personagens', description='Endpoints para gerenciar personagens')

# ========== HEALTH CHECK ==========
@api_bp.get(
    '/',
    summary='Health check',
    description='Verifica se a API está funcionando',
    tags=[tag_health]
)
def health_check():
    """Endpoint básico para verificar se a API está rodando"""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    }), 200

@api_bp.get(
    '/hello',
    summary='Endpoint de teste',
    description='Um simples endpoint de teste',
    tags=[tag_health]
)
def hello():
    """Endpoint de teste simples para desenvolvimento"""
    return jsonify({
        'status': 'success',
        'message': 'Hello from Flask API!'
    }), 200

# ========== PERSONAGENS CRUD ==========
@api_bp.get(
    '/personagens',
    summary='Listar todos os personagens',
    description='Retorna uma lista com todos os personagens cadastrados',
    tags=[tag_personagens]
)
def listar_personagens():
    """Endpoint GET para listar todos os personagens."""
    try:
        personagens = Personagens.query.all()
        return jsonify({
            'status': 'success',
            'total': len(personagens),
            'personagens': [p.para_dicionario() for p in personagens]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao listar personagens: {str(e)}'
        }), 500

@api_bp.get(
    '/personagens/<int:id>',
    summary='Obter personagem por ID',
    description='Retorna os dados de um personagem específico pelo ID',
    tags=[tag_personagens],
    responses={200: PersonagemResponseSchema, 404: ErrorSchema}
)
def obter_personagem(path):
    """Endpoint GET para obter um personagem específico pelo ID."""
    id = path['id']
    try:
        personagem = Personagens.query.get(id)
        if not personagem:
            return jsonify({
                'status': 'error',
                'message': 'Personagem não encontrado'
            }), 404
        return jsonify({
            'status': 'success',
            'personagem': personagem.para_dicionario()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter personagem: {str(e)}'
        }), 500

@api_bp.post(
    '/personagens',
    summary='Criar novo personagem',
    description='Cria um novo personagem com as informações fornecidas',
    tags=[tag_personagens]
)
def criar_personagem(body: PersonagemSchema):
    """Endpoint POST para criar um novo personagem."""
    try:
        if not body.nome.strip():
            return jsonify({
                'status': 'error',
                'message': 'Nome não pode estar vazio'
            }), 400

        existe = Personagens.query.filter_by(nome=body.nome).first()
        if existe:
            return jsonify({
                'status': 'error',
                'message': 'Já existe um personagem com este nome'
            }), 409

        novo_personagem = Personagens(
            nome=body.nome,
            classe=body.classe,
            nivel=body.nivel if body.nivel else 1
        )

        db.session.add(novo_personagem)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Personagem criado com sucesso',
            'personagem': novo_personagem.para_dicionario()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao criar personagem: {str(e)}'
        }), 500

@api_bp.put(
    '/personagens/<int:id>',
    summary='Atualizar personagem',
    description='Atualiza um personagem existente pelo ID',
    tags=[tag_personagens]
)
def atualizar_personagem(path, body: PersonagemSchema):
    """Endpoint PUT para atualizar um personagem existente."""
    id = path['id']
    try:
        nome = body.nome.strip()
        classe = body.classe.strip()
        nivel = body.nivel

        if not nome:
            return jsonify({'status': 'error', 'message': 'Nome não pode estar vazio'}), 400
        if not classe:
            return jsonify({'status': 'error', 'message': 'Classe não pode estar vazia'}), 400
        if nivel is None or not isinstance(nivel, int) or nivel < 1:
            return jsonify({'status': 'error', 'message': 'Nível deve ser um número inteiro maior que 0'}), 400

        personagem = Personagens.query.get(id)
        if not personagem:
            return jsonify({
                'status': 'error',
                'message': 'Personagem não encontrado'
            }), 404

        if nome != personagem.nome:
            existe = Personagens.query.filter_by(nome=nome).first()
            if existe:
                return jsonify({
                    'status': 'error',
                    'message': 'Já existe um personagem com este nome'
                }), 409

        personagem.nome = nome
        personagem.classe = classe
        personagem.nivel = nivel
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Personagem atualizado com sucesso',
            'personagem': personagem.para_dicionario()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar personagem: {str(e)}'
        }), 500

@api_bp.delete(
    '/personagens/<int:id>',
    summary='Deletar personagem',
    description='Remove um personagem existente pelo ID',
    tags=[tag_personagens]
)
def deletar_personagem(path):
    """Endpoint DELETE para remover um personagem."""
    id = path['id']
    try:
        personagem = Personagens.query.get(id)
        if not personagem:
            return jsonify({
                'status': 'error',
                'message': 'Personagem não encontrado'
            }), 404

        db.session.delete(personagem)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Personagem deletado com sucesso'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao deletar personagem: {str(e)}'
        }), 500

# ========== BUSCA E ESTATÍSTICAS ==========
@api_bp.get(
    '/buscar',
    summary='Buscar personagens por nome',
    description='Busca personagens cujo nome contenha o termo fornecido (case-insensitive)',
    tags=[tag_personagens]
)
def buscar_personagens():
    """Busca personagens por nome."""
    try:
        termo = request.args.get('nome', '').strip()
        if not termo:
            return jsonify({
                'status': 'error',
                'message': 'Forneça um termo de busca no parâmetro "nome"'
            }), 400

        personagens = Personagens.query.filter(
            Personagens.nome.ilike(f'%{termo}%')
        ).all()

        return jsonify({
            'status': 'success',
            'total': len(personagens),
            'termo_busca': termo,
            'personagens': [p.para_dicionario() for p in personagens]
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao buscar personagens: {str(e)}'
        }), 500

@api_bp.get(
    '/classe',
    summary='Filtrar personagens por classe',
    description='Retorna todos os personagens de uma classe específica',
    tags=[tag_personagens]
)
def filtrar_por_classe():
    """Filtra personagens por classe."""
    try:
        classe = request.args.get('nome', '').strip()
        if not classe:
            return jsonify({
                'status': 'error',
                'message': 'Forneça uma classe no parâmetro "nome"'
            }), 400

        personagens = Personagens.query.filter(
            Personagens.classe.ilike(f'%{classe}%')
        ).all()

        return jsonify({
            'status': 'success',
            'total': len(personagens),
            'classe_filtrada': classe,
            'personagens': [p.para_dicionario() for p in personagens]
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao filtrar por classe: {str(e)}'
        }), 500

@api_bp.get(
    '/estatisticas',
    summary='Obter estatísticas dos personagens',
    description='Retorna informações estatísticas sobre o roster de personagens',
    tags=[tag_personagens]
)
def obter_estatisticas():
    """Endpoint GET para obter estatísticas gerais dos personagens."""
    try:
        personagens = Personagens.query.all()

        if not personagens:
            return jsonify({
                'status': 'success',
                'total_personagens': 0,
                'nivel_minimo': 0,
                'nivel_maximo': 0,
                'nivel_medio': 0,
                'classes': []
            }), 200

        total = len(personagens)
        niveis = [p.nivel for p in personagens]
        nivel_minimo = min(niveis)
        nivel_maximo = max(niveis)
        nivel_medio = sum(niveis) / total

        classes = {}
        for p in personagens:
            classe = p.classe
            classes[classe] = classes.get(classe, 0) + 1

        return jsonify({
            'status': 'success',
            'total_personagens': total,
            'nivel_minimo': nivel_minimo,
            'nivel_maximo': nivel_maximo,
            'nivel_medio': round(nivel_medio, 2),
            'classes': classes
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter estatísticas: {str(e)}'
        }), 500
