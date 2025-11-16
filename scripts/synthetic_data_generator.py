import random, string

def random_aadhaar():
    return str(random.randint(2,9)) + ''.join(str(random.randint(0,9)) for _ in range(11))

def random_pan():
    return ''.join(random.choices(string.ascii_uppercase, k=5)) + \
           ''.join(random.choices(string.digits, k=4)) + \
           random.choice(string.ascii_uppercase)
# ...add more generators...
def random_passport():
    return random.choice('A-PR-WY') + ''.join(random.choices(string.digits, k=7))

def random_dl():
    state = ''.join(random.choices(string.ascii_uppercase, k=2))
    rto = ''.join(random.choices(string.digits, k=2))
    num = ''.join(random.choices(string.digits, k=11))
    return f"{state}{rto}{num}"

if __name__ == "__main__":
    print("Aadhaar:", random_aadhaar())
    print("PAN:", random_pan())
    print("Passport:", random_passport())
    print("DL:", random_dl())
