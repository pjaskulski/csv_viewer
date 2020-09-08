from random import randint


def gen_int(filename, rows, cols):
    """Generuje plik z danymi typu integer"""
    with open(filename, "w") as f:
        # column name
        for col in range(1, cols + 1):
            if col == cols:
                f.write(f"col_{col}")
            else:
                f.write(f"col_{col},")
        f.write("\n")

        # data
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                # brak danych dla ok 10% komórek
                if randint(1, 11) != 10:
                    liczba = str(randint(1, 100))
                else:
                    liczba = ""

                if j == cols:
                    f.write(liczba)
                else:
                    f.write(f"{liczba},")
            f.write("\n")


gen_int("dane.csv", 100000, 10)
