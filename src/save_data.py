from src import text
from enum import Flag, auto, IntEnum

from src.pokemon import (
    POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER,
    TRADE_EVOLUTIONS,
    POKEMON_BY_INDEX,
    stupid_index_to_correct_index,
)


class StatusCondition(Flag):
    NONE = 0
    UNUSUED_1 = auto()
    UNUSUED_2 = auto()
    SLEEP = auto()
    POISON = auto()
    BURN = auto()
    FREEZE = auto()
    PARALYSIS = auto()


class PokemonType(IntEnum):
    NORMAL = 0
    FIGHTING = 1
    FLYING = 2
    POISON = 3
    GROUND = 4
    ROCK = 5
    BUG = 7
    GHOST = 8
    FIRE = 20
    WATER = 21
    GRASS = 22
    ELECTRIC = 23
    PSYCHIC = 24
    ICE = 25
    DRAGON = 26


# Constants
_player_name_offset = 0x2598
_player_name_size = 0xB
_pokedex_seen_address = 0x25B6
_pokedex_owned_address = 0x25A3
_pokedex_data_size = 0x13
_party_data_offset = 0x2F2C
_checksum_address = 0x3523
_species_id_offset = _party_data_offset + 1
_pokemon_party_data_offset = _party_data_offset + 0x8

# Internal party data offsets
_pokemon_size = 0x2C
_current_hp_offset = 0x01
_status_condition_offset = 0x04
_type_one_offset = 0x05
_type_two_offset = 0x06
_catch_rate = 0x07
_moves_offset = 0x08
_original_trainer_id_offset = 0x0C
_experience_offset = 0x0E
_level_offset = 0x21
_ot_name_offset = 0x110
_nickname_offset = 0x152


def pokedex_index_of(pokemon_name):
    return POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER.index(pokemon_name)


def write_int_as_bytes(data: bytearray, offset: int, *, value: int, size: int) -> bytes:
    return data[offset : offset + size] + value.to_bytes(size, byteorder="big")


def update_save_data(save: "SaveData", original_bytes: bytes) -> bytes:
    updated = update_party_data(save.party, original_bytes)
    for pokedex_number in save.pokemon_owned:
        set_pokedex(updated, pokedex_number, _pokedex_owned_address)
    for pokedex_number in save.pokemon_seen:
        set_pokedex(updated, pokedex_number, _pokedex_seen_address)

    updated[_checksum_address] = checksum(updated)
    return updated


def update_party_data(party: "PartyDataIsolated", original_bytes: bytes) -> bytes:
    updated = bytearray(original_bytes)
    updated[_party_data_offset] = len(party.pokemon)
    for pokemon_index, pokemon in enumerate(party.pokemon):
        pokemon_offset = _pokemon_party_data_offset + (_pokemon_size * pokemon_index)
        updated[pokemon_offset] = pokemon.species_id
        write_int_as_bytes(
            updated,
            pokemon_offset + _current_hp_offset,
            value=pokemon.current_hp,
            size=2,
        )
        updated[
            pokemon_offset + _status_condition_offset
        ] = pokemon.status_condition.value
        updated[pokemon_offset + _type_one_offset] = pokemon.type_one
        updated[pokemon_offset + _type_two_offset] = pokemon.type_two
        updated[pokemon_offset + _level_offset] = pokemon.level
        updated[pokemon_offset + _catch_rate] = pokemon.catch_rate
        moves_offset = pokemon_offset + _moves_offset
        updated[moves_offset : moves_offset + 4] = pokemon.moves
        ot_id_offset = pokemon_offset + _original_trainer_id_offset
        write_int_as_bytes(
            updated, ot_id_offset, value=pokemon.original_trainer_id, size=2
        )
        write_int_as_bytes(
            updated,
            pokemon_offset + _experience_offset,
            value=pokemon.experience,
            size=3,
        )

        ot_name_offset = _party_data_offset + _ot_name_offset + (pokemon_index * 0xB)
        ot_name_length = len(pokemon.ot_name) + 1  # Include terminator
        updated[
            ot_name_offset : ot_name_offset + ot_name_length
        ] = text.ascii_string_to_pokii_string(pokemon.ot_name, length=0xB)

        nickname_offset = _party_data_offset + _nickname_offset + (pokemon_index * 0xB)
        nickname_length = len(pokemon.nickname) + 1  # Include terminator
        updated[
            nickname_offset : nickname_offset + nickname_length
        ] = text.ascii_string_to_pokii_string(pokemon.nickname, length=0xB)
        return updated


def read_bytes(data: bytes, offset: int, size: int) -> int:
    return int.from_bytes(data[offset : offset + size], byteorder="big")


def enumerate_party(party: "PartyDataIsolated") -> str:
    result = ""
    for i, pokemon in enumerate(party.pokemon):
        result += f"{i + 1}. {pokemon.nickname} ({POKEMON_BY_INDEX[pokemon.species_id]}) - Level {pokemon.level}\n"
    return result.strip()


def read_save_data(data: bytes):
    result = SaveData()
    result.player_name = text.pokii_string_to_ascii_string(
        data[_player_name_offset : _player_name_offset + _player_name_size],
        length=_player_name_size,
    )
    result.party = read_party_data(data)
    result.pokemon_owned = set(pokemon_in_pokedex(data, _pokedex_owned_address))
    result.pokemon_seen = set(pokemon_in_pokedex(data, _pokedex_seen_address))
    return result


