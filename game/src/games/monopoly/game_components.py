import pygame
import random

class Property:
    """Represents a property on the game board."""
    def __init__(self, name, cost, rent, hotel_cost=0, buildable=True, group=None):
        """
        Initializes a property.

        Args:
            name (str): Il nome della proprietà.
            cost (int): Il costo per acquistare la proprietà.
            rent (int): L'affitto base per la proprietà.
            hotel_cost (int, optional): Il costo per costruire un hotel. Defaults to 0.
            buildable (bool, optional): Indica se si possono costruire hotel. Defaults to True.
            group (str, optional): Il gruppo della proprietà (e.g., "Marrone", "Blu"). Defaults to None.
        """
        self.name = name
        self.cost = cost
        self.rent = rent
        self.owner = None
        self.is_mortgaged = False
        self.hotels = 0  # Numero di hotel (0, 1)
        self.buildable = buildable
        self.group = group
        self.good_type = None  # Per Ocean Trader - il tipo di bene che questa proprietà produce/vuole

    def get_rent(self):
        """Calculates the rent for the property, considering hotels."""
        if self.is_mortgaged:
            return 0
        rent = self.rent
        if self.hotels > 0:
            rent *= 4  # Hotel increases rent significantly
        return rent

    def __str__(self):
        return f"{self.name} (Cost: {self.cost}, Rent: {self.rent}, Hotels: {self.hotels}, Owner: {self.owner})"


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
        self.speed_tokens = 0  #For general speed
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #assign a random color
        self.ship_capacity = 1000  # For Ocean Trader
        self.good_inventory = {}  # For Ocean Trader

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
