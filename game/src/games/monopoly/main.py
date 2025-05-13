# main.py
import pygame
import random
import time
import copy
from game_components import Property, Player
from board import Board
from deck import Deck  # Corrected import statement

def create_board():
    """Creates the game board with properties, including Hotel, Clue, Inkognito, and Ocean Trader spaces."""
    properties = [
        Property("Go", 0, 0, buildable=False),
        Property("Mediterranean Avenue", 60, 2, group="Brown"),
        Property("Community Chest", 0, 0, buildable=False),
        Property("Baltic Avenue", 60, 4, group="Brown"),
        Property("Income Tax", 0, 0, buildable=False),
        Property("Reading Railroad", 200, 25, buildable=False, group="Railroad"),
        Property("Oriental Avenue", 100, 6, group="Blue"),
        Property("Chance", 0, 0, buildable=False),
        Property("Vermont Avenue", 100, 6, group="Blue"),
        Property("Connecticut Avenue", 120, 8, group="Blue"),
        Property("Jail", 0, 0, buildable=False),
        Property("St. Charles Place", 140, 10, group="Purple"),
        Property("Electric Company", 150, 0, buildable=False, group="Utility"),
        Property("States Avenue", 140, 10, group="Purple"),
        Property("Virginia Avenue", 160, 12, group="Purple"),
        Property("Pennsylvania Railroad", 200, 25, buildable=False, group="Railroad"),
        Property("St. James Place", 180, 14, group="Orange"),
        Property("Community Chest", 0, 0, buildable=False),
        Property("Tennessee Avenue", 180, 14, group="Orange"),
        Property("New York Avenue", 200, 16, group="Orange"),
        Property("Free Parking", 0, 0, buildable=False),
        Property("Kentucky Avenue", 220, 18, group="Red"),
        Property("Chance", 0, 0, buildable=False),
        Property("Indiana Avenue", 220, 18, group="Red"),
        Property("Illinois Avenue", 240, 20, group="Red"),
        Property("B&O Railroad", 200, 25, buildable=False, group="Railroad"),
        Property("Atlantic Avenue", 260, 22, group="Yellow"),
        Property("VentnorAvenue", 260, 22, group="Yellow"),
        Property("Water Works", 150, 0, buildable=False, group="Utility"),
        Property("Marvin Gardens", 280, 24, group="Yellow"),
        Property("Go to Jail", 0, 0, buildable=False),
        Property("Pacific Avenue", 300, 26, group="Green"),
        Property("Pennsylvania Avenue", 300, 26, group="Green"),
        Property("Community Chest", 0, 0, buildable=False),
        Property("North Carolina Avenue", 320, 28, group="Green"),
        Property("Short Line", 200, 25, buildable=False, group="Railroad"),
        Property("Passport Office", 0, 0, buildable=False),  # Inkognito
        Property("Park Place", 350, 35, group="Dark Blue"),
        Property("Luxury Tax", 0, 0, buildable=False),
        Property("Boardwalk", 400, 50, group="Dark Blue"),
        Property("Clue HQ", 0, 0, buildable=False),  # Cluedo
        Property("Ocean Trade", 0, 0, buildable=False),  # Ocean Trader
    ]

    # Assign property groups.  Useful for AI and hotel logic.
    property_groups = {
        "Brown": ["Mediterranean Avenue", "Baltic Avenue"],
        "Blue": ["Oriental Avenue", "Vermont Avenue", "Connecticut Avenue"],
        "Purple": ["St. Charles Place", "States Avenue", "Virginia Avenue"],
        "Orange": ["St. James Place", "Tennessee Avenue", "New York Avenue"],
        "Red": ["Kentucky Avenue", "Indiana Avenue", "Illinois Avenue"],
        "Yellow": ["Atlantic Avenue", "VentnorAvenue", "Marvin Gardens"],
        "Green": ["Pacific Avenue", "Pennsylvania Avenue", "North Carolina Avenue"],
        "Dark Blue": ["Park Place", "Boardwalk"],
        "Railroad": ["Reading Railroad", "Pennsylvania Railroad", "B&O Railroad", "Short Line"],
        "Utility": ["Electric Company", "Water Works"],
        "Special": ["Go", "Jail", "Free Parking", "Go to Jail", "Income Tax", "Luxury Tax", "Chance",
                   "Community Chest", "Passport Office", "Clue HQ", "Ocean Trade"]  # Inkognito, Cluedo, Ocean Trade
    }
    for prop in properties:
        for group_name, group_list in property_groups.items():
            if prop.name in group_list:
                prop.group = group_name
                break
    # Set Hotel Costs
    for prop in properties:
        if prop.group in ["Brown", "Blue"]:
            prop.hotel_cost = 50
        elif prop.group in ["Purple", "Orange"]:
            prop.hotel_cost = 100
        elif prop.group in ["Red", "Yellow"]:
            prop.hotel_cost = 150
        elif prop.group in ["Green", "Dark Blue"]:
            prop.hotel_cost = 200
        else:
            prop.hotel_cost = 0

    return Board(properties)



