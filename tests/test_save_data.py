import unittest
import pathlib

from src.pokemon import (
    TRADE_EVOLUTIONS,
    POKEMON_BY_INDEX,
    stupid_index_to_correct_index,
)

from src.save_data import (
    enumerate_party,
    read_save_data,
    update_save_data,
    update_party_data,
    pokedex_index_of,
    trade_pokemon,
    PokemonIsolated,
    PokemonType,
    StatusCondition,
    SaveData,
)


class TestSaveDataIsolated(unittest.TestCase):
    def setUp(self) -> None:
        save_file = (
            pathlib.Path(__file__).parent.absolute().parent / "saves" / "red.sav"
        )
        self.save_bytes = save_file.read_bytes()
        self.save_data = read_save_data(self.save_bytes)

    def test_round_trip(self):
        round_tripped_data = update_save_data(self.save_data, self.save_bytes)
        self.assertEqual(self.save_bytes, round_tripped_data)

    def test_read_specific_values(self):
        self.assertSetEqual(
            set(
                pokedex_index_of(pokemon_name)
                for pokemon_name in ("Charmander", "Rattata")
            ),
            self.save_data.pokemon_owned,
        )
        self.assertSetEqual(
            set(
                pokedex_index_of(pokemon_name)
                for pokemon_name in ("Charmander", "Squirtle", "Rattata")
            ),
            self.save_data.pokemon_seen,
        )
        self.assertEqual("RED", self.save_data.player_name)


