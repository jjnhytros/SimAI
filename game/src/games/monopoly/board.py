import pygame
import random
from game_components import Property

class Board:
    """Represents the game board."""
    def __init__(self, properties):
        """
        Initializes the game board.

        Args:
            properties (list): A list of Property objects representing the board spaces.
        """
        self.properties = properties
        self.good_prices = self.initialize_good_prices()  # Initialize good prices

    def get_property(self, position):
        """Gets the property at a given position."""
        return self.properties[position]

    def display(self, players):
        """Displays the current state of the game board and players. Now includes property details and player money."""
        print("\n--- Game Board ---")
        for i, prop in enumerate(self.properties):
            owner_name = prop.owner.name if prop.owner else "None"
            print(f"{i}. {prop} (Owner: {owner_name})")  # Show full property info
        print("\n--- Players ---")
        for player in players:
            print(player)  # Use the Player's __str__ method
        print(f"\n--- Good Prices ---")
        for good, price in self.good_prices.items():
            print(f"{good}: ${price:.2f}")

    def update_good_prices(self):
        """Simulates market fluctuations for all goods."""
        available_goods = ["Grain", "Tropical Fruits", "Bananas", "Tobacco", "Cocoa", "Coffee", "Tea", "Rice",
                           "Linseed Oil", "Sugar", "Animal Products", "Wool", "Cotton", "Precious Wood", "Rubber",
                           "Fish Products", "Coal", "Petroleum", "Iron Ore", "Copper", "Bauxite", "Lead and Zinc",
                           "Phosphates", "Textiles", "Iron and Steel", "Aluminium", "Machinery", "Vehicles",
                           "Electrical Appliances", "Electronics and Computers", "Chemical Products"]

        for good in available_goods:
            price_change = random.uniform(-0.1, 0.1)  # Fluctuate prices by -10% to +10%
            self.good_prices[good] *= (1 + price_change)
            self.good_prices[good] = max(1, self.good_prices[good])  # Ensure prices don't go below $1

    def initialize_good_prices(self):
        """Initializes the prices of all goods."""
        available_goods = ["Grain", "Tropical Fruits", "Bananas", "Tobacco", "Cocoa", "Coffee", "Tea", "Rice",
                           "Linseed Oil", "Sugar", "Animal Products", "Wool", "Cotton", "Precious Wood", "Rubber",
                           "Fish Products", "Coal", "Petroleum", "Iron Ore", "Copper", "Bauxite", "Lead and Zinc",
                           "Phosphates", "Textiles", "Iron and Steel", "Aluminium", "Machinery", "Vehicles",
                           "Electrical Appliances", "Electronics and Computers", "Chemical Products"]
        prices = {}
        for good in available_goods:
            prices[good] = random.randint(20, 100)  # Initial price between $20 and $100
        return prices
      
    def draw_board(self, screen, players):
        """Draws the game board on the Pygame screen."""
        screen.fill((255, 255, 255))  # White background

        # Define colors
        color_mapping = {
            "Brown": (165, 42, 42),  # Brown
            "Blue": (0, 0, 255),  # Blue
            "Purple": (128, 0, 128),  # Purple
            "Orange": (255, 165, 0),  # Orange
            "Red": (255, 0, 0),  # Red
            "Yellow": (255, 255, 0),  # Yellow
            "Green": (0, 255, 0),  # Green
            "Dark Blue": (0, 0, 128),  # Dark Blue
            "Railroad": (128, 128, 128),  # Gray
            "Utility": (220, 220, 220),  # Light Gray
            "Special": (0, 0, 0),  # Black
        }

        # Board dimensions
        board_width = 600
        board_height = 600
        property_width = board_width / 11
        property_height = board_height / 11
        font = pygame.font.Font(None, 16)

        for i, prop in enumerate(self.properties):
            # Calculate property position
            if 0 <= i <= 10:
                x = board_width - (i * property_width)
                y = board_height - property_height
            elif 11 <= i <= 20:
                x = 0
                y = board_height - ((i - 10) * property_height)
            elif 21 <= i <= 30:
                x = (i - 20) * property_width
                y = 0
            else:
                x = board_width - property_width
                y = (i - 30) * property_height

            # Draw property rectangle
            color = color_mapping.get(prop.group, (0, 0, 0))
            pygame.draw.rect(screen, color, (x, y, property_width, property_height))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, property_width, property_height), 1)  # Black border

            # Display property name
            text = font.render(prop.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + property_width / 2, y + property_height / 2))
            screen.blit(text, text_rect)

            # Display owner
            if prop.owner:
                owner_text = font.render(prop.owner.name, True, (0, 0, 0))
                owner_rect = owner_text.get_rect(center=(x + property_width / 2, y + property_height / 4))
                screen.blit(owner_text, owner_rect)
            
            # Display hotels
            if prop.hotels > 0:
                hotel_text = font.render(f"Hotel: {prop.hotels}", True, (255, 255, 255))
                hotel_rect = hotel_text.get_rect(center=(x + property_width / 2, y + property_height * 3/4))
                screen.blit(hotel_text, hotel_rect)

        #draw player positions
        for player in players:
            player_pos_x = 0
            player_pos_y = 0
            if 0 <= player.position <= 10:
                player_pos_x = board_width - (player.position * property_width) + property_width/2
                player_pos_y = board_height - property_height/2
            elif 11 <= player.position <= 20:
                player_pos_x = property_width/2
                player_pos_y = board_height - ((player.position - 10) * property_height) + property_height/2
            elif 21 <= player.position <= 30:
                player_pos_x = (player.position - 20) * property_width + property_width/2
                player_pos_y = property_height/2
            else:
                player_pos_x = board_width - property_width/2
                player_pos_y = (player.position - 30) * property_height + property_height/2
            
            pygame.draw.circle(screen, player.color, (player_pos_x, player_pos_y), 10) #use player color
            text = font.render(player.name[0], True, (0,0,0))
            text_rect = text.get_rect(center=(player_pos_x, player_pos_y))
            screen.blit(text, text_rect)

        pygame.display.flip()

