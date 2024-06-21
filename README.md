# PokeTrader

The Poketrader is a simple Python script that allows you trade Pokemon between save data of Gen 1 Pokemon games.

To run, simply call `python main.py <save_data_1> <save_data_2>`. You will then be prompted through the rest of the process.

## Will this work with Pokemon Yellow?

Probably? From my understanding of [the save data format](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_I)) it *should* be fine? I don't understand where Pikachu's happiness is stored though, and that worries me.

## Will this work with GSC/RBE/Digimon/Zelda?

No. That will probably ruin your save file. Please don't do this.

## Are trade evolutions supported?

Kind of. For Pokedex purposes, yes. If there any stat adjustments that happen when a Pokemon evolves, that is not yet implemented. 