class TestPartyIsolated(unittest.TestCase):
    def setUp(self) -> None:
        save_file = (
            pathlib.Path(__file__).parent.absolute().parent / "saves" / "red.sav"
        )
        self.party_bytes = save_file.read_bytes()
        self.save_data = read_save_data(self.party_bytes)
        self.party = self.save_data.party

    def test_read_specific_values(self):
        self.assertEqual(2, len(self.party.pokemon))
        self.assertIsInstance(self.party.pokemon[0], PokemonIsolated)

        self.assertEqual(176, self.party.pokemon[0].species_id)
        self.assertEqual(23, self.party.pokemon[0].current_hp)
        self.assertEqual(StatusCondition.NONE, self.party.pokemon[0].status_condition)
        self.assertEqual(self.party.pokemon[0].type_one, PokemonType.FIRE)
        self.assertEqual(self.party.pokemon[0].type_two, PokemonType.FIRE)
        self.assertEqual(self.party.pokemon[0].catch_rate, 45)
        self.assertListEqual(self.party.pokemon[0].moves, [10, 45, 0, 0])
        self.assertEqual(41231, self.party.pokemon[0].original_trainer_id)
        self.assertEqual(325, self.party.pokemon[0].experience)
        self.assertEqual(8, self.party.pokemon[0].level)
        self.assertEqual("RED", self.party.pokemon[0].ot_name)
        self.assertEqual("AKL", self.party.pokemon[0].nickname)

        self.assertEqual(165, self.party.pokemon[1].species_id)
        self.assertEqual(6, self.party.pokemon[1].current_hp)
        self.assertEqual(StatusCondition.NONE, self.party.pokemon[0].status_condition)
        self.assertEqual(self.party.pokemon[1].type_one, PokemonType.NORMAL)
        self.assertEqual(self.party.pokemon[1].type_two, PokemonType.NORMAL)
        self.assertEqual(self.party.pokemon[1].catch_rate, 255)
        self.assertEqual(41231, self.party.pokemon[1].original_trainer_id)
        self.assertEqual(27, self.party.pokemon[1].experience)
        self.assertEqual(3, self.party.pokemon[1].level)
        self.assertEqual("RED", self.party.pokemon[1].ot_name)
        self.assertEqual("RATTATA", self.party.pokemon[1].nickname)

    def test_enumerate_party(self):
        expected_str = """
1. AKL (Charmander) - Level 8
2. RATTATA (Rattata) - Level 3
""".strip()
        self.assertEqual(expected_str, enumerate_party(self.party))

    def test_round_trip(self):
        round_tripped_data = update_party_data(self.party, self.party_bytes)
        self.assertEqual(self.party_bytes, round_tripped_data)

    def test_trade_pokemon(self):
        save_one = SaveData()
        save_one.party.pokemon = [PokemonIsolated()]
        save_one.party.pokemon[0].species_id = 176
        save_one.party.pokemon[0].ot_name = "Bill"
        save_one.party.pokemon[0].nickname = "Nickname"

        save_two = SaveData()
        save_two.party.pokemon = [PokemonIsolated()]
        save_two.party.pokemon[0].species_id = 165
        save_two.party.pokemon[0].ot_name = "Charlie"
        save_two.party.pokemon[0].nickname = "RATTATA"

        trade_pokemon(0, 0, save_one, save_two)

        self.assertEqual(1, len(save_one.party.pokemon))
        self.assertEqual(1, len(save_two.party.pokemon))

        self.assertEqual(165, save_one.party.pokemon[0].species_id)
        self.assertEqual(176, save_two.party.pokemon[0].species_id)

        self.assertEqual("Charlie", save_one.party.pokemon[0].ot_name)
        self.assertEqual("Bill", save_two.party.pokemon[0].ot_name)

    def test_trade_evolution(self):
        save_one = SaveData()
        save_one.party.pokemon = [PokemonIsolated()]
        save_one.party.pokemon[0].species_id = POKEMON_BY_INDEX.index("Graveler")
        save_one.party.pokemon[0].ot_name = "Bill"
        save_one.party.pokemon[0].nickname = "GRAVELER"
        save_one.party.pokemon[0].level = 15

        save_two = SaveData()
        save_two.party.pokemon = [PokemonIsolated()]
        save_two.party.pokemon[0].species_id = POKEMON_BY_INDEX.index("Machoke")
        save_two.party.pokemon[0].ot_name = "Charlie"
        save_two.party.pokemon[0].nickname = "MACHOKE"
        save_two.party.pokemon[0].level = 15

        trade_pokemon(0, 0, save_one, save_two)

        self.assertEqual(1, len(save_one.party.pokemon))
        self.assertEqual(1, len(save_two.party.pokemon))

        self.assertEqual(
            POKEMON_BY_INDEX.index("Machamp"), save_one.party.pokemon[0].species_id
        )
        self.assertEqual(
            POKEMON_BY_INDEX.index("Golem"), save_two.party.pokemon[0].species_id
        )

        self.assertEqual("Charlie", save_one.party.pokemon[0].ot_name)
        self.assertEqual("Bill", save_two.party.pokemon[0].ot_name)

        self.assertEqual("MACHAMP", save_one.party.pokemon[0].nickname)
        self.assertEqual("GOLEM", save_two.party.pokemon[0].nickname)

        self.assertIn(pokedex_index_of("Machoke"), save_one.pokemon_owned)
        self.assertIn(pokedex_index_of("Machoke"), save_two.pokemon_owned)
        self.assertIn(pokedex_index_of("Graveler"), save_one.pokemon_owned)
        self.assertIn(pokedex_index_of("Graveler"), save_two.pokemon_owned)
        self.assertIn(pokedex_index_of("Machamp"), save_one.pokemon_owned)
        self.assertIn(pokedex_index_of("Machamp"), save_two.pokemon_owned)
        self.assertIn(pokedex_index_of("Golem"), save_one.pokemon_owned)
        self.assertIn(pokedex_index_of("Golem"), save_two.pokemon_owned)


class TestBitfield(unittest.TestCase):
    def testStatusCondition(self):
        self.assertEqual(StatusCondition.NONE, StatusCondition(0))
        self.assertEqual(StatusCondition(0b00000100), StatusCondition.SLEEP)
        self.assertEqual(StatusCondition(0b00001000), StatusCondition.POISON)
        self.assertEqual(StatusCondition(0b00010000), StatusCondition.BURN)
        self.assertEqual(StatusCondition(0b00100000), StatusCondition.FREEZE)
        self.assertEqual(StatusCondition(0b01000000), StatusCondition.PARALYSIS)