# deck.py
import pygame
import random

class Deck:
    """Represents a deck of cards (e.g., Chance, Community Chest).  Now includes Clue and Inkognito cards."""
    def __init__(self, cards):
        """
        Initializes a deck of cards.

        Args:
            cards (list): A list of dictionaries representing the cards.
        """
        self.cards = cards
        self.discard_pile = []  # Added discard pile for cards that are removed from the game.

    def draw_card(self):
        """Draws a card from thedeck."""
        if not self.cards:
            self.cards = self.discard_pile[:]  # Reshuffle
            self.discard_pile = []
            random.shuffle(self.cards)
        return self.cards.pop(0)

    def add_card_to_discard(self, card):
        """Adds a card to the discard pile."""
        self.discard_pile.append(card)

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)
        
# player.py
import pygame
import random
from game_components import Property

class Player:
    """Represents a player in the game."""
    def __init__(self, name, money, position=0, properties=None, briefcase=None, suspicion=0):
        """
        Initializes a player.

        Args:
            name (str): Il nome del giocatore.
            money (int): La quantità iniziale di denaro del giocatore.
            position (int, optional): La posizione iniziale del giocatore sul tabellone. Defaults to 0.
            properties (list, optional): Le proprietà possedute dal giocatore. Defaults to [].
            briefcase (dict, optional): Gli oggetti nella valigetta del giocatore (per Inkognito). Defaults to {}.
            suspicion (int, optional): Il livello di sospetto del giocatore (per Clue). Defaults to 0.
        """
        self.name = name
        self.money = money
        self.position = position
        self.properties = properties if properties else []
        self.jailed_for = 0  # Turns jailed, 0 if not jailed
        self.briefcase = briefcase if briefcase else {}  # For Inkognito
        self.suspicion = suspicion  # For Cluedo
        self.aquatic_goods = 0  # For Ocean Trader
        self.has_passport = False  # For Inkognito
        self.speed_tokens = 0  # For general speed
        self.ship_capacity = 1000  # For Ocean Trader -  increased capacity for all players.
        self.good_inventory = {}  # For Ocean Trader -  what goods the player is carrying.  {good_type: quantity}
        self.ocean_trade_card = False  # New attribute to track the "Use Ocean Trade" card
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #assign a random color

    def add_property(self, property):
        """Adds a property to the player's portfolio."""
        self.properties.append(property)
        property.owner = self

    def remove_property(self, property):
        """Removes a property from the player's portfolio."""
        self.properties.remove(property)
        property.owner = None

    def pay_money(self, amount, to=None):
        """
        Pays money to another player or the bank.

        Args:
            amount (int): The amount of money to pay.
            to (Player, optional): The recipient of the payment. Defaults to None (the bank).

        Returns:
            bool: True if the payment was successful, False if the player went bankrupt.
        """
        if self.money >= amount:
            self.money -= amount
            if to:
                to.money += amount
            return True
        else:
            return False  # Changed to return False

    def receive_money(self, amount):
        """Receives money."""
        self.money += amount

    def move(self, spaces, board_properties_length):
        """Moves the player's position on the board."""
        self.position = (self.position + spaces) % board_properties_length

    def __str__(self):
        return f"{self.name} (Money: {self.money}, Position: {self.position}, Properties: {len(self.properties)}, Aquatic Goods: {self.aquatic_goods}, Ship Capacity: {self.ship_capacity}, Goods: {self.good_inventory}, Ocean Trade Card: {self.ocean_trade_card})"

