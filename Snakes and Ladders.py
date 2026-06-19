import random
import time

print("Welcome to Snakes and Laddeders")
print("Select 1 to start")
print("Any key to exit")
print()

ch1 = int(input("What do you choose? "))

def assets():
    snakes = [[70,1], [11,4], [45,35], [27,16], [98, 12]]
    ladders = [[5,12], [35,54], [52, 87]]
    return snakes, ladders

def play(number, player):
    snakes, ladders = assets()
    print(f"Player {number} to play!")
    roll = input("Roll(y/n)? ")
    exits = False
    if roll == "y":
        die = random.randint(1,6)
        player += die
        for snake in snakes:
            if snake[0] == player:
                print("Oops you got bit by a snake!")
                player = snake[1]
                break
            else:
                pass
        for ladder in ladders:
            if ladder[0] == player:
                print("Woah you got a ladder!")
                player = ladder[1]
                break
            else:
                pass
        if player > 100:
            print("Need any other number crossing 100")
            player -= die
        else:
            pass
        print(f"Current position is {player}!")
        print()
    else:
        print("Exiting...")
        exits = True
    time.sleep(0.7)
    return player, exits

def botPlay(bot):
    snakes, ladders = assets()
    print("Bot to play!")
    die = random.randint(1,6)
    bot += die
    for snake in snakes:
        if snake[0] == bot:
            print("Oops bot got bit by a snake!")
            bot = snake[1]
            break
        else:
            pass
    for ladder in ladders:
        if ladder[0] == bot:
            print("Woah bot got a ladder!")
            bot = ladder[1]
            break
        else:
            pass
    if bot > 100:
        print("Bot needs any other number crossing 100")
        bot -= die
    else:
        pass
    print(f"Current position of bot is {bot}!")
    print()
    time.sleep(0.5)
    return bot

def won(player):
    win = False
    if player == 100:
        print("You won!")
        win = True
    else:
        pass
    return win

if ch1 == 1:
    print("The rules are simple avoid snakes and get ladder!")
    print("Mode 2 offline players and 1 bot")
    player1 = 0
    player2= 0
    bot = 0
    while True:
        number = 1
        player1,exits = play(number,player1)
        if exits == True:
            break
        else:
            pass
        win = won(player1)
        if win == True:
            print("Game Over")
            break
        else:
            pass
        number = 2
        player2, exits = play(number, player2)
        if exits == True:
            break
        else:
            pass
        win = won(player2)
        if win == True:
            print("Game Over")
            break
        else:
            pass
        bot = botPlay(bot)
        win = won(bot)
        if win == True:
            print("Game Over")
            break
        else:
            pass

else:
    print("Exiting...")
    
    
