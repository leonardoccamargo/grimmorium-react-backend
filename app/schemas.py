from pydantic import BaseModel, Field
from typing import List, Optional


# ===== LEGADO MVP 1 =====
class PersonagemSchema(BaseModel):
    nome: str = Field(..., description='Nome do personagem', example='Aragorn')
    classe: str = Field(..., description='Classe do personagem', example='Guerreiro')
    nivel: Optional[int] = Field(1, description='Nível do personagem', example=10)


class PersonagemResponseSchema(BaseModel):
    id: int = Field(..., description='ID do personagem')
    nome: str = Field(..., description='Nome do personagem')
    classe: str = Field(..., description='Classe do personagem')
    nivel: int = Field(..., description='Nível do personagem')


class PersonagensListSchema(BaseModel):
    status: str = Field(..., example='success')
    total: int = Field(..., example=1)
    personagens: List[PersonagemResponseSchema]


class PersonagemSingleSchema(BaseModel):
    status: str = Field(..., example='success')
    personagem: PersonagemResponseSchema


class PersonagemCreateSchema(BaseModel):
    status: str = Field(..., example='success')
    message: str = Field(..., example='Personagem criado com sucesso')
    personagem: PersonagemResponseSchema


class ErrorSchema(BaseModel):
    status: str = Field(..., example='error')
    message: str = Field(..., example='Mensagem de erro')


# ===== V2 ROADMAP MASTERIZADO =====
class PathCharacterId(BaseModel):
    id: int = Field(..., description='ID do personagem')


class QueryCharactersV2(BaseModel):
    name: Optional[str] = Field(None, description='Filtro por nome')
    campaign: Optional[str] = Field(None, description='Filtro por campanha')
    character_class: Optional[str] = Field(None, description='Filtro por classe')
    min_level: Optional[int] = Field(None, ge=1, le=20)
    max_level: Optional[int] = Field(None, ge=1, le=20)


class AbilityInputSchema(BaseModel):
    str_base: int = Field(..., ge=3, le=18)
    dex_base: int = Field(..., ge=3, le=18)
    con_base: int = Field(..., ge=3, le=18)
    int_base: int = Field(..., ge=3, le=18)
    wis_base: int = Field(..., ge=3, le=18)
    cha_base: int = Field(..., ge=3, le=18)
    str_racial: int = Field(0, ge=0, le=6)
    dex_racial: int = Field(0, ge=0, le=6)
    con_racial: int = Field(0, ge=0, le=6)
    int_racial: int = Field(0, ge=0, le=6)
    wis_racial: int = Field(0, ge=0, le=6)
    cha_racial: int = Field(0, ge=0, le=6)


class SpellSlotInputSchema(BaseModel):
    slot_level: int = Field(..., ge=1, le=9)
    max_slots: int = Field(..., ge=0, le=9)
    used_slots: int = Field(0, ge=0, le=9)


class InventoryItemInputSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: Optional[str] = Field(None, max_length=60)
    quantity: int = Field(1, ge=1, le=999)
    weight: float = Field(0.0, ge=0)
    price_gp: float = Field(0.0, ge=0)
    is_equipped: bool = False
    grants_ac: int = Field(0, ge=0, le=10)
    requires_attunement: bool = False
    is_attuned: bool = False
    source: str = Field('manual', max_length=40)


class CharacterWizardCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    campaign: Optional[str] = Field(None, max_length=120)
    level: int = Field(1, ge=1, le=20)
    race: str = Field(..., min_length=1, max_length=60)
    subrace: Optional[str] = Field(None, max_length=60)
    character_class: str = Field(..., min_length=1, max_length=60)
    hit_die: int = Field(8, ge=4, le=20)
    alignment: Optional[str] = Field(None, max_length=32)
    background: Optional[str] = Field(None, max_length=80)
    personality_traits: Optional[str] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None
    hp_max: int = Field(10, ge=1, le=999)
    hp_current: Optional[int] = Field(None, ge=0, le=999)
    hp_temp: int = Field(0, ge=0, le=999)
    ac_base: int = Field(10, ge=1, le=30)
    speed: int = Field(30, ge=0, le=120)
    coins_cp: int = Field(0, ge=0)
    coins_sp: int = Field(0, ge=0)
    coins_ep: int = Field(0, ge=0)
    coins_gp: int = Field(0, ge=0)
    coins_pp: int = Field(0, ge=0)
    abilities: AbilityInputSchema
    spell_slots: List[SpellSlotInputSchema] = Field(default_factory=list)
    inventory: List[InventoryItemInputSchema] = Field(default_factory=list)


class CharacterPlayPatchSchema(BaseModel):
    hp_current: Optional[int] = Field(None, ge=0, le=999)
    hp_temp: Optional[int] = Field(None, ge=0, le=999)
    hit_dice_current: Optional[int] = Field(None, ge=0, le=20)
    ac_base: Optional[int] = Field(None, ge=1, le=30)
    speed: Optional[int] = Field(None, ge=0, le=120)


class SpellSlotPatchSchema(BaseModel):
    used_slots: int = Field(..., ge=0, le=9)


class RewardSchema(BaseModel):
    amount_gp: float = Field(..., gt=0)
    description: str = Field(..., min_length=3, max_length=220)


class ShopItemCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=60)
    price_gp: float = Field(..., ge=0)
    weight: float = Field(0.0, ge=0)
    description: Optional[str] = None


class ShopQuerySchema(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None


class PurchaseSchema(BaseModel):
    shop_item_id: int = Field(..., ge=1)
    quantity: int = Field(1, ge=1, le=999)


class InventoryEquipSchema(BaseModel):
    is_equipped: bool


class InventoryAttuneSchema(BaseModel):
    is_attuned: bool
