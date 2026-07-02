import json
import os
import re
from typing import Any

from app.models import Character, CharacterAbility, CharacterSpellSlot, InventoryItem, Personagens, Spell, db

HIT_DIE_BY_CLASS = {
    "barbaro": 12,
    "guerreiro": 10,
    "paladino": 10,
    "patrulheiro": 10,
    "artifice": 8,
    "artificie": 8,
    "bardo": 8,
    "clerigo": 8,
    "druida": 8,
    "monge": 8,
    "ladino": 8,
    "bruxo": 8,
    "mago": 6,
    "feiticeiro": 6,
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _slugify(value: str) -> str:
    cleaned = _normalize_text(value).lower()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned or "sem-nome"


def _class_key(value: str) -> str:
    text = _normalize_text(value).lower()
    replacements = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _hit_die_for_class(class_name: str) -> int:
    return HIT_DIE_BY_CLASS.get(_class_key(class_name), 8)


def _frontend_public_dir() -> str:
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    return os.path.join(project_root, "grimmorium-react-main", "public")


def _safe_read_json(file_path: str):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, list) else []


def _safe_write_json(file_path: str, payload) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _parse_hp(hp_text: str) -> tuple[int, int]:
    parts = str(hp_text or "").split("/")
    if len(parts) != 2:
        return (10, 10)
    try:
        current = max(0, int(parts[0]))
        max_hp = max(1, int(parts[1]))
        return (min(current, max_hp), max_hp)
    except ValueError:
        return (10, 10)


def _spell_slots_from_front(row: dict) -> tuple[int, int, int]:
    slot_map = row.get("slots_magia") or {}
    return (
        int(slot_map.get("nivel1") or 0),
        int(slot_map.get("nivel2") or 0),
        int(slot_map.get("nivel3") or 0),
    )


def _seed_legacy_characters(personagens_data: list[dict]) -> int:
    if Personagens.query.count() > 0:
        return 0

    inserted = 0
    seen_names = set()
    for row in personagens_data:
        nome = _normalize_text(row.get("nome"))
        if not nome:
            continue
        normalized_name = nome.lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)

        db.session.add(
            Personagens(
                nome=nome,
                classe=_normalize_text(row.get("classe")) or "Aventureiro",
                nivel=max(1, int(row.get("nivel") or 1)),
            )
        )
        inserted += 1

    return inserted


def _seed_v2_characters(personagens_data: list[dict]) -> int:
    if Character.query.count() > 0:
        return 0

    inserted = 0
    seen_names = set()

    for row in personagens_data:
        name = _normalize_text(row.get("nome"))
        if not name:
            continue
        normalized_name = name.lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)

        level = max(1, int(row.get("nivel") or 1))
        character_class = _normalize_text(row.get("classe")) or "Aventureiro"
        ac_base = max(1, int(row.get("ca") or 10))
        hp_current, hp_max = _parse_hp(row.get("hp"))
        slot_1, slot_2, slot_3 = _spell_slots_from_front(row)

        character = Character(
            name=name,
            campaign="MVP 2",
            level=level,
            race="Humano",
            subrace=None,
            character_class=character_class,
            hit_die=_hit_die_for_class(character_class),
            alignment=None,
            background="Aventureiro",
            personality_traits="",
            ideals="",
            bonds="",
            flaws="",
            hp_current=hp_current,
            hp_max=hp_max,
            hp_temp=0,
            hit_dice_current=level,
            hit_dice_max=level,
            ac_base=ac_base,
            ac_current=ac_base,
            speed=30,
        )
        db.session.add(character)
        db.session.flush()

        db.session.add(
            CharacterAbility(
                character_id=character.id,
                str_base=10,
                dex_base=10,
                con_base=10,
                int_base=10,
                wis_base=10,
                cha_base=10,
            )
        )

        db.session.add(CharacterSpellSlot(character_id=character.id, slot_level=1, max_slots=slot_1, used_slots=0))
        db.session.add(CharacterSpellSlot(character_id=character.id, slot_level=2, max_slots=slot_2, used_slots=0))
        db.session.add(CharacterSpellSlot(character_id=character.id, slot_level=3, max_slots=slot_3, used_slots=0))

        for item_name in row.get("consumiveis") or []:
            item_label = _normalize_text(item_name)
            if not item_label:
                continue
            db.session.add(
                InventoryItem(
                    character_id=character.id,
                    name=item_label,
                    category="Consumivel",
                    quantity=1,
                    weight=0.0,
                    price_gp=0.0,
                    source="seed",
                )
            )

        inserted += 1

    return inserted


