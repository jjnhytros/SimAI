def ai_buy_property(player, property, board):
    """
    AI decision-making logic for buying properties.  Considers more factors.

    Args:
        player (Player): The AI player.
        property (Property): The property to be considered.
        board (Board): The game board.

    Returns:
        bool: True if the AI decides to buy the property, False otherwise.
    """
    # --- Basic Strategy ---
    # 1. Can the AI afford it?
    if player.money < property.cost:
        return False

    # 2. Is it a good investment?  (Consider rent and potential for hotels)
    #    Higher rent is better.  Potential for hotels is a big plus.
    if property.cost == 0:  # Check for division by zero
        return False
    expected_return = property.get_rent() / property.cost
    if property.buildable:
        expected_return = property.get_rent() * 4 / (property.cost + property.hotel_cost)  # Estimate Rent with hotel.

    # 3. Does the AI already own properties in the same group?
    #    Completing a group is very valuable.
    group_count = 0
    if property.group:
        for owned_property in player.properties:
            if owned_property.group == property.group:
                group_count += 1
    group_completion_bonus = 0
    if property.group:
        group_properties_count = 0
        for p in board.properties:
            if p.group == property.group:
                group_properties_count += 1
        if group_count >= group_properties_count - 1:
            group_completion_bonus = 0.2  # Big bonus

    # --- Risk Assessment ---
    # 4. How much money does the AI have left after buying?
    remaining_money = player.money - property.cost
    # Don't buy if it leaves the AI with very little money.
    if remaining_money < 200:
        return False

    # --- Decision ---
    # Combine all factors to make a decision.
    if expected_return > 0.05 or group_completion_bonus > 0.1:  # Aggressive strategy
        return True
    elif expected_return > 0.03 and group_count > 0:  # Moderate Strategy
        return True
    else:
        return False  # Conservative strategy


def ai_manage_properties(player, board):
    """
    AI logic for managing properties, including building hotels.

    Args:
        player (Player): The AI player.
        board (Board): The game board.
    """
    for group_name in ["Brown", "Blue", "Green", "Yellow", "Red", "Purple", "Orange", "Dark Blue"]:  # Check each group.
        group_properties = [prop for prop in player.properties if prop.group == group_name]
        if len(group_properties) > 0 and len(group_properties) == len(
                [p for p in board.properties if p.group == group_name]):  # Check if we own the group
            # Check if we can build a hotel on any property in the group
            for prop in group_properties:
                if prop.buildable and prop.hotels == 0 and player.money >= prop.hotel_cost:
                    player.pay_money(prop.hotel_cost)
                    prop.hotels += 1
                    print(f"{player.name} builds a hotel on {prop.name}.")
                    break  # Build only one hotel per turn.
