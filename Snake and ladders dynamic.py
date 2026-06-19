import random
import math

turn1, turn2, bot , end = False, False, False, False
start1, start2, startb = False, False, False

def assets():
    asset = []
    for i in range (10):
        pos1 = random.randint(2, 95)      # start square for ladder
        pos2 = random.randint(pos1+5, 100)  # end square for ladder
        group = (pos1, pos2)
        asset.append(group)
    for i in range(10):
        pos2 = random.randint(2, 95)      # snake's tail (destination)
        pos1 = random.randint(pos2+5, 100)  # snake's head (starting point)
        group = (pos1, pos2)
        asset.append(group)   
    return asset

def randomizer(number):
    select = random.randint(1, 5)
    if select == 1:
        roll = int(5/(1 + math.exp(-number)) + 1)
    elif select == 2:
        roll = int((5/math.pi) * math.atan(number) + 3.5)
    elif select == 3:
        roll = int(2.5 * math.tanh(number) + 3.5)
    elif select == 4:
        roll = int(2.5 * math.sin(number) + 3.5)
    else:
        if number <= 0:
            roll = 1
        elif number < 1:
            roll = int(1 + 5*number)
        else:
            roll = 6
    print(f"You got {roll} on your die!") 
    return roll

def rotate(turn1, turn2, bot):
    if turn1 == False and turn2 == False and bot == False:
        chance = 1
        turn1 = True
    elif turn1 == True and turn2 == False and bot == False:
        chance = 2
        turn2 = True
    else:
        chance = 3
        turn1, turn2 = False, False
    return turn1, turn2, bot, chance

def play(position, number, asset, end):
    roll = randomizer(number)
    new_position = position + roll
    if new_position > 100:
        print("Exceeding 100 thus invalid play!")
        new_position = position
    elif new_position == 100:
        print("You won the game!")
        end = True
    else:
        for i in asset:
            if asset[0] == new_position:
                new_position == asset[1]
                if asset[1] > asset[0]:
                    print("You got a ladder!")
                else:
                    print("Oh no you got bit by a snake!")
            else:
                pass
        print(f"You current position is {new_position}")
    return new_position, end

def start(position, number, start):
    roll = randomizer(number)
    if roll == 1:
        position = 1
        print("You can start the game!")
        start = True
    else:
        print("You can't proceed yet!")
    return position, start

print("Welcome to the game of snake and ladders!")
print("1 Know the features of this game")
print("2 Start a game")
print("Any integer to exit")
print()

while True:
    try:
        ch1 = int(input("What do you choose? "))
        break
    except:
        print("Please enter a valid integer")
        
if ch1 == 1:
    print("1 The board is created dynamically and thus differs from game to game.")
    print("2 The number you input goes into a random function to create a random fair die for you but what you input matters!")
    print("3 A bot is available for the play")
    print()

elif ch1 == 2:
    print("Let's start the game!")
    asset = assets()
    pos1 = 0
    pos2 = 0
    posb = 0
    while True:
        turn1, turn2, bot, chance = rotate(turn1, turn2, bot)
        if chance == 1:
            print("Player 1 turn")
            while True:
                try:
                    number = int(input("Give any random integer! "))
                    break
                except:
                    print("Please enter a valid integer")
            if start1 == False:
                pos1, start1 = start(pos1,number, start1)
            else:
                pos1, end = play(pos1, number, asset, end)
                if end == True:
                    break
            print()
            
        elif chance == 2:
            print("Player 2 turn")
            while True:
                try:
                    number = int(input("Give any random integer! "))
                    break
                except:
                    print("Please enter a valid integer")
            if start2 == False:
                pos2, start2 = start(pos2,number, start2)
            else:
                pos2, end = play(pos2, number, asset, end)
                if end == True:
                    break
            print()

        else:
            print("Bots turn")
            number = random.randint(-50,50)
            if startb == False:
                posb, startb = start(posb,number, startb)
            else:
                posb, end = play(posb, number, asset, end)
                if end == True:
                    break
            print()
            
        
        
        
    
        
    
    
