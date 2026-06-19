#  Python Game Collection

A collection of terminal-based board and card games built from scratch in Python — no libraries, no frameworks, just logic, randomness, and progressively more complex bot intelligence.

---

## Games

###  Snakes & Ladders

Two versions, each a meaningful step up from the last.

**`Snakes_and_Ladders.py`** — The original. Static board with hardcoded snake and ladder positions, a standard random die, and a simple two-player + bot setup. Clean, functional, and the foundation everything else was built on.

**`Snake_and_ladders_dynamic.py`** — A full redesign. The board regenerates every game — snake heads and ladder bases are placed randomly, so no two sessions are the same. The die is also replaced with a custom `randomizer()` function that pipes your input through one of five mathematical functions (sigmoid, arctan, tanh, sine, or a piecewise linear curve) to produce a result. You're technically always rolling a fair 1–6, but *what you type influences the outcome* — a deliberate design choice to make the input feel less mechanical.

Both versions require a player to roll a 1 before they can enter the board.

---

###  UNO

Two versions, with a significant jump in bot sophistication between them.

**`UNO.py`** — The first attempt. Card distribution, a working play/draw loop, basic wild card handling, and a bot that scans its hand for any legal card and plays the first one it finds. Functional but naive — the bot has no preference system.

**`Working_UNO.py`** — A full rebuild with a proper bot brain.

#### Bot Architecture

The bot evaluates every legal card using a weighted utility function before playing:

```
Utility = (W_color_bias × color_match) + (W_power × is_action_card) + (W_power × W_panic × opponent_near_win)
```

A noise term is added on top to simulate human inconsistency — the amount of noise depends on the selected difficulty.

Three difficulty profiles are available at startup:

| Profile | Description |
|---|---|
| **Casual Friend** | High noise, low weights — plays loosely and makes mistakes |
| **Adaptive Opponent** | Moderate settings that shift based on match outcomes |
| **Grandmaster Bot** | Near-zero noise, maximally weighted — close to optimal play |

#### Adaptive Mode

In Adaptive mode, the bot's noise factor and panic weight update after each match. A win slightly relaxes its focus; a loss sharpens it. This means the bot calibrates to your level over multiple sessions.

#### Match Journaling

Every bot turn is logged — card evaluated, utility score breakdown, favorite color bias, and hand sizes at the time of the decision. At the end of each game, the full match timeline is exported to `uno_bot_journals/bot_match_log.json`. Useful for reviewing why the bot made a particular play.

---

## Project Structure

```
Python-Game-Collection/
│
├── Snakes_and_Ladders.py          # Original static board version
├── Snake_and_ladders_dynamic.py   # Dynamic board + math-based die
│
├── UNO.py                         # First UNO implementation
├── Working_UNO.py                 # Full rebuild with bot brain and journaling
│
└── uno_bot_journals/              # Created automatically on first UNO match
    └── bot_match_log.json
```

---

## Running the Games

No dependencies beyond the Python standard library.

```bash
python Snakes_and_Ladders.py
python Snake_and_ladders_dynamic.py
python UNO.py
python Working_UNO.py
```

Python 3.7+ recommended.

---

## Design Notes

These games were built iteratively — each version exists because the previous one had a ceiling worth breaking through. The dynamic Snakes & Ladders board removes the familiarity advantage of a fixed layout. The UNO bot's utility scoring replaces random card selection with something that at least models *preference*, even if it isn't full lookahead. The noise factor is the most deliberate design element: a completely deterministic bot is boring to play against, but a completely random one isn't satisfying either — the noise keeps it feeling like an opponent rather than a coin flip.

---

*Built by [@itzvarunv](https://github.com/itzvarunv)*
