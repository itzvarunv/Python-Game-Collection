import random
import time

print("Let's play UNO!")

# Deck creation
def deck():
    red = [f'Red {str(i).zfill(2)}' for i in range(1, 11)] + ["Red +2"] * 2 + ["Red Reverse"] * 2 + ["Red Skip"] * 2
    blue = [f'Blue {str(i).zfill(2)}' for i in range(1, 11)] + ["Blue +2"] * 2 + ["Blue Reverse"] * 2 + ["Blue Skip"] * 2
    green = [f'Green {str(i).zfill(2)}' for i in range(1, 11)] + ["Green +2"] * 2 + ["Green Reverse"] * 2 + ["Green Skip"] * 2
    yellow = [f'Yellow {str(i).zfill(2)}' for i in range(1, 11)] + ["Yellow +2"] * 2 + ["Yellow Reverse"] * 2 + ["Yellow Skip"] * 2
    wild = ["Wild Card (Color Change)"] * 4 + ["Wild Draw Four Card (+4 & Color Change)"] * 4
    return red, blue, green, yellow, wild

# Draw card
def draw_card(used):
    red, blue, green, yellow, wild = deck()
    all_cards = red + blue + green + yellow + wild
    while True:
        card = random.choice(all_cards)
        if card not in used:
            used.append(card)
            return card, used

# Distribute initial cards

def distribute():
    player = []
    bot = []
    used = []
    for _ in range(8):
        card, used = draw_card(used)
        player.append(card)
    for _ in range(8):
        card, used = draw_card(used)
        bot.append(card)
    return player, bot, used

# Color selection for wild card

def color_change():
    print("Choose a color:")
    print("1. Red  2. Blue  3. Green  4. Yellow")
    while True:
        choice = input("Enter your choice (1-4): ")
        if choice == '1':
            return "Red"
        elif choice == '2':
            return "Blue"
        elif choice == '3':
            return "Green"
        elif choice == '4':
            return "Yellow"
        else:
            print("Invalid choice. Try again.")

# Check if card can be placed

def can_place(top, card):
    if "Wild" in card:
        return True
    return top.split()[0] == card.split()[0] or top.split()[-1] == card.split()[-1]

# Play turn

def play_turn(player, stack, used):
    top = stack[-1]
    print(f"Top card: {top}")
    print("Your cards:")
    for idx, card in enumerate(player):
        print(f"{idx+1}. {card}")
    choice = input("Choose card number to play or 0 to draw: ")
    if choice == '0':
        card, used = draw_card(used)
        player.append(card)
        print(f"You drew: {card}")
        return player, stack, used, False
    else:
        index = int(choice) - 1
        if index >= len(player):
            print("Invalid card number.")
            return player, stack, used, False
        card = player[index]
        if not can_place(top, card):
            print("You can't place this card.")
            return player, stack, used, False
        played_card = player.pop(index)
        if "Wild" in played_card:
            color = color_change()
            stack.append(color)
            if "+4" in played_card:
                for _ in range(4):
                    bot_card, used = draw_card(used)
                    bot.append(bot_card)
                print("Bot draws 4 cards!")
                return player, stack, used, True
        else:
            stack.append(played_card)
        return player, stack, used, False

# Bot logic

def bot_turn(bot, stack, used):
    top = stack[-1]
    for idx, card in enumerate(bot):
        if can_place(top, card):
            played_card = bot.pop(idx)
            if "Wild" in played_card:
                color = random.choice(["Red", "Blue", "Green", "Yellow"])
                stack.append(color)
                if "+4" in played_card:
                    for _ in range(4):
                        player_card, used = draw_card(used)
                        player.append(player_card)
                    print("You draw 4 cards!")
                    return bot, stack, used, True
            else:
                stack.append(played_card)
            print(f"Bot played: {played_card}")
            return bot, stack, used, False
    card, used = draw_card(used)
    bot.append(card)
    print("Bot draws a card.")
    return bot, stack, used, False

# Check win

def check_win(hand, name):
    if len(hand) == 0:
        print(f"{name} wins the game!")
        return True
    return False

# === MAIN GAME LOOP ===
player, bot, used = distribute()
card, used = draw_card(used)
stack = [card]
skip = False

while True:
    player, stack, used, skip = play_turn(player, stack, used)
    if check_win(player, "You"):
        break
    if not skip:
        bot, stack, used, skip = bot_turn(bot, stack, used)
        if check_win(bot, "Bot"):
            break
    skip = False
    time.sleep(0.5)