def _seed_spells(magias_data: list[dict]) -> int:
    if Spell.query.count() > 0:
        return 0

    inserted = 0
    seen_indexes = set()

    for row in magias_data:
        nome = _normalize_text(row.get("nome"))
        if not nome:
            continue
        spell_index = _slugify(nome)
        if spell_index in seen_indexes:
            continue
        seen_indexes.add(spell_index)

        db.session.add(
            Spell(
                spell_index=spell_index,
                nome=nome,
                nivel=int(row.get("nivel") or 0),
                escola=_normalize_text(row.get("escola")),
                classes_json=json.dumps(row.get("classes") or [], ensure_ascii=False),
                tempo=_normalize_text(row.get("tempo")),
                alcance=_normalize_text(row.get("alcance")),
                componentes=_normalize_text(row.get("componentes")),
                comp_v=bool(row.get("comp_v")),
                comp_s=bool(row.get("comp_s")),
                comp_m=bool(row.get("comp_m")),
                material=_normalize_text(row.get("material")),
                duracao=_normalize_text(row.get("duracao")),
                ritual=bool(row.get("ritual")),
                concentracao=bool(row.get("concentracao")),
                descricao=_normalize_text(row.get("descricao")),
            )
        )
        inserted += 1

    return inserted


def seed_backend_from_frontend_json() -> dict:
    public_dir = _frontend_public_dir()
    personagens_path = os.path.join(public_dir, "personagens.json")
    magias_path = os.path.join(public_dir, "magias.json")

    personagens_data = _safe_read_json(personagens_path)
    magias_data = _safe_read_json(magias_path)

    inserted_legacy = _seed_legacy_characters(personagens_data)
    inserted_v2 = _seed_v2_characters(personagens_data)
    inserted_spells = _seed_spells(magias_data)

    if inserted_legacy or inserted_v2 or inserted_spells:
        db.session.commit()

    return {
        "legacy_characters": inserted_legacy,
        "v2_characters": inserted_v2,
        "spells": inserted_spells,
    }


def export_backend_to_frontend_json() -> dict:
    public_dir = _frontend_public_dir()
    personagens_path = os.path.join(public_dir, "personagens.json")
    magias_path = os.path.join(public_dir, "magias.json")

    characters_payload = []
    characters = Character.query.order_by(Character.id.asc()).all()
    for character in characters:
        slots_map = {slot.slot_level: slot.max_slots for slot in character.spell_slots}
        characters_payload.append(
            {
                "id": character.id,
                "nome": character.name,
                "classe": character.character_class,
                "nivel": character.level,
                "hp": f"{character.hp_current}/{character.hp_max}",
                "mana": "0/0",
                "ca": character.ac_current,
                "slots_magia": {
                    "nivel1": int(slots_map.get(1, 0)),
                    "nivel2": int(slots_map.get(2, 0)),
                    "nivel3": int(slots_map.get(3, 0)),
                },
                "consumiveis": [item.name for item in sorted(character.inventory_items, key=lambda row: row.id)],
            }
        )

    spells_payload = [row.to_dict() for row in Spell.query.order_by(Spell.nivel.asc(), Spell.nome.asc()).all()]

    _safe_write_json(personagens_path, characters_payload)
    _safe_write_json(magias_path, spells_payload)

    return {
        "characters_exported": len(characters_payload),
        "spells_exported": len(spells_payload),
    }
