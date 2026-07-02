# -*- coding: utf-8 -*-
from math import ceil
from typing import Optional
from flask import jsonify, request
from flask_openapi3 import Tag
from pydantic import BaseModel, Field

from app.models import (
    db,
    Personagens,
    Character,
    CharacterAbility,
    CharacterSpellSlot,
    InventoryItem,
    ShopItem,
    LedgerEntry,
    Spell,
    ability_modifier,
    normalize_name,
)
from app.data_sync import export_backend_to_frontend_json, seed_backend_from_frontend_json
from app.schemas import (
    PersonagemSchema,
    PathCharacterId,
    QueryCharactersV2,
    CharacterWizardCreateSchema,
    CharacterPlayPatchSchema,
    SpellSlotPatchSchema,
    RewardSchema,
    ShopItemCreateSchema,
    ShopQuerySchema,
    PurchaseSchema,
    InventoryEquipSchema,
    InventoryAttuneSchema,
)


tag_health = Tag(name='Health', description='Health check')
tag_personagens = Tag(name='Personagens', description='Legacy character management')
tag_characters_v2 = Tag(name='CharactersV2', description='Grimmorium v2 character hub')
tag_shop_v2 = Tag(name='ShopV2', description='Shop and economy endpoints')
tag_spells = Tag(name='Spells', description='Spellbook endpoints and JSON sync')


class QueryCharactersLegacy(BaseModel):
    nome: Optional[str] = Field(None, description='Filtra por nome (contém)', min_length=1)
    classe: Optional[str] = Field(None, description='Filtra por classe (contém)', min_length=1)


class PathCharacterSlot(BaseModel):
    id: int = Field(..., description='ID do personagem')
    slot_level: int = Field(..., ge=1, le=9)


class PathCharacterItem(BaseModel):
    id: int = Field(..., description='ID do personagem')
    item_id: int = Field(..., description='ID do item no inventário')


def cp_to_coin_breakdown(total_cp: int):
    cp = max(total_cp, 0)
    pp, remainder = divmod(cp, 1000)
    gp, remainder = divmod(remainder, 100)
    ep, remainder = divmod(remainder, 50)
    sp, cp = divmod(remainder, 10)
    return {'cp': cp, 'sp': sp, 'ep': ep, 'gp': gp, 'pp': pp}


def apply_coin_cp(character: Character, amount_cp: int):
    coins = cp_to_coin_breakdown(amount_cp)
    character.cp = coins['cp']
    character.sp = coins['sp']
    character.ep = coins['ep']
    character.gp = coins['gp']
    character.pp = coins['pp']


def current_ac(character: Character):
    equipped_bonus = sum(item.grants_ac for item in character.inventory_items if item.is_equipped)
    return character.ac_base + equipped_bonus


def register_ledger(character_id: int, entry_type: str, amount_cp: int, description: str):
    db.session.add(
        LedgerEntry(
            character_id=character_id,
            entry_type=entry_type,
            amount_cp=amount_cp,
            description=description,
        )
    )


