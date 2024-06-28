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
        if self.size == 6:
            subgrid_row_start = (row // 2) * 2
            subgrid_col_start = (column // 3) * 3
            subgrid_row_end = subgrid_row_start + 1
            subgrid_col_end = subgrid_col_start + 2

            for row in range(subgrid_row_start, subgrid_row_end + 1):
                for column in range(subgrid_col_start, subgrid_col_end + 1):
                    if self.board[row][column] == number:
                        return True
            return False
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

    def generate_board(self) -> list[list[int | str]]:
        limit: dict[str, dict[int, int]] = {
            "EASY": {6: random.randint(9, 12), 9: random.randint(20, 27)},
            "MEDIUM": {
                6: random.randint(12, 15),
                9: random.randint(28, 37),
                16: random.randint(58, 77),
            },
            "HARD": {
                6: random.randint(15, 18),
                9: random.randint(38, 47),
                16: random.randint(78, 97),
            },
            "EXPERT": {
                6: random.randint(22, 25),
                9: random.randint(48, 57),
                16: random.randint(98, 117),
            },
        }

        self.populate_numbers_in_board()

        self.remove_numbers_at_random_positions(
            limit=limit[self.difficulty.upper()][self.size]
        )
        return self.board
