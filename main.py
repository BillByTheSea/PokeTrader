import argparse
from src.save_data import (
    SaveData,
    read_save_data,
    enumerate_party,
    trade_pokemon,
    update_save_data,
)


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
    save_one = read_save_data(save_data_one)
    save_two = read_save_data(save_data_two)

    print(
        "Welcome to the CLI PokeTrader! This tool allows you to trade Pokemon between two save files."
    )
    print("The Pokemon in the first save file are:")
    print(enumerate_party(save_one.party))
    print("Which Pokemon would you like to trade?")
    pokemon_one_index = int(input())
    num_pokemon = len(save_one.party.pokemon)
    while pokemon_one_index < 1 or pokemon_one_index > num_pokemon:
        pokemon_one_index = int(input(f"Enter a number between 1 and {num_pokemon}: "))
    pokemon_one_index = pokemon_one_index - 1

    print("The Pokemon in the second save file are:")
    print(enumerate_party(save_two.party))
    print("Which Pokemon would you like to trade?")
    pokemon_two_index = int(input())
    num_pokemon = len(save_two.party.pokemon)
    while pokemon_two_index < 1 or pokemon_two_index > num_pokemon:
        pokemon_two_index = int(input(f"Enter a number between 1 and {num_pokemon}: "))
    pokemon_two_index = pokemon_two_index - 1

    pokemon_one = save_one.party.pokemon[pokemon_one_index]
    pokemon_two = save_two.party.pokemon[pokemon_two_index]
    print(
        f"Trading {pokemon_one.nickname} (Level {pokemon_one.level}) for \
{pokemon_two.nickname} (Level {pokemon_two.level})"
    )
    trade_pokemon(pokemon_one_index, pokemon_two_index, save_one, save_two)

    save_data_one = update_save_data(save_one, save_data_one)
    save_data_two = update_save_data(save_two, save_data_two)

    save_one = read_save_data(save_data_one)
    save_two = read_save_data(save_data_two)

    with open(args.save_file_one, "wb") as file:
        file.write(save_data_one)
    with open(args.save_file_two, "wb") as file:
        file.write(save_data_two)


if __name__ == "__main__":
    main()
