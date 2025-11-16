import re

def verhoeff_validate(number: str) -> bool:
    # Verhoeff algorithm tables
    d = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,2,3,4,0,6,7,8,9,5],
        [2,3,4,0,1,7,8,9,5,6],
        [3,4,0,1,2,8,9,5,6,7],
        [4,0,1,2,3,9,5,6,7,8],
        [5,9,8,7,6,0,4,3,2,1],
        [6,5,9,8,7,1,0,4,3,2],
        [7,6,5,9,8,2,1,0,4,3],
        [8,7,6,5,9,3,2,1,0,4],
        [9,8,7,6,5,4,3,2,1,0]
    ]
    p = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,5,7,6,2,8,3,0,9,4],
        [5,8,0,3,7,9,6,1,4,2],
        [8,9,1,6,0,4,3,5,2,7],
        [9,4,5,3,1,2,6,8,7,0],
        [4,2,8,6,5,7,3,9,0,1],
        [2,7,9,3,8,0,6,4,1,5],
        [7,0,4,6,9,1,3,2,5,8]
    ]
    inv = [0,4,3,2,1,5,6,7,8,9]
    c = 0
    number = number.replace(' ', '')
    if not number.isdigit() or len(number) != 12:
        return False
    for i, item in enumerate(reversed(number)):
        c = d[c][p[i % 8][int(item)]]
    return c == 0

def pan_format(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", value))

def passport_format(value: str) -> bool:
    return bool(re.match(r"^[A-PR-WY][0-9]{7}$", value))

def dl_format(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}[0-9]{2}\s?[0-9]{11,12}$", value))
