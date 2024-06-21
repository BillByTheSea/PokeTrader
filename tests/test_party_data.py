import unittest

from src import pokemon, save_data, text


class TestPartyData(unittest.TestCase):
    def setUp(self) -> None:
        self.party_data_one = save_data.PartyData(bytearray(32 * 1024))
        self.party_data_one.player_name = "Bill"
        self.party_data_two = save_data.PartyData(bytearray(32 * 1024))
        self.party_data_two.player_name = "Charlie"
        self.pokemon_size = 44

    def test_empty_party_from_empty_data(self):
        self.assertEqual(self.party_data_one.num_pokemon, 0)

    def test_append_pokemon_to_party(self):
        a_pokemon = save_data.Pokemon(bytearray(self.pokemon_size))
        a_pokemon.species_id = pokemon.species_id_for("Bulbasaur")
        a_pokemon.level = 5
        self.party_data_one.append_pokemon_to_party(a_pokemon)
        self.assertEqual(self.party_data_one.num_pokemon, 1)
        self.assertEqual(self.party_data_one.pokemon(0).species, "Bulbasaur")
        self.assertEqual(self.party_data_one.pokemon(0).level, 5)
        self.assertEqual(self.party_data_one.nickname_ascii(0), "BULBASAUR")
        self.assertEqual(self.party_data_one.ot_name_ascii(0), "Bill")
        self.assertTrue(
            save_data.check_pokedex(self.party_data_one.data, a_pokemon.species_id)
        )

    def test_append_to_full_party(self):
        for i in range(6):
            a_pokemon = save_data.Pokemon(bytearray(self.pokemon_size))
            a_pokemon.species_id = 5
            a_pokemon.level = (i + 1) * 2
            self.party_data_one.append_pokemon_to_party(a_pokemon)
        self.assertEqual(self.party_data_one.num_pokemon, 6)
        with self.assertRaises(IndexError):
            self.party_data_one.append_pokemon_to_party(
                save_data.Pokemon(bytearray(self.pokemon_size))
            )

    def append_pokemon(self, party_data, species, level):
        a_pokemon = save_data.Pokemon(bytearray(self.pokemon_size))
        a_pokemon.species_id = pokemon.species_id_for(species)
        a_pokemon.level = level
        party_data.append_pokemon_to_party(a_pokemon)

    def test_trade_pokemon(self):
        self.append_pokemon(self.party_data_one, "Bulbasaur", 5)
        self.append_pokemon(self.party_data_one, "Charmander", 8)

        self.append_pokemon(self.party_data_two, "Squirtle", 9)
        self.append_pokemon(self.party_data_two, "Caterpie", 6)

        save_data.trade_pokemon(0, 1, self.party_data_one, self.party_data_two)

        self.assertEqual(self.party_data_one.num_pokemon, 2)
        self.assertEqual(self.party_data_one.pokemon(0).species, "Caterpie")
        self.assertEqual(self.party_data_one.pokemon(1).species, "Charmander")
        self.assertEqual(self.party_data_one.ot_name_ascii(0), "Charlie")
        self.assertEqual(self.party_data_one.ot_name_ascii(1), "Bill")

        self.assertEqual(self.party_data_two.num_pokemon, 2)
        self.assertEqual(self.party_data_two.pokemon(0).species, "Squirtle")
        self.assertEqual(self.party_data_two.pokemon(1).species, "Bulbasaur")
        self.assertEqual(self.party_data_two.ot_name_ascii(0), "Charlie")
        self.assertEqual(self.party_data_two.ot_name_ascii(1), "Bill")

    def test_trade_evolution(self):
        self.append_pokemon(self.party_data_one, "Graveler", 15)
        self.append_pokemon(self.party_data_two, "Machoke", 20)

        save_data.trade_pokemon(0, 0, self.party_data_one, self.party_data_two)

        self.assertEqual(self.party_data_one.pokemon(0).species, "Machamp")
        for pokemon_name in ("Graveler", "Golem", "Machoke", "Machamp"):
            self.assertTrue(
                save_data.check_pokedex(
                    self.party_data_one.data, pokemon.species_id_for(pokemon_name)
                )
            )
            self.assertTrue(
                save_data.check_pokedex(
                    self.party_data_two.data, pokemon.species_id_for(pokemon_name)
                )
            )

    def test_trade_evolution_keeps_nicknames(self):
        self.append_pokemon(self.party_data_one, "Graveler", 15)
        self.party_data_one.set_nickname(
            0, text.ascii_string_to_pokii_string("Rocky", 11)
        )

        self.append_pokemon(self.party_data_two, "Machoke", 20)
        self.party_data_two.set_nickname(
            0, text.ascii_string_to_pokii_string("Chuck", 11)
        )

        save_data.trade_pokemon(0, 0, self.party_data_one, self.party_data_two)

        self.assertEqual(self.party_data_one.nickname_ascii(0), "Chuck")
        self.assertEqual(self.party_data_two.nickname_ascii(0), "Rocky")

    def test_has_nickname(self):
        self.append_pokemon(self.party_data_one, "Bulbasaur", 5)
        self.assertEqual(self.party_data_one.has_nickname(0), False)
        self.party_data_one.set_nickname(
            0, text.ascii_string_to_pokii_string("name", 11)
        )
        self.assertEqual(self.party_data_one.has_nickname(0), True)
        self.assertEqual(self.party_data_one.nickname_ascii(0), "name")
