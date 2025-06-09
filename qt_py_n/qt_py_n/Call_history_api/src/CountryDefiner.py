import json

def identify_country_by_prefix(phone_number):
    with open('country_codes.json', 'r', encoding='utf-8') as file:
        country_prefixes = json.load(file)
    for country, prefixes in country_prefixes.items():
        for prefix in prefixes:
            if phone_number.startswith(prefix):
                return country, prefix
    print("Неизвестный код страны")
    return None