def init_api_routes(app):
    @app.get('/', summary='Root health endpoint', tags=[tag_health])
    def root_health():
        return jsonify({'status': 'success', 'message': 'Grimmorium backend is running'}), 200

    @app.get('/api/hello', summary='Test Endpoint', tags=[tag_health])
    def hello():
        return jsonify({'status': 'success', 'message': 'Hello from Flask API!'}), 200

    @app.get('/api/magias', summary='List spells from backend', tags=[tag_spells])
    def list_spells():
        try:
            search = request.args.get('search', '').strip()
            level_raw = request.args.get('nivel', '').strip()

            query = Spell.query
            if search:
                query = query.filter(Spell.nome.ilike(f'%{search}%'))

            if level_raw != '':
                level_value = int(level_raw)
                query = query.filter(Spell.nivel == level_value)

            rows = query.order_by(Spell.nivel.asc(), Spell.nome.asc()).all()
            return jsonify({'status': 'success', 'total': len(rows), 'magias': [row.to_dict() for row in rows]}), 200
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Query parameter nivel must be an integer'}), 400
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/sync/import-local-json', summary='Seed backend from local JSON files', tags=[tag_spells])
    def sync_import_local_json():
        try:
            result = seed_backend_from_frontend_json()
            export_info = export_backend_to_frontend_json()
            return jsonify({'status': 'success', 'imported': result, 'exported': export_info}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/sync/export-local-json', summary='Export backend state to local JSON files', tags=[tag_spells])
    def sync_export_local_json():
        try:
            result = export_backend_to_frontend_json()
            return jsonify({'status': 'success', 'exported': result}), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    # ==================== LEGADO MVP 1 ====================
    @app.get('/api/personagens', summary='List Characters (legacy)', tags=[tag_personagens])
    def listar_personagens(query: QueryCharactersLegacy):
        try:
            nome = query.nome.strip() if query.nome else ''
            classe = query.classe.strip() if query.classe else ''

            personagens_query = Personagens.query
            if nome:
                personagens_query = personagens_query.filter(Personagens.nome.ilike(f'%{nome}%'))
            if classe:
                personagens_query = personagens_query.filter(Personagens.classe.ilike(f'%{classe}%'))

            personagens = personagens_query.all()
            if not personagens:
                return jsonify({'status': 'error', 'message': 'No characters found'}), 404

            return jsonify({
                'status': 'success',
                'total': len(personagens),
                'personagens': [p.para_dicionario() for p in personagens],
            }), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/personagens', summary='Create Character (legacy)', tags=[tag_personagens])
    def create_character_legacy(body: PersonagemSchema):
        try:
            nome = normalize_name(body.nome)
            if not nome:
                return jsonify({'status': 'error', 'message': 'Name is required'}), 400

            existe = Personagens.query.filter_by(nome=nome).first()
            if existe:
                return jsonify({'status': 'error', 'message': 'Character already exists'}), 409

            novo_personagem = Personagens(nome=nome, classe=normalize_name(body.classe), nivel=body.nivel if body.nivel else 1)
            db.session.add(novo_personagem)
            db.session.commit()

            return jsonify({'status': 'success', 'personagem': novo_personagem.para_dicionario()}), 201
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    # ==================== V2 ROADMAP MASTERIZADO ====================
    @app.get('/api/v2/characters', summary='List characters v2', tags=[tag_characters_v2])
    def list_characters_v2(query: QueryCharactersV2):
        try:
            q = Character.query
            if query.name:
                q = q.filter(Character.name.ilike(f"%{query.name.strip()}%"))
            if query.campaign:
                q = q.filter(Character.campaign.ilike(f"%{query.campaign.strip()}%"))
            if query.character_class:
                q = q.filter(Character.character_class.ilike(f"%{query.character_class.strip()}%"))
            if query.min_level:
                q = q.filter(Character.level >= query.min_level)
            if query.max_level:
                q = q.filter(Character.level <= query.max_level)

            rows = q.order_by(Character.updated_at.desc()).all()
            return jsonify({'status': 'success', 'total': len(rows), 'characters': [row.to_dict() for row in rows]}), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.get('/api/v2/characters/<int:id>', summary='Get character v2', tags=[tag_characters_v2])
    def get_character_v2(path: PathCharacterId):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404
            return jsonify({'status': 'success', 'character': character.to_dict()}), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.delete('/api/v2/characters/<int:id>', summary='Delete character v2', tags=[tag_characters_v2])
    def delete_character_v2(path: PathCharacterId):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            snapshot = {'id': character.id, 'name': character.name}
            db.session.delete(character)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Character deleted', 'character': snapshot}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/characters/wizard', summary='Create character by wizard', tags=[tag_characters_v2])
    def create_character_wizard(body: CharacterWizardCreateSchema):
        try:
            name = normalize_name(body.name)
            if not name:
                return jsonify({'status': 'error', 'message': 'Character name is required'}), 400

            exists = Character.query.filter_by(name=name).first()
            if exists:
                return jsonify({'status': 'error', 'message': 'Character name already exists'}), 409

            hp_current = body.hp_current if body.hp_current is not None else body.hp_max
            hp_current = min(max(hp_current, 0), body.hp_max)

            character = Character(
                name=name,
                campaign=normalize_name(body.campaign) or None,
                level=body.level,
                race=normalize_name(body.race),
                subrace=normalize_name(body.subrace) or None,
                character_class=normalize_name(body.character_class),
                hit_die=body.hit_die,
                alignment=normalize_name(body.alignment) or None,
                background=normalize_name(body.background) or None,
                personality_traits=body.personality_traits,
                ideals=body.ideals,
                bonds=body.bonds,
                flaws=body.flaws,
                hp_current=hp_current,
                hp_max=body.hp_max,
                hp_temp=body.hp_temp,
                hit_dice_current=body.level,
                hit_dice_max=body.level,
                ac_base=body.ac_base,
                ac_current=body.ac_base,
                speed=body.speed,
                cp=body.coins_cp,
                sp=body.coins_sp,
                ep=body.coins_ep,
                gp=body.coins_gp,
                pp=body.coins_pp,
            )
            db.session.add(character)
            db.session.flush()

            abilities = body.abilities
            ability_row = CharacterAbility(
                character_id=character.id,
                str_base=abilities.str_base,
                dex_base=abilities.dex_base,
                con_base=abilities.con_base,
                int_base=abilities.int_base,
                wis_base=abilities.wis_base,
                cha_base=abilities.cha_base,
                str_racial=abilities.str_racial,
                dex_racial=abilities.dex_racial,
                con_racial=abilities.con_racial,
                int_racial=abilities.int_racial,
                wis_racial=abilities.wis_racial,
                cha_racial=abilities.cha_racial,
            )
            db.session.add(ability_row)

            for slot in body.spell_slots:
                if slot.used_slots > slot.max_slots:
                    return jsonify({'status': 'error', 'message': f'Used slots cannot exceed max at level {slot.slot_level}'}), 400
                db.session.add(
                    CharacterSpellSlot(
                        character_id=character.id,
                        slot_level=slot.slot_level,
                        max_slots=slot.max_slots,
                        used_slots=slot.used_slots,
                    )
                )

            attuned_count = 0
            for item in body.inventory:
                if item.is_attuned and item.requires_attunement:
                    attuned_count += 1
                db.session.add(
                    InventoryItem(
                        character_id=character.id,
                        name=item.name,
                        category=item.category,
                        quantity=item.quantity,
                        weight=item.weight,
                        price_gp=item.price_gp,
                        is_equipped=item.is_equipped,
                        grants_ac=item.grants_ac,
                        requires_attunement=item.requires_attunement,
                        is_attuned=item.is_attuned,
                        source=item.source,
                    )
                )

            if attuned_count > character.attunement_slots:
                return jsonify({'status': 'error', 'message': 'Attunement limit exceeded during character creation'}), 400

            character.ac_current = current_ac(character)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Character created from wizard flow', 'character': character.to_dict()}), 201
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.put('/api/v2/characters/<int:id>/play', summary='Patch play mode vitals', tags=[tag_characters_v2])
    def patch_play_mode(path: PathCharacterId, body: CharacterPlayPatchSchema):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            if body.hp_current is not None:
                character.hp_current = min(max(body.hp_current, 0), character.hp_max)
            if body.hp_temp is not None:
                character.hp_temp = max(body.hp_temp, 0)
            if body.hit_dice_current is not None:
                character.hit_dice_current = min(max(body.hit_dice_current, 0), character.hit_dice_max)
            if body.ac_base is not None:
                character.ac_base = body.ac_base
            if body.speed is not None:
                character.speed = body.speed

            character.ac_current = current_ac(character)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Play mode values updated', 'character': character.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.put('/api/v2/characters/<int:id>/spell-slots/<int:slot_level>', summary='Update spell slot usage', tags=[tag_characters_v2])
    def update_spell_slot(path: PathCharacterSlot, body: SpellSlotPatchSchema):
        try:
            slot = CharacterSpellSlot.query.filter_by(character_id=path.id, slot_level=path.slot_level).first()
            if not slot:
                return jsonify({'status': 'error', 'message': 'Spell slot row not found for this level'}), 404
            if body.used_slots > slot.max_slots:
                return jsonify({'status': 'error', 'message': 'Used slots cannot exceed max slots'}), 400

            slot.used_slots = body.used_slots
            db.session.commit()

            return jsonify({'status': 'success', 'slot': slot.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/characters/<int:id>/rest/short', summary='Apply short rest', tags=[tag_characters_v2])
    def short_rest(path: PathCharacterId):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            if character.hit_dice_current <= 0:
                return jsonify({'status': 'error', 'message': 'No hit dice available for short rest'}), 400

            con_mod = ability_modifier(character.abilities.con_total) if character.abilities else 0
            heal = max(1, ceil(character.hit_die / 2) + con_mod)
            character.hp_current = min(character.hp_current + heal, character.hp_max)
            character.hit_dice_current -= 1
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Short rest applied', 'healed': heal, 'character': character.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/characters/<int:id>/rest/long', summary='Apply long rest', tags=[tag_characters_v2])
    def long_rest(path: PathCharacterId):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            character.hp_current = character.hp_max
            character.hp_temp = 0
            recover_hit_dice = max(1, character.hit_dice_max // 2)
            character.hit_dice_current = min(character.hit_dice_current + recover_hit_dice, character.hit_dice_max)

            for slot in character.spell_slots:
                slot.used_slots = 0

            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Long rest applied', 'character': character.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.put('/api/v2/characters/<int:id>/inventory/<int:item_id>/equip', summary='Equip or unequip inventory item', tags=[tag_characters_v2])
    def update_item_equip(path: PathCharacterItem, body: InventoryEquipSchema):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            item = InventoryItem.query.filter_by(id=path.item_id, character_id=path.id).first()
            if not item:
                return jsonify({'status': 'error', 'message': 'Inventory item not found'}), 404

            item.is_equipped = body.is_equipped
            character.ac_current = current_ac(character)
            db.session.commit()
            return jsonify({'status': 'success', 'item': item.to_dict(), 'ac_current': character.ac_current}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.put('/api/v2/characters/<int:id>/inventory/<int:item_id>/attune', summary='Attune or unattune magic item', tags=[tag_characters_v2])
    def update_item_attune(path: PathCharacterItem, body: InventoryAttuneSchema):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            item = InventoryItem.query.filter_by(id=path.item_id, character_id=path.id).first()
            if not item:
                return jsonify({'status': 'error', 'message': 'Inventory item not found'}), 404
            if not item.requires_attunement and body.is_attuned:
                return jsonify({'status': 'error', 'message': 'This item does not require attunement'}), 400

            if body.is_attuned:
                used = character.attuned_count()
                if used >= character.attunement_slots and not item.is_attuned:
                    return jsonify({'status': 'error', 'message': 'Attunement slots limit reached'}), 400

            item.is_attuned = body.is_attuned
            db.session.commit()
            return jsonify({'status': 'success', 'item': item.to_dict(), 'attuned_count': character.attuned_count()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.get('/api/v2/shop/items', summary='List shop items', tags=[tag_shop_v2])
    def list_shop_items(query: ShopQuerySchema):
        try:
            q = ShopItem.query
            if query.search:
                q = q.filter(ShopItem.name.ilike(f"%{query.search.strip()}%"))
            if query.category:
                q = q.filter(ShopItem.category.ilike(f"%{query.category.strip()}%"))
            items = q.order_by(ShopItem.category.asc(), ShopItem.name.asc()).all()
            return jsonify({'status': 'success', 'total': len(items), 'items': [item.to_dict() for item in items]}), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/shop/items', summary='Create shop item', tags=[tag_shop_v2])
    def create_shop_item(body: ShopItemCreateSchema):
        try:
            name = normalize_name(body.name)
            if ShopItem.query.filter_by(name=name).first():
                return jsonify({'status': 'error', 'message': 'Shop item already exists'}), 409

            row = ShopItem(
                name=name,
                category=normalize_name(body.category),
                price_gp=body.price_gp,
                weight=body.weight,
                description=body.description,
            )
            db.session.add(row)
            db.session.commit()
            return jsonify({'status': 'success', 'item': row.to_dict()}), 201
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/characters/<int:id>/shop/purchase', summary='Purchase item with one click', tags=[tag_shop_v2])
    def purchase_item(path: PathCharacterId, body: PurchaseSchema):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            shop_item = ShopItem.query.get(body.shop_item_id)
            if not shop_item:
                return jsonify({'status': 'error', 'message': 'Shop item not found'}), 404

            quantity = max(body.quantity, 1)
            total_cost_cp = int(round(shop_item.price_gp * 100)) * quantity
            available_cp = character.coins_as_cp()
            if available_cp < total_cost_cp:
                return jsonify({'status': 'error', 'message': 'Insufficient funds'}), 400

            remaining_cp = available_cp - total_cost_cp
            apply_coin_cp(character, remaining_cp)

            item = InventoryItem.query.filter_by(character_id=character.id, name=shop_item.name, source='shop').first()
            if item:
                item.quantity += quantity
            else:
                item = InventoryItem(
                    character_id=character.id,
                    name=shop_item.name,
                    category=shop_item.category,
                    quantity=quantity,
                    weight=shop_item.weight,
                    price_gp=shop_item.price_gp,
                    source='shop',
                )
                db.session.add(item)

            register_ledger(
                character_id=character.id,
                entry_type='debit',
                amount_cp=total_cost_cp,
                description=f'Purchase: {shop_item.name} x{quantity}',
            )

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Purchase completed', 'character': character.to_dict(), 'item': item.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.post('/api/v2/characters/<int:id>/ledger/reward', summary='Add manual reward', tags=[tag_shop_v2])
    def add_reward(path: PathCharacterId, body: RewardSchema):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            reward_cp = int(round(body.amount_gp * 100))
            apply_coin_cp(character, character.coins_as_cp() + reward_cp)

            register_ledger(
                character_id=character.id,
                entry_type='credit',
                amount_cp=reward_cp,
                description=body.description,
            )

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Reward added', 'character': character.to_dict()}), 200
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    @app.get('/api/v2/characters/<int:id>/ledger', summary='List character ledger entries', tags=[tag_shop_v2])
    def list_ledger(path: PathCharacterId):
        try:
            character = Character.query.get(path.id)
            if not character:
                return jsonify({'status': 'error', 'message': 'Character not found'}), 404

            rows = LedgerEntry.query.filter_by(character_id=character.id).order_by(LedgerEntry.created_at.desc()).all()
            return jsonify({'status': 'success', 'total': len(rows), 'entries': [row.to_dict() for row in rows]}), 200
        except Exception as exc:
            return jsonify({'status': 'error', 'message': str(exc)}), 500
