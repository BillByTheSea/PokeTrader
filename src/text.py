import string

pokii_table = (
    string.ascii_uppercase
    + "():;[]"
    + string.ascii_lowercase
    + ("_") * 38
    + "'PM-__?!.______♂$_./,♀0123456789"
)


def pokii_to_ascii(char):
    index = char - 0x80
    return pokii_table[index]


def ascii_to_pokii(char):
    index = pokii_table.index(char)
    return index + 0x80


def ascii_string_to_pokii_string(ascii_string, length):
    if len(ascii_string) >= length:
        raise ValueError(
            f"ascii_string is {len(ascii_string)} long, but length is {length}"
        )
    result = bytearray([0x50] * (len(ascii_string) + 1))
    for index, char in enumerate(ascii_string):
        result[index] = ascii_to_pokii(char)
    return result


def pokii_string_to_ascii_string(pokii_string, length):
    result = ""
    for index in range(length):
        char = pokii_string[index]
        if char == 0x50:
            break
        result += pokii_to_ascii(char)
    return result
