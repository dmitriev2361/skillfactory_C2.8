

print("Начало игры")
print(input("Если игрок готов, наберите Yes:   "))
print("""Формат ввода:
 x - номер строки  
 y - номер столбца 
 цифры вводятся через пробел""")
print(input('Введите Yes и делайте выстрел:    '))


from random import randint


class Dot:  # Класс точек на поле
    def __init__(self, x, y):  # Каждая точка описыается параметрами
        self.x = x  # Координата по оси x
        self.y = y  # Координата по осим y

    def __eq__(self, other):  # Проверака точек на равенство
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # информация о точке
        return f"({self.x}, {self.y})"


# Классы исключений

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Уже стреляли в эту клетку. Повтор."


class BoardWrongShipException(BoardException):
    pass


class Ship:  # Корабль на игровом поле
    def __init__(self, bow, l, o):
        self.bow = bow  # Нос корабля
        self.l = l  # Длина корабля равная количеству палуб
        self.o = o  # Ориентация 0 - горизонт, 1 - вертикаль.
        self.lives = l  # Количество жизней равно количеству палуб

    @property
    def dots(self):  # Возвращает список точек корабля
        ship_dots = []  # Список точек корабля
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size  # Размер
        self.hid = hid  # Сокрытие

        self.count = 0  # Счёт

        self.field = [["O"] * size for _ in range(size)]  # Строка с нулями

        self.busy = []  # Живые корабли
        self.ships = []  # Список кораблей

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # Присвоение элементу строки
                                         # обозначения живого корабля
            self.busy.append(d)          # Вносит в список живых кораблей

        self.ships.append(ship)  # Добавление в список кораблей
        self.contour(ship)       # Использование метода contour
                                 # для пометки соседних точек

    def contour(self, ship, verb=False):  # Контур, где корабля быть не может
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):                                       # Игровая доска
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):                                                   # Контроль точки
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)                                       # Добавляем в список

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль убит!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:                                             # Игрющая сторона_алгоритм
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):                                             # Компьютер
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):                                         # Игрок_интерфейс
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:                                       # Условия игры
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board


    def loop(self):                                            # Отображение на досках
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Вы выиграли!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.loop()

g = Game()
g.start()