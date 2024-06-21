import unittest

from src import poketrader, pokemon

class TestPartyData(unittest.TestCase):

    def setUp(self) -> None:
        self.party_data = poketrader.PartyData(bytearray(32 * 1024))
        self.party_data.player_name = "Bill"
        self.pokemon_size = 44

    def test_empty_party_from_empty_data(self):
        self.assertEqual(self.party_data.num_pokemon, 0)
    
    def test_append_pokemon_to_party(self):
        a_pokemon = poketrader.Pokemon(bytearray(self.pokemon_size))
        a_pokemon.species_id = pokemon.species_id_for("Bulbasaur")
        a_pokemon.level = 5
        self.party_data.append_pokemon_to_party(a_pokemon)
        self.assertEqual(self.party_data.num_pokemon, 1)
        self.assertEqual(self.party_data.pokemon(0).species, "Bulbasaur")
        self.assertEqual(self.party_data.pokemon(0).level, 5)
        self.assertEqual(self.party_data.nickname_ascii(0), "BULBASAUR")
        self.assertEqual(self.party_data.ot_name_ascii(0), "Bill")
        self.assertTrue(poketrader.check_pokedex(self.party_data.data, a_pokemon.species_id))

    def test_append_to_full_party(self):
        for i in range(6):
            a_pokemon = poketrader.Pokemon(bytearray(self.pokemon_size))
            a_pokemon.species_id = 5
            a_pokemon.level = (i + 1) * 2
            self.party_data.append_pokemon_to_party(a_pokemon)
        self.assertEqual(self.party_data.num_pokemon, 6)
        with self.assertRaises(IndexError):
            self.party_data.append_pokemon_to_party(poketrader.Pokemon(bytearray(self.pokemon_size)))

    def append_pokemon(self, party_data, species, level):
        a_pokemon = poketrader.Pokemon(bytearray(self.pokemon_size))
        a_pokemon.species_id = pokemon.species_id_for(species)
        a_pokemon.level = level
        party_data.append_pokemon_to_party(a_pokemon)

    def test_trade_pokemon(self):
        self.append_pokemon(self.party_data, "Bulbasaur", 5)        
        self.append_pokemon(self.party_data, "Charmander", 8)

        party_data_two = poketrader.PartyData(bytearray(32 * 1024))
        party_data_two.player_name = "Charlie"
        self.append_pokemon(party_data_two, "Squirtle", 9)
        self.append_pokemon(party_data_two, "Caterpie", 6)

        poketrader.trade_pokemon(0, 1, self.party_data, party_data_two)

        self.assertEqual(self.party_data.num_pokemon, 2)
        self.assertEqual(self.party_data.pokemon(0).species, "Caterpie")
        self.assertEqual(self.party_data.pokemon(1).species, "Charmander")
        self.assertEqual(self.party_data.ot_name_ascii(0), "Charlie")
        self.assertEqual(self.party_data.ot_name_ascii(1), "Bill")

        self.assertEqual(party_data_two.num_pokemon, 2)
        self.assertEqual(party_data_two.pokemon(0).species, "Squirtle")
        self.assertEqual(party_data_two.pokemon(1).species, "Bulbasaur")
        self.assertEqual(party_data_two.ot_name_ascii(0), "Charlie")
        self.assertEqual(party_data_two.ot_name_ascii(1), "Bill")
    
    def test_trade_evolution(self):
        self.append_pokemon(self.party_data, "Graveler", 15)

        party_data_two = poketrader.PartyData(bytearray(32 * 1024))
        party_data_two.player_name = "Charlie"
        self.append_pokemon(party_data_two, "Machoke", 20)

        poketrader.trade_pokemon(0, 0, self.party_data, party_data_two)

        self.assertEqual(self.party_data.pokemon(0).species, "Machamp")
        for pokemon_name in ("Graveler", "Golem", "Machoke", "Machamp"):
            self.assertTrue(poketrader.check_pokedex(self.party_data.data, pokemon.species_id_for(pokemon_name)))
            self.assertTrue(poketrader.check_pokedex(party_data_two.data, pokemon.species_id_for(pokemon_name)))
        

