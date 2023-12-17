from random import randint
import time #Создание иллюзии игры с реальным пользователем
# Классы исключений
# Общий класс исключений
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы доски!'

class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'

class BoardWrongShipException(BoardException):
    pass

# Обозначаем класс для точек (значений)
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # добавляем метод сравнения
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # выводим точки в консоль
    def __repr__(self):
        return f'Dot({self.x},{self.y})'

# создаем класс корабля, в котором будут указываться точки, из которых состоит корабль
# точки по координатам, длина, ориентация (0 - горизонталь/1 -вертикаль)
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    # определение точек корабля с шагом от его начала
    @property
    def dots(self):
        ship_dots = []
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

# Создаем класс игрового поля
class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        # счетчик пораженных кораблей
        self.count = 0

        # сетка поля, где будет храниться состояние
        self.field = [['0'] * size for _ in range(size)]

        # занятые поля (либо стоит корабль, либо был выстрел)
        self.busy = []
        self.ships = []

    #Добавление корабля на доску
    # 1 -  метод для размещения корабля
    # с проверкой что никакая точка не занята и не выходит за границы поля
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship) #добавление собственных кораблей
        self.contour(ship) #Указание контуров кораблей

        # 2 - метод - назначение соседних точек вокруг основной, в которые нельзя будет расставить корабли
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:  # Клетки вокруг корабля, которые нельзя занять по правилам, будут обознаены точкой
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' | '

        if self.hid:
            res = res.replace('■', '0')
        return res

    # проверка нахождения точки в пределах доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))


    # Добавление метода стрельбы
    # Проверка исключений (если корабль размещен за пределами/точка занята)
    def shot(self, d):
        if self.out(d):
            raise BoardOutException

        if d in self.busy:
            raise BoardUsedException

        #Если точка занята - пройтись по циклу
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1 #Если выстрел попадает в корабль - уменьшение количества жизней
                self.field[d.x][d.y] = 'x' #Ставится "х" - поражение точки
                if ship.lives == 0: #Если счетчик жизней корабля = 0
                    self.count +=1 #К счетчику уничтоженных кораблей добавляется новый
                    self.contour(ship, verb = True) #Будут обозначены точки вокруг корабля, чтобы туда нельзя было делать выстрел
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True #Возвращаем true, чтобы можно было сделать повторный ход

        self.field[d.x][d.y] = 'T' #Если промах - будет размещен символ "Т"
        print('Промах!')
        return False

    #Обнуление списка в начале игры
    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

# Добавление класса Игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try: # Попытка сделать выстрел при необходимости повторить его
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# Создание класса "Игрок-компьютер" через наследование
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x+1} {d.y+1}')
        return d

# Создание класса "Игрок - человек"
class User(Player):
    def ask(self):
        # Запрос координат с проверкой
        while True:
            cords = input('Ваш ход:   ').split()

            if len(cords) != 2: #Если игрок ввел некорректное количество координат
                print('Введите две координаты!')
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()): #Если игрок ввел не числовые значения
                print('Введите числа!')
                continue

            x, y = int(x), int(y)

            # Индексация нумерации для пользователя (с единицы)
            return Dot(x-1, y-1)

# Класс игры
class Game:
    # Создание конструктора игры
    def __init__(self, size = 6):
        self.size = size
        # Генерация случайных досок для компьютера и игрока
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        # Создание игроков с передачей сгенерированных досок
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    # Создание игровой доски
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # Указание количества кораблей
        board = Board(size = self.size)
        attempts = 0
        # Расстановка кораблей
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

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    #Создание приветствия
    def greet(self):
        print('---------------------')
        print('  Добро пожаловать  ')
        print('      в игру      ')
        print('    морской бой!     ')
        print('---------------------')
        print('---------------------')
        print(' Формат ввода: x y')
        print('x - номер строки')
        print('y - номер столбца')
        print('---------------------')
        print('  Успехов в игре!  ')

    # Создание игрового цикла
    def loop(self):
        # Задается номер хода
        num = 0
        while True:
            print('-'*20)
            print('Доска пользователя: ')
            print(self.us.board)
            print('-'*20)
            print('Доска компьютера: ')
            print(self.ai.board)
            print('-'*20)
            # Обозначение ходов: если четный - ход пользователя; нечетный - ход компьютера
            if num % 2 == 0:
                print('Ход пользователя!')
                repeat = self.us.move() # Можно ли повторить ход
            else:
                print('Компьютер думает . . . ')
                time.sleep(4)
                print('Ход компьютера!')
                repeat = self.ai.move() # Можно ли повторить ход
            if repeat: # Уменьшение номера хода в связи с повтором хода
                num -= 1

            if self.ai.board.defeat():
                print('-'*20)
                print('Пользователь победил!')
                break

            if self.us.board.defeat():
                print('-'*20)
                print('Компьютер победил!')
                break
            num += 1

    # Старт игры
    def start(self):
        self.greet()
        self.loop()

# начало игры
g = Game()
g.start()