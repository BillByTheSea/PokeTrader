from src import text
from src.pokemon import (
    POKEMON_BY_INDEX,
    POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER,
    TRADE_EVOLUTIONS,
    stupid_index_to_correct_index,
)


def pokemon_to_string(species_id: int) -> str:
    pokemon = POKEMON_BY_INDEX[species_id]
    return "MissingNo." if "MissingNo." in pokemon else pokemon


def party_to_string(party):
    # Print each pokemon on a new line, and number them.
    result = ""
    for index in range(party.num_pokemon):
        pokemon = party.pokemon(index)
        nickname = party.nickname_ascii(index)
        result += (
            f"{index + 1}. {pokemon.species} ({nickname}) - Level {pokemon.level}\n"
        )
    return result


class Pokemon:
    def __init__(self, memory):
        self.memory = memory

    @property
    def level(self):
        return self.memory[0x21]

    @level.setter
    def level(self, value):
        self.memory[0x21] = value

    @property
    def species_id(self):
        return self.memory[0x00]

    @species_id.setter
    def species_id(self, value):
        self.memory[0x00] = value

    @property
    def species(self):
        return pokemon_to_string(self.species_id)


class PartyData:
    def __init__(self, data):
        self.data = data
        self._party_data_offset = 0x2F2C
        self._pokemon_size = 0x2C
        self._ot_name_size = 0xB
        self._nickname_size = 0xB
        self._player_name_offset = 0x2598
        self._pokemon_offset = self._party_data_offset + 0x8
        self._ot_name_offset = self._party_data_offset + 0x110
        self._nickname_offset = self._party_data_offset + 0x152
        self._player_name_size = 0xB

    def __str__(self):
        return party_to_string(self)

    def append_pokemon_to_party(self, pokemon: Pokemon):
        if self.num_pokemon >= 6:
            raise IndexError("Party is full")

        index = self.num_pokemon
        nickname = text.ascii_string_to_pokii_string(
            pokemon_to_string(pokemon.species_id).upper(), length=self._nickname_size
        )
        self.insert_at(index, pokemon, self.player_name, nickname)
        self.data[self._party_data_offset] += 1

    @property
    def num_pokemon(self):
        return self.data[self._party_data_offset]

    def pokemon(self, index):
        offset = self._pokemon_offset + (index * self._pokemon_size)
        return Pokemon(self.data[offset : offset + self._pokemon_size])

    @property
    def player_name(self):
        return self.data[
            self._player_name_offset : self._player_name_offset + self._player_name_size
        ]

    @player_name.setter
    def player_name(self, player_name_ascii):
        player_name_encoded = text.ascii_string_to_pokii_string(
            player_name_ascii, length=self._player_name_size
        )
        self.data[
            self._player_name_offset : self._player_name_offset + self._player_name_size
        ] = player_name_encoded

    def ot_name(self, index):
        offset = self._ot_name_offset + (index * self._ot_name_size)
        return self.data[offset : offset + self._ot_name_size]

    def ot_name_ascii(self, index):
        return text.pokii_string_to_ascii_string(
            self.ot_name(index), length=self._ot_name_size
        )

    def nickname(self, index):
        offset = self._nickname_offset + (index * self._nickname_size)
        return self.data[offset : offset + self._nickname_size]

    def set_nickname(self, index, nickname_pokii):
        offset = self._nickname_offset + (index * self._nickname_size)
        self.data[offset : offset + self._nickname_size] = nickname_pokii

    def nickname_ascii(self, index):
        return text.pokii_string_to_ascii_string(
            self.nickname(index), length=self._nickname_size
        )

    def has_nickname(self, index):
        return self.nickname_ascii(index) != self.pokemon(index).species.upper()

    def insert_at(self, index, pokemon, ot_name, nickname):
        species_id_offset = self._party_data_offset + 0x01 + (index * 0x01)
        self.data[species_id_offset] = pokemon.species_id
        pokemon_offset = self._pokemon_offset + (index * self._pokemon_size)
        self.data[
            pokemon_offset : pokemon_offset + self._pokemon_size
        ] = pokemon.memory[:]
        ot_name_offset = self._ot_name_offset + (index * self._ot_name_size)
        self.data[ot_name_offset : ot_name_offset + self._ot_name_size] = ot_name[:]
        nickname_offset = self._nickname_offset + (index * self._nickname_size)
        self.data[nickname_offset : nickname_offset + self._nickname_size] = nickname[:]

        set_pokedex(self.data, pokemon.species_id)


def check_pokedex(data, pokemon_index):
    pokemon_index = POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER.index(
        POKEMON_BY_INDEX[pokemon_index]
    )
    owned_address = 0x25A3
    pokedex_data = data[owned_address:]
    return ((pokedex_data[pokemon_index >> 3] >> (pokemon_index & 7)) & 1) != 0


def set_pokedex(data, species_id):
    pokemon_index = stupid_index_to_correct_index(species_id)

    def set_pokedex_impl(data, address):
        index = address + (pokemon_index >> 3)
        bit_position = pokemon_index & 7
        data[index] |= 1 << bit_position

    owned_address = 0x25A3
    seen_address = 0x25B6

    set_pokedex_impl(data, owned_address)
    set_pokedex_impl(data, seen_address)


def trade_pokemon(pokemon_one_index, pokemon_two_index, party_one, party_two):
    pokemon_one = party_one.pokemon(pokemon_one_index)
    pokemon_two = party_two.pokemon(pokemon_two_index)

    set_pokedex(party_one.data, pokemon_two.species_id)
    set_pokedex(party_two.data, pokemon_one.species_id)

    ot_name_one = party_one.ot_name(pokemon_one_index)[:]
    ot_name_two = party_two.ot_name(pokemon_two_index)[:]

    if pokemon_one.species_id in TRADE_EVOLUTIONS:
        evolve_pokemon(pokemon_one_index, party_one, party_two, pokemon_one)

    if pokemon_two.species_id in TRADE_EVOLUTIONS:
        evolve_pokemon(pokemon_two_index, party_two, party_one, pokemon_two)

    nickname_one = party_one.nickname(pokemon_one_index)[:]
    nickname_two = party_two.nickname(pokemon_two_index)[:]

    party_one.insert_at(pokemon_one_index, pokemon_two, ot_name_two, nickname_two)
    party_two.insert_at(pokemon_two_index, pokemon_one, ot_name_one, nickname_one)

    return party_one.data, party_two.data


def evolve_pokemon(party_index, source_party, destination_party, the_pokemon):
    evolved_index = TRADE_EVOLUTIONS[the_pokemon.species_id]
    evolved_name = POKEMON_BY_INDEX[evolved_index].upper()
    evolved_name_encoded = text.ascii_string_to_pokii_string(evolved_name, 0xB)
    print(
        f"Evolved {source_party.ot_name_ascii(party_index)}'s {source_party.nickname_ascii(party_index)} into {pokemon_to_string(evolved_index)}"
    )
    if not source_party.has_nickname(party_index):
        source_party.set_nickname(party_index, evolved_name_encoded)
    the_pokemon.species_id = evolved_index
    set_pokedex(destination_party.data, the_pokemon.species_id)
    set_pokedex(source_party.data, the_pokemon.species_id)


def checksum(data):
    return (255 - sum(data[0x2598:0x3523])) & 255
