from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def proficiency_by_level(level: int) -> int:
    if level <= 4:
        return 2
    if level <= 8:
        return 3
    if level <= 12:
        return 4
    if level <= 16:
        return 5
    return 6


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def normalize_name(value: str) -> str:
    return (value or '').strip()


class Personagens(db.Model):
    """Modelo legado mantido para compatibilidade com endpoints do 1o MVP."""

    __tablename__ = 'personagens'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True)
    classe = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.Integer, nullable=False, default=1)

    def para_dicionario(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'classe': self.classe,
            'nivel': self.nivel,
        }


class Character(db.Model):
    """Modelo principal v2 para suportar wizard, play mode e economia."""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    campaign = db.Column(db.String(120), nullable=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    race = db.Column(db.String(60), nullable=False)
    subrace = db.Column(db.String(60), nullable=True)
    character_class = db.Column(db.String(60), nullable=False)
    hit_die = db.Column(db.Integer, nullable=False, default=8)
    alignment = db.Column(db.String(32), nullable=True)
    background = db.Column(db.String(80), nullable=True)
    personality_traits = db.Column(db.Text, nullable=True)
    ideals = db.Column(db.Text, nullable=True)
    bonds = db.Column(db.Text, nullable=True)
    flaws = db.Column(db.Text, nullable=True)

    hp_current = db.Column(db.Integer, nullable=False, default=10)
    hp_max = db.Column(db.Integer, nullable=False, default=10)
    hp_temp = db.Column(db.Integer, nullable=False, default=0)
    hit_dice_current = db.Column(db.Integer, nullable=False, default=1)
    hit_dice_max = db.Column(db.Integer, nullable=False, default=1)
    ac_base = db.Column(db.Integer, nullable=False, default=10)
    ac_current = db.Column(db.Integer, nullable=False, default=10)
    speed = db.Column(db.Integer, nullable=False, default=30)

    cp = db.Column(db.Integer, nullable=False, default=0)
    sp = db.Column(db.Integer, nullable=False, default=0)
    ep = db.Column(db.Integer, nullable=False, default=0)
    gp = db.Column(db.Integer, nullable=False, default=0)
    pp = db.Column(db.Integer, nullable=False, default=0)

    attunement_slots = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    abilities = db.relationship('CharacterAbility', backref='character', uselist=False, cascade='all, delete-orphan')
    spell_slots = db.relationship('CharacterSpellSlot', backref='character', cascade='all, delete-orphan')
    inventory_items = db.relationship('InventoryItem', backref='character', cascade='all, delete-orphan')
    ledger_entries = db.relationship('LedgerEntry', backref='character', cascade='all, delete-orphan')

    def proficiency_bonus(self):
        return proficiency_by_level(self.level)

    def coins_as_cp(self) -> int:
        return self.cp + (self.sp * 10) + (self.ep * 50) + (self.gp * 100) + (self.pp * 1000)

    def encumbrance_capacity(self):
        strength = self.abilities.str_total if self.abilities else 10
        return strength * 15

    def inventory_weight(self):
        return sum(item.total_weight() for item in self.inventory_items)

    def attuned_count(self):
        return sum(1 for item in self.inventory_items if item.is_attuned)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'campaign': self.campaign,
            'level': self.level,
            'race': self.race,
            'subrace': self.subrace,
            'character_class': self.character_class,
            'hit_die': self.hit_die,
            'proficiency_bonus': self.proficiency_bonus(),
            'alignment': self.alignment,
            'background': self.background,
            'personality_traits': self.personality_traits,
            'ideals': self.ideals,
            'bonds': self.bonds,
            'flaws': self.flaws,
            'vitals': {
                'hp_current': self.hp_current,
                'hp_max': self.hp_max,
                'hp_temp': self.hp_temp,
                'hit_dice_current': self.hit_dice_current,
                'hit_dice_max': self.hit_dice_max,
                'ac_base': self.ac_base,
                'ac_current': self.ac_current,
                'speed': self.speed,
            },
            'coins': {
                'cp': self.cp,
                'sp': self.sp,
                'ep': self.ep,
                'gp': self.gp,
                'pp': self.pp,
                'total_cp': self.coins_as_cp(),
            },
            'abilities': self.abilities.to_dict() if self.abilities else None,
            'spell_slots': [slot.to_dict() for slot in sorted(self.spell_slots, key=lambda s: s.slot_level)],
            'inventory': [item.to_dict() for item in self.inventory_items],
            'encumbrance': {
                'current_weight': self.inventory_weight(),
                'capacity': self.encumbrance_capacity(),
            },
            'attunement': {
                'used': self.attuned_count(),
                'max': self.attunement_slots,
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class CharacterAbility(db.Model):
    __tablename__ = 'character_abilities'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False, unique=True)

    str_base = db.Column(db.Integer, nullable=False, default=8)
    dex_base = db.Column(db.Integer, nullable=False, default=8)
    con_base = db.Column(db.Integer, nullable=False, default=8)
    int_base = db.Column(db.Integer, nullable=False, default=8)
    wis_base = db.Column(db.Integer, nullable=False, default=8)
    cha_base = db.Column(db.Integer, nullable=False, default=8)

    str_racial = db.Column(db.Integer, nullable=False, default=0)
    dex_racial = db.Column(db.Integer, nullable=False, default=0)
    con_racial = db.Column(db.Integer, nullable=False, default=0)
    int_racial = db.Column(db.Integer, nullable=False, default=0)
    wis_racial = db.Column(db.Integer, nullable=False, default=0)
    cha_racial = db.Column(db.Integer, nullable=False, default=0)

    @property
    def str_total(self):
        return self.str_base + self.str_racial

    @property
    def dex_total(self):
        return self.dex_base + self.dex_racial

    @property
    def con_total(self):
        return self.con_base + self.con_racial

    @property
    def int_total(self):
        return self.int_base + self.int_racial

    @property
    def wis_total(self):
        return self.wis_base + self.wis_racial

    @property
    def cha_total(self):
        return self.cha_base + self.cha_racial

    def to_dict(self):
        return {
            'str': {'base': self.str_base, 'racial': self.str_racial, 'total': self.str_total, 'mod': ability_modifier(self.str_total)},
            'dex': {'base': self.dex_base, 'racial': self.dex_racial, 'total': self.dex_total, 'mod': ability_modifier(self.dex_total)},
            'con': {'base': self.con_base, 'racial': self.con_racial, 'total': self.con_total, 'mod': ability_modifier(self.con_total)},
            'int': {'base': self.int_base, 'racial': self.int_racial, 'total': self.int_total, 'mod': ability_modifier(self.int_total)},
            'wis': {'base': self.wis_base, 'racial': self.wis_racial, 'total': self.wis_total, 'mod': ability_modifier(self.wis_total)},
            'cha': {'base': self.cha_base, 'racial': self.cha_racial, 'total': self.cha_total, 'mod': ability_modifier(self.cha_total)},
        }


class CharacterSpellSlot(db.Model):
    __tablename__ = 'character_spell_slots'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    slot_level = db.Column(db.Integer, nullable=False)
    max_slots = db.Column(db.Integer, nullable=False, default=0)
    used_slots = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint('character_id', 'slot_level', name='uix_character_slot_level'),
    )

    def to_dict(self):
        return {
            'slot_level': self.slot_level,
            'max_slots': self.max_slots,
            'used_slots': self.used_slots,
            'available_slots': max(self.max_slots - self.used_slots, 0),
        }


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    weight = db.Column(db.Float, nullable=False, default=0.0)
    price_gp = db.Column(db.Float, nullable=False, default=0.0)
    is_equipped = db.Column(db.Boolean, nullable=False, default=False)
    grants_ac = db.Column(db.Integer, nullable=False, default=0)
    requires_attunement = db.Column(db.Boolean, nullable=False, default=False)
    is_attuned = db.Column(db.Boolean, nullable=False, default=False)
    source = db.Column(db.String(40), nullable=False, default='manual')

    def total_weight(self):
        return round((self.weight or 0.0) * max(self.quantity, 0), 2)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'weight': self.weight,
            'total_weight': self.total_weight(),
            'price_gp': self.price_gp,
            'is_equipped': self.is_equipped,
            'grants_ac': self.grants_ac,
            'requires_attunement': self.requires_attunement,
            'is_attuned': self.is_attuned,
            'source': self.source,
        }


class ShopItem(db.Model):
    __tablename__ = 'shop_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    category = db.Column(db.String(60), nullable=False)
    price_gp = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price_gp': self.price_gp,
            'weight': self.weight,
            'description': self.description,
        }


class LedgerEntry(db.Model):
    __tablename__ = 'ledger_entries'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)  # credit | debit
    amount_cp = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(220), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'entry_type': self.entry_type,
            'amount_cp': self.amount_cp,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }