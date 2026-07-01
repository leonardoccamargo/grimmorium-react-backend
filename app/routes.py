# -*- coding: utf-8 -*-
from flask import jsonify, request
from flask_openapi3 import Tag
from app.models import db, Personagens
from app.schemas import PersonagemSchema, PersonagemResponseSchema, PersonagensListSchema, PersonagemSingleSchema, PersonagemCreateSchema, ErrorSchema

tag_health = Tag(name='Health', description='Health check')
tag_personagens = Tag(name='Personagens', description='Character management')

def register_routes(app):
    @app.get('/', summary='Health check', tags=[tag_health])
    def index():
        return jsonify({'status': 'success', 'message': 'API is running'}), 200

    @app.get('/api/hello', summary='Test endpoint', tags=[tag_health])
    def hello():
        return jsonify({'status': 'success', 'message': 'Hello from Flask API!'}), 200

    @app.get('/api/personagens', summary='List all characters', tags=[tag_personagens])
    def listar_personagens():
        try:
            personagens = Personagens.query.all()
            return jsonify({'status': 'success', 'total': len(personagens), 'personagens': [p.para_dicionario() for p in personagens]}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.get('/api/personagens/<int:id>', summary='Get character by ID', tags=[tag_personagens])
    def obter_personagem(id):
        try:
            personagem = Personagens.query.get(id)
            if not personagem:
                return jsonify({'status': 'error', 'message': 'Not found'}), 404
            return jsonify({'status': 'success', 'personagem': personagem.para_dicionario()}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.post('/api/personagens', summary='Create character', tags=[tag_personagens])
    def criar_personagem(body: PersonagemSchema):
        try:
            if not body.nome.strip():
                return jsonify({'status': 'error', 'message': 'Name required'}), 400
            existe = Personagens.query.filter_by(nome=body.nome).first()
            if existe:
                return jsonify({'status': 'error', 'message': 'Already exists'}), 409
            novo_personagem = Personagens(nome=body.nome, classe=body.classe, nivel=body.nivel if body.nivel else 1)
            db.session.add(novo_personagem)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Created', 'personagem': novo_personagem.para_dicionario()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.put('/api/personagens/<int:id>', summary='Update character', tags=[tag_personagens])
    def atualizar_personagem(id, body: PersonagemSchema):
        try:
            personagem = Personagens.query.get(id)
            if not personagem:
                return jsonify({'status': 'error', 'message': 'Not found'}), 404
            personagem.nome = body.nome.strip()
            personagem.classe = body.classe.strip()
            personagem.nivel = body.nivel if body.nivel else 1
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Updated', 'personagem': personagem.para_dicionario()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.delete('/api/personagens/<int:id>', summary='Delete character', tags=[tag_personagens])
    def deletar_personagem(id):
        try:
            personagem = Personagens.query.get(id)
            if not personagem:
                return jsonify({'status': 'error', 'message': 'Not found'}), 404
            db.session.delete(personagem)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.get('/api/buscar', summary='Search characters by name', tags=[tag_personagens])
    def buscar_personagens():
        try:
            termo = request.args.get('nome', '').strip()
            if not termo:
                return jsonify({'status': 'error', 'message': 'Name parameter required'}), 400
            personagens = Personagens.query.filter(Personagens.nome.ilike(f'%{termo}%')).all()
            return jsonify({'status': 'success', 'total': len(personagens), 'termo_busca': termo, 'personagens': [p.para_dicionario() for p in personagens]}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.get('/api/classe', summary='Filter by class', tags=[tag_personagens])
    def filtrar_por_classe():
        try:
            classe = request.args.get('nome', '').strip()
            if not classe:
                return jsonify({'status': 'error', 'message': 'Class parameter required'}), 400
            personagens = Personagens.query.filter(Personagens.classe.ilike(f'%{classe}%')).all()
            return jsonify({'status': 'success', 'total': len(personagens), 'classe_filtrada': classe, 'personagens': [p.para_dicionario() for p in personagens]}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.get('/api/estatisticas', summary='Get statistics', tags=[tag_personagens])
    def obter_estatisticas():
        try:
            personagens = Personagens.query.all()
            if not personagens:
                return jsonify({'status': 'success', 'total_personagens': 0, 'nivel_minimo': 0, 'nivel_maximo': 0, 'nivel_medio': 0, 'classes': []}), 200
            total = len(personagens)
            niveis = [p.nivel for p in personagens]
            classes = {}
            for p in personagens:
                classes[p.classe] = classes.get(p.classe, 0) + 1
            return jsonify({'status': 'success', 'total_personagens': total, 'nivel_minimo': min(niveis), 'nivel_maximo': max(niveis), 'nivel_medio': round(sum(niveis) / total, 2), 'classes': classes}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
