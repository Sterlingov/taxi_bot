import random


def random_car():
    colors = ["Желтый", "Серый", "Черный", "Белый"]
    alphas = ["А", "В", "Е", "К", "М", "Н", "О", "Р", "С", "Т", "У", "Х"]
    cars = ["Toyota", "Kia", "Skoda", "Volkswagen", "Renault", "Ford", "Hyundai", "Chevrolet"]

    return f"{random.choice(colors)} {random.choice(cars)}\nНомер: {random.choice(alphas)}{random.randint(100,1000)}" \
           f"{random.choice(alphas)}{random.choice(alphas)}"
