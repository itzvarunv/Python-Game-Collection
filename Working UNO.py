import random
import json
import os

# ==========================================
# 1. BASE SETUP & DECK GENERATION
# ==========================================
red = ["Red"] + [f"Red {i}" for i in range(1, 11)] + ["Red Skip"] * 2 + ["Red Reverse"] * 2 + ["Red +2"] * 2
blue = ["Blue"] + [f"Blue {i}" for i in range(1, 11)] + ["Blue Skip"] * 2 + ["Blue Reverse"] * 2 + ["Blue +2"] * 2
green = ["Green"] + [f"Green {i}" for i in range(1, 11)] + ["Green Skip"] * 2 + ["Green Reverse"] * 2 + ["Green +2"] * 2
yellow = ["Yellow"] + [f"Yellow {i}" for i in range(1, 11)] + ["Yellow Skip"] * 2 + ["Yellow Reverse"] * 2 + ["Yellow +2"] * 2

wild_cards = ["Wild Card (Color Change)"] * 4 + ["Wild Draw Four (+4 & Color Change)"] * 4
same_turn_cards = red[12:] + blue[12:] + green[12:] + yellow[12:]

pack = red[1:] + blue[1:] + green[1:] + yellow[1:] + wild_cards

# Bot Configuration (With Human Valuation Noise instead of random skips)
# Multi-Tier Strategy Configuration Profiles
DIFFICULTY_MODES = {
    "1": {"name": "Casual Friend", "W_color_bias": 1.5, "W_power": 1.0, "W_panic": 0.5, "noise_factor": 2.5},
    "2": {"name": "Adaptive Opponent", "W_color_bias": 3.0, "W_power": 2.5, "W_panic": 1.8, "noise_factor": 1.5},
    "3": {"name": "Grandmaster Bot", "W_color_bias": 4.5, "W_power": 4.0, "W_panic": 3.0, "noise_factor": 0.3}
}

# Default Active Configuration Setup
bot_weights = {}
selected_mode = "2" # Will be set dynamically by player at startup
# ==========================================
# 2. CORE BACKEND FUNCTIONS
# ==========================================
def draw_card(deck):
    if not deck:
        return None, deck
    random_idx = random.randint(0, len(deck) - 1)
    return deck.pop(random_idx), deck

def recycle_discard_pile(deck, stash):
    if len(deck) < 5 and len(stash) > 1:
        top_card = stash[-1]
        cards_to_recycle = stash[:-1]
        cleaned_recycle = [c for c in cards_to_recycle if c not in ["Red", "Blue", "Green", "Yellow"]]
        deck.extend(cleaned_recycle)
        stash = [top_card]
        random.shuffle(deck)
        print(f"\n[System] Deck running low! Recycled {len(cleaned_recycle)} cards.")
    return deck, stash

def get_legal_moves(hand, top_card):
    legal_cards = []
    top_color = None
    for color in ["Red", "Blue", "Green", "Yellow"]:
        if top_card.startswith(color):
            top_color = color

    top_value_suffix = top_card[-2:]
    is_top_same_turn = top_card in same_turn_cards

    for card in hand:
        if "Wild" in card:
            legal_cards.append(card)
            continue
        if top_color and card.startswith(top_color):
            legal_cards.append(card)
            continue
        if is_top_same_turn and card in same_turn_cards:
            if card[-2:] == top_value_suffix:
                legal_cards.append(card)
                continue
        if not is_top_same_turn and card[-2:] == top_value_suffix:
            legal_cards.append(card)
            continue
    return legal_cards

def decide_next_state(played_card, current_turn, player_hand, bot_hand, deck):
    opponent = "bot" if current_turn == "player" else "player"
    opp_hand = bot_hand if current_turn == "player" else player_hand
    
    is_plus_two = played_card in ["Red +2", "Blue +2", "Green +2", "Yellow +2"]
    is_wild_four = "Wild Draw Four" in played_card
    is_same_turn = played_card in same_turn_cards
    
    if is_plus_two or is_wild_four:
        draw_count = 2 if is_plus_two else 4
        print(f"--> Penalty activated! {opponent.capitalize()} draws {draw_count} cards and loses their turn!")
        for _ in range(draw_count):
            if deck:
                card, deck = draw_card(deck)
                if card: opp_hand.append(card)
        next_turn = current_turn  
    elif is_same_turn:
        print(f"--> {played_card.split()[-1]} played! {opponent.capitalize()} is skipped!")
        next_turn = current_turn
    else:
        next_turn = opponent

    if current_turn == "player":
        return deck, player_hand, opp_hand, next_turn
    else:
        return deck, opp_hand, bot_hand, next_turn