def create_decks():
    """Creates the Chance and Community Chest decks."""
    chance_cards = [
        {"description": "Advance to Go. Collect $200", "action": "move", "amount": 0},
        {"description": "Advance to Illinois Ave.", "action": "move", "amount": 24},
        {"description": "Advance to St. Charles Place", "action": "move", "amount": 11},
        {"description": "Go back to Reading Railroad", "action": "move", "amount": 5},
        {"description": "Bank pays you $50", "action": "money", "amount": 50},
        {"description": "Pay poor tax of $15", "action": "money", "amount": -15},
        {"description": "Take a trip to Reading Railroad", "action": "move", "amount": 5},
        {"description": "You have been elected Chairman of the Board. Pay each player $50", "action": "money",
         "amount": -50},
        {"description": "Your building loan matures. Collect $150", "action": "money", "amount": 150},
        {"description": "Go to Jail. Go directly to Jail. Do not pass Go, do not collect $200", "action": "jail"},
        {"description": "Get out of Jail Free", "action": "get_out_of_jail_free"},
        {"description": "Make general repairs on all of your property. For each house pay $25. For each hotel $100",
         "action": "hotel"},  # Simplified
        {"description": "Speed Token", "action": "speed_token"},
        {"description": "Use Ocean Trade card", "action": "ocean_trade"},  # Added Ocean Trade Card
    ]
    community_chest_cards = [
        {"description": "Advance to Go. Collect $200", "action": "move", "amount": 0},
        {"description": "Bank error in your favor. Collect $200", "action": "money", "amount": 200},
        {"description": "Doctor's fee. Pay $50", "action": "money", "amount": -50},
        {"description": "From sale of stock you receive $45", "action": "money", "amount": 45},
        {"description": "Get out of Jail Free", "action": "get_out_of_jail_free"},
        {"description": "Go to Jail. Go directly to Jail. Do not pass Go, do not collect $200", "action": "jail"},
        {"description": "Grand Opera Night. Collect $you10 from every player for opening night seats", "action": "birthday"},
        {"description": "Income tax refund.Collect $20", "action": "money", "amount": 20},
        {"description": "You inherit $100", "action": "money", "amount": 100},
        {"description": "Receive for services $20", "action": "money", "amount": 20},
        {"description": "You have won second prize in a beauty contest.Collect $10", "action": "money", "amount": 10},
        {"description": "You receive $25 consultancy fee", "action": "money", "amount": 25},
        {"description": "Make general repairs on all of your property. For each house pay $25. For each hotel $100",
         "action": "hotel"},  # Simplified
        {"description": "Speed Token", "action": "speed_token"},
        {"description": "Use Ocean Trade card", "action": "ocean_trade"}  # Added Ocean Trade Card
    ]
    chance_deck = Deck(chance_cards)
    community_chest_deck = Deck(community_chest_cards)
    return {"chance": chance_deck, "community_chest": community_chest_deck}



def create_players(num_players):
    """Creates a list of Player objects."""
    if num_players > 8:
        num_players = 8
    player_names = [f"Player {i + 1}" for i in range(num_players)]
    players =  [Player(name, 1500) for name in player_names]
    for player in players:
        player.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return players



def play_game(num_players=4):
    """
    Simulates a game of Monopoly (with Hotel, Clue, Inkognito, and Ocean Trader elements).

    Args:
        num_players (int, optional): The number of players in the game. Defaults to 4.
    """
    board = create_board()
    decks = create_decks()
    players = create_players(num_players)

    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Monopoly Game")
    font = pygame.font.Font(None, 24)


    # Game Setup
    for deck in decks.values():
        deck.shuffle()

    game_over = False
    turn = 0
    while not game_over and turn < 1000:  # Limit turns to prevent infinite games
        for event in pygame.event.get():  # handle events to prevent freezing
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        print(f"\n--- Turn {turn} ---")
        for player in players:
            if not player.jailed_for and player in players: #Added check for jail and if player is still in the game
                handle_move(player, board, players, decks)
                ai_manage_properties(player, board)  # AI builds hotels
        board.display(players)  # Display after each move  #moved inside the loop
        board.draw_board(screen, players) #draw board
        pygame.display.flip()
        game_over = check_game_over(players)
        turn += 1
        time.sleep(0.5)  # Add a small delay for better visualization
        board.update_good_prices() # Update prices at the end of each turn
        players = [p for p in players if len(p.properties) > 0] #remove players with no properties

    # Determine the winner
    pygame.quit()
    if game_over:
        winners = [player for player in players if len(player.properties) > 0]
        if winners:
            print("\n--- Game Over ---")
            print(f"Winner(s): {', '.join(winner.name for winner in winners)}")
        else:
            print("\n--- Game Over ---")
            print("All players are bankrupt!")
    else:
        print("\n--- Game Over ---")
        print("Game ended due to turn limit.")
        winners = [player for player in players if len(player.properties) > 0]
        if winners:
            print(f"Active Players: {', '.join(winner.name for winner in winners)}")



if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    play_game(num_players)