def pokemon_in_pokedex(data, start_address):
    pokedex_data = data[start_address : start_address + _pokedex_data_size]
    for i, byte in enumerate(pokedex_data):
        for j in range(8):
            if (byte >> j) & 1:
                yield (i * 8 + j)


def checksum(data):
    return (255 - sum(data[0x2598:0x3523])) & 255


def set_pokedex(data, pokedex_number, address):
    index = address + (pokedex_number >> 3)
    bit_position = pokedex_number & 7
    data[index] |= 1 << bit_position


def read_party_data(data: bytes):
    result = PartyDataIsolated()
    for i in range(data[_party_data_offset]):
        pokemon = PokemonIsolated()
        pokemon.species_id = data[_species_id_offset + i]
        pokemon_offset = _pokemon_party_data_offset + (_pokemon_size * i)
        pokemon.current_hp = read_bytes(data, pokemon_offset + _current_hp_offset, 2)
        pokemon.status_condition = StatusCondition(
            data[pokemon_offset + _status_condition_offset]
        )
        pokemon.type_one = PokemonType(data[pokemon_offset + _type_one_offset])
        pokemon.type_two = PokemonType(data[pokemon_offset + _type_two_offset])
        pokemon.catch_rate = data[pokemon_offset + _catch_rate]
        pokemon.moves = list(
            data[pokemon_offset + _moves_offset : pokemon_offset + _moves_offset + 4]
        )
        pokemon.original_trainer_id = read_bytes(
            data, pokemon_offset + _original_trainer_id_offset, 2
        )
        pokemon.experience = read_bytes(data, pokemon_offset + _experience_offset, 3)
        pokemon.level = data[pokemon_offset + _level_offset]

        ot_name_offset = _party_data_offset + _ot_name_offset + (i * 0xB)
        pokemon.ot_name = text.pokii_string_to_ascii_string(
            data[ot_name_offset : ot_name_offset + 0xB], length=0xB
        )

        nickname_offset = _party_data_offset + _nickname_offset + (i * 0xB)
        pokemon.nickname = text.pokii_string_to_ascii_string(
            data[nickname_offset : nickname_offset + 0xB], length=0xB
        )

        result.pokemon.append(pokemon)
    return result


class PokemonIsolated:
    def __init__(self):
        self.species_id: int = 0
        self.current_hp: int = 0
        self.status_condition: int = 0
        self.type_one: PokemonType = PokemonType.GHOST
        self.type_two: PokemonType = PokemonType.DRAGON
        self.catch_rate: int = 0
        self.moves: list[int] = []
        self.original_trainer_id: int = 0
        self.experience: int = 0
        self.level: int = 0
        self.ot_name: str = ""
        self.nickname: str = ""


class PartyDataIsolated:
    def __init__(self):
        self.pokemon: list[PokemonIsolated] = []


class SaveData:
    def __init__(self):
        self.player_name: str = ""
        self.party: PartyDataIsolated = PartyDataIsolated()
        self.pokemon_seen: set[int] = set()
        self.pokemon_owned: set[int] = set()


def trade_pokemon(
    index_one: int, index_two: int, save_one: SaveData, save_two: SaveData
):
    pokemon_one = save_one.party.pokemon[index_one]
    pokemon_two = save_two.party.pokemon[index_two]
    save_one.party.pokemon[index_one], save_two.party.pokemon[index_two] = (
        pokemon_two,
        pokemon_one,
    )

    if pokemon_one.species_id in TRADE_EVOLUTIONS:
        if pokemon_one.nickname == POKEMON_BY_INDEX[pokemon_one.species_id].upper():
            pokemon_one.nickname = POKEMON_BY_INDEX[
                TRADE_EVOLUTIONS[pokemon_one.species_id]
            ].upper()
            save_one.pokemon_owned.add(
                stupid_index_to_correct_index(pokemon_one.species_id)
            )
            save_two.pokemon_owned.add(
                stupid_index_to_correct_index(pokemon_one.species_id)
            )
        pokemon_one.species_id = TRADE_EVOLUTIONS[pokemon_one.species_id]

    if pokemon_two.species_id in TRADE_EVOLUTIONS:
        if pokemon_two.nickname == POKEMON_BY_INDEX[pokemon_two.species_id].upper():
            pokemon_two.nickname = POKEMON_BY_INDEX[
                TRADE_EVOLUTIONS[pokemon_two.species_id]
            ].upper()
            save_one.pokemon_owned.add(
                stupid_index_to_correct_index(pokemon_two.species_id)
            )
            save_two.pokemon_owned.add(
                stupid_index_to_correct_index(pokemon_two.species_id)
            )
        pokemon_two.species_id = TRADE_EVOLUTIONS[pokemon_two.species_id]

    save_one.pokemon_owned.add(stupid_index_to_correct_index(pokemon_one.species_id))
    save_one.pokemon_owned.add(stupid_index_to_correct_index(pokemon_two.species_id))
    save_two.pokemon_owned.add(stupid_index_to_correct_index(pokemon_one.species_id))
    save_two.pokemon_owned.add(stupid_index_to_correct_index(pokemon_two.species_id))

    save_one.pokemon_seen.update(save_one.pokemon_owned)
    save_two.pokemon_seen.update(save_two.pokemon_owned)