# ==========================================
# 3. BOT BRAIN WITH SNAPSHOT JOURNALING
# ==========================================
def bot_turn_backend(bot_hand, top_card, player_hand_size):
    legal_moves = get_legal_moves(bot_hand, top_card)
    if not legal_moves:
        return None, "Draw", {"action": "Draw Card", "reason": "No legal moves available"}

    color_counts = {"Red": 0, "Blue": 0, "Green": 0, "Yellow": 0}
    for card in bot_hand:
        for color in color_counts:
            if card.startswith(color):
                color_counts[color] += 1
    favorite_color = max(color_counts, key=color_counts.get)

    best_card = None
    highest_utility = float('-inf')
    decision_snapshots = {}

    for card in legal_moves:
        is_power = 1.0 if ("Wild" in card or "Skip" in card or "Reverse" in card or "+2" in card) else 0.0
        matches_bias = 1.0 if card.startswith(favorite_color) else 0.0
        panic_factor = 1.0 if player_hand_size <= 2 else 0.0

        # Calculate base strategy utility
        base_utility = (bot_weights["W_color_bias"] * matches_bias) + \
                       (bot_weights["W_power"] * is_power) + \
                       (bot_weights["W_power"] * is_power * bot_weights["W_panic"] * panic_factor)

        if is_power == 0.0 and card[-1].isdigit():
            base_utility += int(card[-1]) * 0.1

        # Add profile noise (Casual mode has massive variation, Grandmaster has almost zero)
        human_noise = random.uniform(-bot_weights["noise_factor"], bot_weights["noise_factor"])
        final_utility = base_utility + human_noise

        decision_snapshots[card] = f"Base: {round(base_utility, 1)} -> Fuzzy: {round(final_utility, 1)}"

        if final_utility > highest_utility:
            highest_utility = final_utility
            best_card = card

    log_entry = {
        "action": f"Played {best_card}",
        "bot_hand_size_at_turn": len(bot_hand),
        "opponent_hand_size_at_turn": player_hand_size,
        "favorite_color_bias": favorite_color,
        "evaluated_utilities": decision_snapshots
    }

    return best_card, favorite_color, log_entry

def save_bot_journal(game_history, match_result):
    log_directory = "uno_bot_journals"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        
    journal_data = {
        "bot_id": "Neural_Bot_v1",
        "match_outcome": match_result,
        "active_weights": bot_weights,
        "game_timeline": game_history
    }
    
    file_path = os.path.join(log_directory, "bot_match_log.json")
    with open(file_path, "w") as f:
        json.dump(journal_data, f, indent=4)
    print(f"\n[System Log] Match data exported successfully to: {file_path}")

def training_adaptation_step(outcome):
    """ Modifies noise dynamically *only* if the player selected Adaptive Mode """
    global bot_weights, selected_mode
    if selected_mode != "2":
        return # Keep weights completely locked for fixed difficulty profiles

    if outcome == "Won against Player":
        bot_weights["W_panic"] = max(1.0, bot_weights["W_panic"] - 0.2)
        bot_weights["noise_factor"] = min(3.0, bot_weights["noise_factor"] + 0.2)
        print(f"[Training Mode] Bot relaxed focus due to winning: Noise Factor={bot_weights['noise_factor']:.2f}")
    elif outcome == "Lost to Player":
        bot_weights["W_panic"] = min(2.5, bot_weights["W_panic"] + 0.1)
        bot_weights["noise_factor"] = max(0.2, bot_weights["noise_factor"] - 0.2)
        print(f"[Training Mode] Bot sharpened focus following a loss: Noise Factor={bot_weights['noise_factor']:.2f}")

