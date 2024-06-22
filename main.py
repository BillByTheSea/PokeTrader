import argparse
from src.save_data import PartyData, Pokemon, checksum, trade_pokemon


def validate_args(save_file_one, save_file_two):
    with open(save_file_one, "rb") as file:
        save_data_one = file.read()
    with open(save_file_two, "rb") as file:
        save_data_two = file.read()
    return bytearray(save_data_one), bytearray(save_data_two)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("save_file_one", help="The first save file to read")
    parser.add_argument("save_file_two", help="The second save file to read")
    args = parser.parse_args()

    save_data_one, save_data_two = validate_args(args.save_file_one, args.save_file_two)
    party_one = PartyData(save_data_one)
    party_two = PartyData(save_data_two)

    print(
        "Welcome to the CLI PokeTrader! This tool allows you to trade Pokemon between two save files."
    )
    print("The Pokemon in the first save file are:")
    print(str(party_one))
    print("Which Pokemon would you like to trade?")
    pokemon_one_index = int(input())
    while pokemon_one_index < 1 or pokemon_one_index > party_one.num_pokemon:
        pokemon_one_index = int(
            input(f"Enter a number between 1 and {party_one.num_pokemon}: ")
        )
    pokemon_one_index = pokemon_one_index - 1

    print("The Pokemon in the second save file are:")
    print(str(party_two))
    print("Which Pokemon would you like to trade?")
    pokemon_two_index = int(input())
    while pokemon_two_index < 1 or pokemon_two_index > party_two.num_pokemon:
        pokemon_two_index = int(
            input(f"Enter a number between 1 and {party_two.num_pokemon}: ")
        )
    pokemon_two_index = pokemon_two_index - 1

    print(
        f"Trading {party_one.pokemon(pokemon_one_index).species} (Level {party_one.pokemon(pokemon_one_index).level}) for {party_two.pokemon(pokemon_two_index).species} (Level {party_two.pokemon(pokemon_two_index).level})"
    )
    save_data_one, save_data_two = trade_pokemon(
        pokemon_one_index, pokemon_two_index, party_one, party_two
    )
    save_data_one[0x3523] = checksum(save_data_one)
    save_data_two[0x3523] = checksum(save_data_two)
    with open(args.save_file_one, "wb") as file:
        file.write(save_data_one)
    with open(args.save_file_two, "wb") as file:
        file.write(save_data_two)


if __name__ == "__main__":
    main()
