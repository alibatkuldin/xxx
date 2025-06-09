def find_abonnent(data, abonnent):
    for val in data:
        if val.get("phoneNumber", None) == abonnent:
            return val
    print("Номер не найден в базе данных оператора")