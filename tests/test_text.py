from src import text
import unittest
import string


class TestText(unittest.TestCase):
    pokii_chars = string.ascii_letters + string.digits + "():;[]'-?!.$/♂♀"

    def test_round_trip(self):
        for char in self.pokii_chars:
            self.assertEqual(char, text.pokii_to_ascii(text.ascii_to_pokii(char)))

    def test_length_too_small(self):
        with self.assertRaises(ValueError):
            text.ascii_string_to_pokii_string(
                "abc", length=3
            )  # Need room for null terminator

    def test_ascii_to_pokii_includes_terminator(self):
        pokii_string = text.ascii_string_to_pokii_string("abc", length=5)
        self.assertEqual(pokii_string[3], 0x50)
