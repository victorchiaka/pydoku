from math import sqrt, floor
import random


class Generator:
    def __init__(self, difficulty: str, size: int = 9) -> None:
        self.difficulty: str = difficulty
        self.size: int = size
        self.board: list[list[int | str]] = [
            [0 for _ in range(self.size)] for _ in range(self.size)
        ]
        self.number_to_char = {
            10: "10",
            11: "A",
            12: "B",
            13: "C",
            14: "D",
            15: "E",
            16: "F",
        }
        self.char_to_number: dict[str, int] = {
            v: k for k, v in self.number_to_char.items()
        }

    def is_number_in_row(self, number: int | str, row: int) -> bool:
        return number in self.board[row]

    def is_number_in_column(self, number: int | str, column: int) -> bool:
        for i in range(self.size):
            if self.board[i][column] == number:
                return True
        return False

    def is_number_in_subgrid(self, number: int | str, row: int, column: int) -> bool:
        subgrid_row_size: int = 0
        subgrid_col_size: int = 0
        subgrid_size: int = 0

        if self.size == 6:
            subgrid_row_size, subgrid_col_size = 2, 3
        else:
            subgrid_size = floor(sqrt(self.size))
            subgrid_row_size, subgrid_col_size = subgrid_size, subgrid_size

        subgrid_row = row - row % subgrid_row_size
        subgrid_column = column - column % subgrid_col_size

        for row in range(subgrid_row, subgrid_row + subgrid_size):
            for column in range(subgrid_column, subgrid_column + subgrid_size):
                if self.board[row][column] == number:
                    return True
        return False

    def is_valid_position(self, number: int | str, row: int, column: int) -> bool:
        return (
            not self.is_number_in_row(number=number, row=row)
            and not self.is_number_in_column(number=number, column=column)
            and not self.is_number_in_subgrid(number=number, row=row, column=column)
        )

    def populate_numbers_in_board(self) -> bool:
        for row in range(self.size):
            for column in range(self.size):
                if self.board[row][column] == 0:
                    numbers = (
                        list(range(1, 10)) + list(self.number_to_char.values())
                        if self.size == 16
                        else list(range(1, self.size + 1))
                    )
                    random.shuffle(numbers)
                    for number in numbers:
                        if self.is_valid_position(
                            number=number, row=row, column=column
                        ):
                            self.board[row][column] = number
                            if self.populate_numbers_in_board():
                                return True
                            self.board[row][column] = 0
                    return False
        return True

    def remove_numbers_at_random_positions(self, limit: int) -> None:
        while limit > 0:
            row: int = random.randint(0, self.size - 1)
            column: int = random.randint(0, self.size - 1)
            if self.board[row][column] != 0:
                self.board[row][column] = 0
                limit -= 1

    def generate_limit(self) -> int:
        limit: int = 0
        if self.difficulty.upper() == "EASY":
            match self.size:
                case 6:
                    limit = random.randint(8, 11)
                case 9:
                    limit = random.randint(20, 27)
        elif self.difficulty.upper() == "MEDIUM":
            match self.size:
                case 6:
                    limit = random.randint(11, 15)
                case 9:
                    limit = random.randint(28, 37)
                case 16:
                    limit = random.randint(58, 77)
        elif self.difficulty.upper() == "HARD":
            match self.size:
                case 6:
                    limit = random.randint(15, 18)
                case 9:
                    limit = random.randint(38, 47)
                case 16:
                    limit = random.randint(78, 97)
        elif self.difficulty.upper() == "EXPERT":
            match self.size:
                case 6:
                    limit = random.randint(18, 20)
                case 9:
                    limit = random.randint(48, 57)
                case 16:
                    limit = random.randint(98, 117)
        return limit

    def generate_board(self) -> list[list[int | str]]:
        self.populate_numbers_in_board()

        self.remove_numbers_at_random_positions(limit=self.generate_limit())
        return self.board
