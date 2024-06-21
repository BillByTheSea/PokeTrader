from src.pokemon import (
    POKEMON_BY_INDEX,
    POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER,
    species_id_for,
    stupid_index_to_correct_index,
)

import unittest


class TestPokemon(unittest.TestCase):
    def test_lists_align(self):
        for pokemon in POKEMON_BY_INDEX[1:]:
            if "MissingNo" not in pokemon:
                self.assertIn(pokemon, POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER)

        for pokemon in POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER:
            self.assertIn(pokemon, POKEMON_BY_INDEX)

    def test_index_conversion(self):
        for index, pokemon in enumerate(POKEMON_IN_THE_ACTUAL_GODDAMN_CORRECT_ORDER):
            correct_index = stupid_index_to_correct_index(species_id_for(pokemon))
            self.assertEqual(correct_index, index)