# ==========================================
# 4. MAIN ENGINE
# ==========================================
def main_game_loop():
    global bot_weights, selected_mode
    print("==========================================")
    print("      NEURAL-ENGINE UNO CONTROL PANEL     ")
    print("==========================================")
    print("Select Bot Strategy Profile:")
    print(" [1] Casual Friend (Plays loose, easy to beat)")
    print(" [2] Adaptive Opponent (Changes skill based on outcomes)")
    print(" [3] Grandmaster Bot (Flawless, highly mathematical optimization)")
    
    choice = input("Enter Choice (1-3): ").strip()
    if choice in DIFFICULTY_MODES:
        selected_mode = choice
    else:
        selected_mode = "2" # Fallback to adaptive
        
    bot_weights = DIFFICULTY_MODES[selected_mode].copy()
    print(f"\n-> Engine Initialized Profile: [{DIFFICULTY_MODES[selected_mode]['name']}]")

    print("Initializing Custom Neural-Engine UNO pack...")
    deck = pack.copy()
    random.shuffle(deck)
    
    player_hand = []
    bot_hand = []
    stash = []
    game_journal = []  
    
    for _ in range(7):
        c, deck = draw_card(deck); player_hand.append(c)
        c, deck = draw_card(deck); bot_hand.append(c)
        
    while True:
        first_card, deck = draw_card(deck)
        if "Wild" not in first_card:
            stash.append(first_card)
            break
        deck.append(first_card)
        random.shuffle(deck)

    turn = "player"
    print("\n--- Game Setup Complete! Let's Play ---")

    while True:
        if len(player_hand) == 0:
            print("\nCongratulations! You win the game!")
            training_adaptation_step("Lost to Player")
            save_bot_journal(game_journal, "Lost to Player")
            break
        if len(bot_hand) == 0:
            print("\nBot Brain wins the game! Better luck next time.")
            training_adaptation_step("Won against Player")
            save_bot_journal(game_journal, "Won against Player")
            break

        deck, stash = recycle_discard_pile(deck, stash)
        top_card = stash[-1]

        if turn == "player":
            print("\n" + "="*45)
            print(f"=== YOUR TURN === (Bot hand size: {len(bot_hand)})")
            print(f"Top Pile Card: {top_card}")
            print("="*45)
            
            legal_moves = get_legal_moves(player_hand, top_card)
            
            if not legal_moves:
                print("No legal moves! Drawing a card automatically...")
                drawn, deck = draw_card(deck)
                if drawn:
                    player_hand.append(drawn)
                    print(f"-> You drew: {drawn}")
                    legal_moves = get_legal_moves(player_hand, top_card)
                    if not legal_moves:
                        print("Still no valid plays available. Passing turn.")
                        turn = "bot"
                        continue
                else:
                    turn = "bot"
                    continue

            print("\nYour Hand:")
            for idx, card in enumerate(player_hand, 1):
                marker = " * [PLAYABLE]" if card in legal_moves else ""
                print(f"  {idx}. {card}{marker}")
                
            while True:
                try:
                    choice = int(input(f"\nSelect a card number to play (1-{len(player_hand)}): "))
                    if 1 <= choice <= len(player_hand):
                        selected_card = player_hand[choice - 1]
                        if selected_card in legal_moves:
                            player_hand.pop(choice - 1)
                            
                            if "Wild" in selected_card:
                                print("\n--- Wild Card Activated! ---")
                                while True:
                                    color_choice = input("Choose active color (Red/Blue/Green/Yellow): ").strip().capitalize()
                                    if color_choice in ["Red", "Blue", "Green", "Yellow"]:
                                        stash.append(color_choice)
                                        break
                                    print("Invalid color.")
                            else:
                                stash.append(selected_card)
                                
                            deck, player_hand, bot_hand, turn = decide_next_state(selected_card, "player", player_hand, bot_hand, deck)
                            break
                        else:
                            print("Illegal selection! Pick a card with the * symbol.")
                    else:
                        print("Index out of boundaries.")
                except ValueError:
                    print("Invalid option.")

        else:
            print(f"\n--- Bot Brain Analyzing Options... (Your hand size: {len(player_hand)}) ---")
            played_card, favorite_color, log_entry = bot_turn_backend(bot_hand, top_card, len(player_hand))
            
            game_journal.append(log_entry)
            
            if played_card is None:
                print("Bot had no playable cards. Bot draws a card.")
                drawn, deck = draw_card(deck)
                if drawn:
                    bot_hand.append(drawn)
                    played_card, favorite_color, post_draw_log = bot_turn_backend(bot_hand, top_card, len(player_hand))
                    game_journal.append(post_draw_log)
                    
                    if played_card and drawn == played_card:
                        bot_hand.remove(played_card)
                        print(f"Bot drew and immediately plays: {played_card}")
                    else:
                        print("Bot cannot play the drawn card. Turn passes to you.")
                        turn = "player"
                        continue
                else:
                    turn = "player"
                    continue

            if played_card:
                if played_card in bot_hand:
                    bot_hand.remove(played_card)
                print(f"Bot played: {played_card}")
                
                if "Wild" in played_card:
                    stash.append(favorite_color)
                    print(f"Bot chose active color: {favorite_color}")
                else:
                    stash.append(played_card)
                    
                deck, player_hand, bot_hand, turn = decide_next_state(played_card, "bot", player_hand, bot_hand, deck)

if __name__ == "__main__":
    main_game_loop()
