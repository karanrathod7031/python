# import random

# target = random.randint(1,100)
# print("if you wanna Quit press 'Q' ")
# attempts = 0
# while True:
#     userChoise = input("  guess the number : ")
#     attempts += 1
#     if (userChoise=="Q"):
#         print("logging out..")
#         break
#     userChoise = int(userChoise)
#     if(userChoise==target):
#         print("you win!!!!!")
#         print("GAME IS OVER")
#         print(f"Correct! You guessed it in --> {attempts} <--attempts.")
#         break
#     elif(userChoise < target):
#         print("your number was to small")
#     else:
#         print("your number was to big")


import random

# Function to play the game
def play_game():
    secret_number = random.randint(1, 5)
    attempts = 0
    
    while True:
        guess = int(input("Guess a number between 1 and 10: "))
        attempts += 1

        if guess == secret_number:
            print(f"🎉 Correct! You guessed it in {attempts} attempts.")
            return True   # Player won
        elif guess < secret_number:
            print("Too low! Try again.")
        else:
            print("Too high! Try again.")

# Main function with win counter
def main():
    wins = 0  # counter for number of wins
    
    while True:
        if play_game():
            wins += 1  # increase win count
            print(f"🏆 You have won {wins} times so far.")

        again = input("Do you want to play again? (0/1): ")
        if again != "1":
            print(f"Game Over. Final wins: {wins}")
            break

main()
