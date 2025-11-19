import random


class Die:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)


class Player:
    def __init__(self, name, num_dice):
        self.name = name
        self.dice = [Die() for _ in range(num_dice)]
        self.last_roll = []

    def roll_dice(self):
        roll_results = []
        for dice in self.dice:
            roll_results.append(dice.roll())
        self.last_roll = roll_results
        return roll_results

    def get_total(self):
        if not self.last_roll:
            return 0

        total = 0
        for result in self.last_roll:
            total += result
        return total


class Game:
    def __init__(self, name1, name2, num_dice):
        self.player_1 = Player(name1, num_dice)
        self.player_2 = Player(name2, num_dice)
        self.p1_score = 0
        self.p2_score = 0

    def play_round(self):

        p1_rolls = self.player_1.roll_dice()
        p2_rolls = self.player_2.roll_dice()

        print(
            f"{self.player_1.name} rolled {p1_rolls} (Total: {self.player_1.get_total()})"
        )
        print(
            f"{self.player_2.name} rolled {p2_rolls} (Total: {self.player_2.get_total()})"
        )

        if self.player_1.get_total() > self.player_2.get_total():
            print(f"{self.player_1.name} has won!")
            self.p1_score += 1
        elif self.player_2.get_total() > self.player_1.get_total():
            print(f"{self.player_2.name} has won!")
            self.p2_score += 1
        else:
            print("Its a tie!")


player1 = input("Please input player ones name")

player2 = input("Please input player twos name")

while True:
    dice_count = input("Please choose number of dice wanted")
    try:
        dice_count = int(dice_count)
        if dice_count >= 1:
            break
        else:
            dice_count = input("Please choose a number larger then 1")
    except ValueError:
        print("Please enter a valid number")


game = Game(player1, player2, dice_count)

while True:
    game.play_round()
    print(
        f"{player1} has a total of {game.p1_score} wins \n{player2} has a total of {game.p2_score} wins \nYou have played a total of {game.p1_score + game.p2_score} rounds"
    )
    while True:
        play_again = input("Play again? (y/n)").strip().upper()

        if play_again in ("YES", "Y"):
            break
        elif play_again in ("NO", "N"):
            print("Thank you for playing")
            exit()
        else:
            print("Wrong input, please try again")
            continue
