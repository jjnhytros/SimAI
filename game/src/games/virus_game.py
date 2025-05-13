import random
import time
import math
import datetime
import os

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True
        self.infected = False
        self.has_antidote = False
        self.bullet = 1 if role == "Terrorist" else 0
        self.officer_bullets = 3 if role == "Officer" else 0
        self.virus = 1 if role == "Terrorist" else 0
        self.investigated = False
        self.tested = False # For Researchers
        self.suspicion = 0
        self.traits = {
            "Aggressive": random.uniform(0.01, 1.00),
            "Cautiousness": random.uniform(0.01, 1.00),
            "Deception": random.uniform(0.01, 1.00),
            "Helpfulness": random.uniform(0.01, 1.00),
            "Paranoia": random.uniform(0.01, 1.00),
            "Observance": random.uniform(0.01, 1.00),
            "Trusting": random.uniform(0.01, 1.00),
            "Skeptical": random.uniform(0.01, 1.00),
            "Brave": random.uniform(0.01, 1.00),
            "Timid": random.uniform(0.01, 1.00),
            "Leaderlike": random.uniform(0.01, 1.00),
            "Followerlike": random.uniform(0.01, 1.00),
            "Optimistic": random.uniform(0.01, 1.00),
            "Pessimistic": random.uniform(0.01, 1.00),
            "Impulsive": random.uniform(0.01, 1.00),
            "Deliberate": random.uniform(0.01, 1.00),
            "Secretive": random.uniform(0.01, 1.00),
            "Open": random.uniform(0.01, 1.00),
            "Patient": random.uniform(0.01, 1.00),
            "Impatient": random.uniform(0.01, 1.00),
            "Empathetic": random.uniform(0.01, 1.00),
            "Callous": random.uniform(0.01, 1.00),
            "Humorous": random.uniform(0.01, 1.00),
            "Serious": random.uniform(0.01, 1.00),
            "Eloquent": random.uniform(0.01, 1.00),
            "Quiet": random.uniform(0.01, 1.00),
            "Vengeful": random.uniform(0.01, 1.00),
            "Forgiving": random.uniform(0.01, 1.00),
            "Ambitious": random.uniform(0.01, 1.00),
            "Content": random.uniform(0.01, 1.00),
            "Loyal": random.uniform(0.01, 1.00),
            "Independent": random.uniform(0.01, 1.00),
            "Curious": random.uniform(0.01, 1.00),
            "Apathetic": random.uniform(0.01, 1.00),
            "Organized": random.uniform(0.01, 1.00),
            "Disorganized": random.uniform(0.01, 1.00),
            "Adaptable": random.uniform(0.01, 1.00),
            "Rigid": random.uniform(0.01, 1.00),
            "Resourceful": random.uniform(0.01, 1.00),
            "Wasteful": random.uniform(0.01, 1.00),
            "Principled": random.uniform(0.01, 1.00),
            "Pragmatic": random.uniform(0.01, 1.00),
            "Confident": random.uniform(0.01, 1.00),
            "Insecure": random.uniform(0.01, 1.00),
            "Energetic": random.uniform(0.01, 1.00),
            "Lethargic": random.uniform(0.01, 1.00),
            "Conventional": random.uniform(0.01, 1.00),
            "Unconventional": random.uniform(0.01, 1.00),
            "Vulnerability": random.uniform(0.01, 1.000),  # Resistance to vius
            "Resistance": random.uniform(0.01, 1.00),
        }
        self.trust_model = self.initialize_trust_model()
        self.suspicion_memory = [] # Store past suspicion levels and outcomes
        self.investigation_successes = 0
        self.investigation_failures = 0

    def __str__(self):
        trait_str = ", ".join(f"{k}: {v:.2f}" for k, v in self.traits.items())
        return f"{self.name} ({self.role}, {trait_str}, {'Alive' if self.alive else 'Dead'}, {'Infected' if self.infected else 'Not Infected'}, Suspicion: {self.suspicion:.2f})"

    def initialize_trust_model(self):
        # Simple model: trust is influenced by helpfulness and skepticism
        return {"base_trust": self.traits["Helpfulness"] * (1 - self.traits["Skeptical"]),
                "adjustments": {}}

    def update_trust(self, other_player, outcome):
        # Outcome can be "positive" (e.g., player was helpful), "negative" (e.g., player acted suspiciously)
        if other_player.name not in self.trust_model["adjustments"]:
            self.trust_model["adjustments"][other_player.name] = 0

        if outcome == "positive":
            self.trust_model["adjustments"][other_player.name] += 0.05
        elif outcome == "negative":
            self.trust_model["adjustments"][other_player.name] -= 0.1

        self.trust_model["adjustments"][other_player.name] = max(-0.5, min(0.5, self.trust_model["adjustments"][other_player.name]))

    def get_trust(self, other_player):
        base_trust = self.trust_model["base_trust"]
        adjustment = self.trust_model["adjustments"].get(other_player.name, 0)
        return max(0, min(1, base_trust + adjustment))

    def learn_from_suspicion(self, round_outcome):
        # Simple reinforcement learning: if high suspicion led to a "bad" outcome (e.g., innocent killed), adjust paranoia/observance
        if self.suspicion > 0.7:
            if round_outcome == "innocent_killed":
                self.traits["Paranoia"] *= 0.95
                self.traits["Observance"] *= 1.05
            elif round_outcome == "terrorist_killed":
                self.traits["Paranoia"] *= 1.05
                self.traits["Observance"] *= 0.95
        elif self.suspicion < 0.3:
            if round_outcome == "innocent_killed":
                self.traits["Paranoia"] *= 1.05
                self.traits["Observance"] *= 0.95
            elif round_outcome == "terrorist_killed":
                self.traits["Paranoia"] *= 0.95
                self.traits["Observance"] *= 1.05

        for trait in ["Paranoia", "Observance"]:
            self.traits[trait] = max(0.01, min(1.00, self.traits[trait]))

    def adjust_traits_based_on_investigation(self, success):
        learning_rate = 0.05
        if self.role == "Journalist" or self.role == "Officer":
            if success:
                self.investigation_successes += 1
                if self.traits["Observance"] < 0.99:
                    self.traits["Observance"] += learning_rate
                if self.traits["Confident"] < 0.99:
                    self.traits["Confident"] += learning_rate * 0.5
            else:
                self.investigation_failures += 1
                if self.traits["Observance"] > 0.01:
                    self.traits["Observance"] -= learning_rate * 0.5
                if self.traits["Cautiousness"] < 0.99:
                    self.traits["Cautiousness"] += learning_rate * 0.3
                if self.traits["Insecure"] < 0.99:
                    self.traits["Insecure"] += learning_rate * 0.2
        elif self.role == "Researcher":
            if success:
                self.investigation_successes += 1
                if self.traits["Deliberate"] < 0.99:
                    self.traits["Deliberate"] += learning_rate
                if self.traits["Patient"] < 0.99:
                    self.traits["Patient"] += learning_rate * 0.5
            else:
                self.investigation_failures += 1
                if self.traits["Impulsive"] < 0.99:
                    self.traits["Impulsive"] += learning_rate * 0.3
                if self.traits["Pessimistic"] < 0.99:
                    self.traits["Pessimistic"] += learning_rate * 0.2

        # Keep traits within bounds
        for trait in self.traits:
            self.traits[trait] = max(0.00, min(1.00, self.traits[trait]))


class Game:
    def __init__(self):
        self.players = []
        self.round = 0
        self.current_date = {"year": 1, "month": 1, "day": 1, "hour": 8, "minute": 0, "second": 0}
        self.time_unit = self.get_time_unit()
        self.antidote_holder = None
        self.terrorists_alive = 2
        self.officer_alive = True
        self.journalist_revealed = False
        self.journalist_investigations = {}
        self.rounds_without_terrorist_kill = 0
        self.game_narrative = []
        self.round_history = []
        self.action_time_scale = 60

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_game_info(self):
        print("-" * 30)
        print(f"Round: {self.round}")
        print(f"Time: {self.format_time()} ({self.time_unit})")
        print("-" * 30)

    def display_players(self):
        print("\n--- Players Status ---")
        for player in self.players:
            status = "Alive" if player.alive else "Dead"
            infected = " (Infected)" if player.infected else ""
            investigated = " (Investigated)" if player.investigated else ""
            tested = " (Tested)" if player.tested else ""
            suspicion_level = f"Suspicion: {player.suspicion:.2f}"
            print(f"{player.name} ({player.role}): {status}{infected}{investigated}{tested}, {suspicion_level}")
        print("-" * 30)

    def display_narrative(self):
        if self.game_narrative:
            print("\n--- Recent Events ---")
            for event in self.game_narrative[-5:]: # Show last 5 events
                print(event)
            print("-" * 30)
        self.game_narrative = [] # Clear narrative after displaying

    def advance_time(self, seconds):
        game_seconds = int(seconds * self.action_time_scale) # Convert to integer here
        self.current_date["second"] += game_seconds
        while self.current_date["second"] >= 60:
            self.current_date["second"] -= 60
            self.current_date["minute"] += 1
        while self.current_date["minute"] >= 60:
            self.current_date["minute"] -= 60
            self.current_date["hour"] += 1
        while self.current_date["hour"] >= 24:
            self.current_date["hour"] -= 24
            self.current_date["day"] += 1
        while self.current_date["day"] > self.days_in_month(self.current_date["month"], self.current_date["year"]):
            self.current_date["day"] -= self.days_in_month(self.current_date["month"], self.current_date["year"])
            self.current_date["month"] += 1
            if self.current_date["month"] > 12:
                self.current_date["month"] = 1
                self.current_date["year"] += 1

        self.time_unit = self.get_time_unit()

    def days_in_month(self, month, year):
        if month == 2:
            return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31

    def format_time(self):
        return f"Anno {self.current_date['year']}, Mese {self.current_date['month']}, Giorno {self.current_date['day']} - Ora: {self.current_date['hour']:02d}:{self.current_date['minute']:02d}:{self.current_date['second']:02d}"

    def get_time_unit(self):
        hour = self.current_date["hour"]
        if 6 <= hour < 12:
            return "Mattina"
        elif 12 <= hour < 18:
            return "Pomeriggio"
        elif 18 <= hour < 24:
            return "Sera"
        else:
            return "Notte"

    def get_alive_players(self):
        return [player for player in self.players if player.alive]

    def simulate_pause(self):
        pause_duration = random.uniform(1, 3)  # Simulate a pause of 1 to 3 seconds
        print("\n--- Time Passes... ---")
        time.sleep(pause_duration)
        self.player_interactions()

    def player_interactions(self):
        alive_players = self.get_alive_players()
        if len(alive_players) < 2:
            return

        num_interactions = random.randint(1, min(3, len(alive_players) // 2))
        random.shuffle(alive_players)

        for _ in range(num_interactions):
            player1 = random.choice(alive_players)
            player2 = random.choice([p for p in alive_players if p != player1])

            interaction_type = random.choice(["trust_assessment", "suspicion_sharing", "plea_innocence", "express_fear"])
            interaction_duration = random.uniform(5, 30)
            self.advance_time(interaction_duration)
            self.display_narrative() # Show narrative before new event
            print(f"[{self.format_time()}]")

            if interaction_type == "trust_assessment":
                trust_level = player1.get_trust(player2)
                if trust_level > 0.7 and player1.traits["Trusting"] > 0.5:
                    self.game_narrative.append(f"{player1.name} (trusting {player2.name}): \"I believe we can rely on you, {player2.name}.\"")
                elif trust_level < 0.3 and player1.traits["Skeptical"] > 0.5:
                    self.game_narrative.append(f"{player1.name} (skeptical of {player2.name}): \"I'm keeping an eye on you, {player2.name}.\"")
            elif interaction_type == "suspicion_sharing":
                suspect = random.choice([p for p in alive_players if p != player1 and p != player2])
                if player1.suspicion > 0.4 and player1.get_trust(player2) > 0.5:
                    self.game_narrative.append(f"{player1.name} (to {player2.name}): \"I have a bad feeling about {suspect.name}. What do you think?\"")
                    if suspect.suspicion > 0.3 or player2.traits["Paranoia"] > 0.6:
                        self.game_narrative.append(f"{player2.name}: \"Hmm, you might be right about {suspect.name}.\"")
                        suspect.suspicion += 0.02 * player2.traits["Paranoia"]
            elif interaction_type == "plea_innocence":
                if player1.suspicion > 0.5 and player1.traits["Helpfulness"] > 0.3:
                    other = random.choice([p for p in alive_players if p != player1])
                    self.game_narrative.append(f"{player1.name} (to {other.name}): \"Please, you have to believe me. I'm innocent!\"")
                    other.suspicion -= 0.01 * other.traits["Empathetic"]
            elif interaction_type == "express_fear":
                if player1.traits["Timid"] > 0.6 and player1.suspicion > 0.2:
                    other = random.choice([p for p in alive_players if p != player1])
                    self.game_narrative.append(f"{player1.name} (to {other.name}, nervously): \"I'm scared... what's going to happen?\"")
                    other.traits["Helpfulness"] += 0.01 * other.traits["Empathetic"]

            player1.suspicion += random.uniform(-0.01, 0.01)
            player1.suspicion = max(0, min(1, player1.suspicion))
            player2.suspicion += random.uniform(-0.01, 0.01)
            player2.suspicion = max(0, min(1, player2.suspicion))

    def setup_game(self):
        roles = ["Terrorist", "Terrorist", "Fanatic", "Officer", "Ordinary Citizen", "Ordinary Citizen", "Ordinary Citizen", "Ordinary Citizen", "Ordinary Citizen", "Researcher", "Researcher", "Journalist"]
        random.shuffle(roles)
        names = [f"Player {i+1}" for i in range(12)]
        self.players = [Player(name, role) for name, role in zip(names, roles)]
        self.antidote_holder = random.choice([p for p in self.players if p.role == "Ordinary Citizen"])
        self.antidote_holder.has_antidote = True
        self.virus_carrier = random.choice([p for p in self.players if p.role == "Terrorist"])
        self.journalist = next((p for p in self.players if p.role == "Journalist"), None)

    def display_players(self):
        print(f"\n--- Players Status (Round {self.round}, Time: {self.time_unit}) ---")
        for player in self.players:
            print(player)
        print("-----------------------\n")
        for event in self.game_narrative:
            print(event)
        self.game_narrative = []

    def get_alive_players(self):
        return [player for player in self.players if player.alive]

    def get_players_by_role(self, role):
        return [player for player in self.players if player.role == role and player.alive]

    def player_interactions(self):
        alive_players = self.get_alive_players()
        if len(alive_players) < 2:
            return

        num_interactions = random.randint(1, min(3, len(alive_players) // 2))
        random.shuffle(alive_players)

        for _ in range(num_interactions):
            player1 = random.choice(alive_players)
            player2 = random.choice([p for p in alive_players if p != player1])

            interaction_type = random.choice(["trust_assessment", "suspicion_sharing", "plea_innocence", "express_fear"])
            interaction_duration = random.uniform(5, 30) # Interaction takes 5 to 30 real seconds
            self.advance_time(interaction_duration)
            print(f"[{self.format_time()}]")

            if interaction_type == "trust_assessment":
                trust_level = player1.get_trust(player2)
                if trust_level > 0.7 and player1.traits["Trusting"] > 0.5:
                    print(f"{player1.name} (trusting {player2.name}): \"I believe we can rely on you, {player2.name}.\"")
                elif trust_level < 0.3 and player1.traits["Skeptical"] > 0.5:
                    print(f"{player1.name} (skeptical of {player2.name}): \"I'm keeping an eye on you, {player2.name}.\"")
            elif interaction_type == "suspicion_sharing":
                suspect = random.choice([p for p in alive_players if p != player1 and p != player2])
                if player1.suspicion > 0.4 and player1.get_trust(player2) > 0.5:
                    print(f"{player1.name} (to {player2.name}): \"I have a bad feeling about {suspect.name}. What do you think?\"")
                    if suspect.suspicion > 0.3 or player2.traits["Paranoia"] > 0.6:
                        print(f"{player2.name}: \"Hmm, you might be right about {suspect.name}.\"")
                        suspect.suspicion += 0.02 * player2.traits["Paranoia"]
            elif interaction_type == "plea_innocence":
                if player1.suspicion > 0.5 and player1.traits["Helpfulness"] > 0.3:
                    other = random.choice([p for p in alive_players if p != player1])
                    print(f"{player1.name} (to {other.name}): \"Please, you have to believe me. I'm innocent!\"")
                    other.suspicion -= 0.01 * other.traits["Empathetic"]
            elif interaction_type == "express_fear":
                if player1.traits["Timid"] > 0.6 and player1.suspicion > 0.2:
                    other = random.choice([p for p in alive_players if p != player1])
                    print(f"{player1.name} (to {other.name}, nervously): \"I'm scared... what's going to happen?\"")
                    other.traits["Helpfulness"] += 0.01 * other.traits["Empathetic"]

            player1.suspicion += random.uniform(-0.01, 0.01)
            player1.suspicion = max(0, min(1, player1.suspicion))
            player2.suspicion += random.uniform(-0.01, 0.01)
            player2.suspicion = max(0, min(1, player2.suspicion))

    def player_action(self, player):
        if not player.alive:
            return

        thinking_time = random.uniform(1, 3)
        time.sleep(thinking_time)

        action_duration = random.uniform(5, 20)
        self.advance_time(action_duration)
        self.display_narrative()
        print(f"[{self.format_time()}] {player.name} ({player.role}) is acting...")

        trait_desc = ", ".join(f"{k}: {v:.2f}" for k, v in player.traits.items())
        action_narrative = f"{player.name} ({player.role}, Traits: {trait_desc})"

        if player.role == "Terrorist":
            targets = [p for p in self.get_alive_players() if p != player]
            if targets:
                officer_target = next((t for t in targets if t.role == "Officer"), None)
                priority_target = officer_target if officer_target else (targets[0] if targets else None)

                shoot_chance = player.traits["Aggressive"] * (1 - player.traits["Cautiousness"])
                infect_chance = player.traits["Deception"] * (1 - player.traits["Aggressive"])

                if priority_target:
                    trust_scores = {t: sum(other.get_trust(t) for other in self.get_alive_players() if other != player) for t in targets}
                    lowest_trust_target = min(trust_scores, key=trust_scores.get) if trust_scores else priority_target
                    if random.random() < 0.2:
                        priority_target = lowest_trust_target

                if player.bullet > 0 and priority_target and random.random() < shoot_chance:
                    self.game_narrative.append(f"{player.name} (Terrorist) aggressively targets {priority_target.name}.")
                    priority_target.alive = False
                    player.bullet -= 1
                    if priority_target.role == "Terrorist":
                        self.terrorists_alive -= 1
                    elif priority_target.role == "Officer":
                        self.officer_alive = False
                    for p in self.players:
                        if p == priority_target:
                            p.suspicion += 2
                            for other_player in self.get_alive_players():
                                if other_player != player:
                                    other_player.update_trust(player, "negative")
                    for other_player in self.get_alive_players():
                        if other_player != player:
                            other_player.update_trust(priority_target, "negative")

                elif player.virus > 0 and targets and random.random() < infect_chance:
                    infection_target = random.choice(targets)
                    self.game_narrative.append(f"{player.name} (Terrorist) deceptively infects {infection_target.name}.")
                    infection_target.infected = True
                    player.virus -= 1
                    for p in self.players:
                        if p == infection_target:
                            p.suspicion += 1
                            for other_player in self.get_alive_players():
                                if other_player != player:
                                    other_player.update_trust(player, "negative")
                    for other_player in self.get_alive_players():
                        if other_player != player:
                            other_player.update_trust(infection_target, "negative")
                else:
                    self.game_narrative.append(f"{player.name} acted with calculated stealth.")

        elif player.role == "Officer":
            if player.officer_bullets > 0:
                targets = self.get_alive_players()
                if targets:
                    potential_targets = []
                    suspicious_low_trust = sorted([p for p in targets if p.suspicion > 0.5 and player.get_trust(p) < 0.4], key=lambda x: x.suspicion, reverse=True)
                    journalist_info_targets = [p for p in targets if p.name in self.journalist_investigations and self.journalist_investigations[p.name] == "Terrorist"]

                    if journalist_info_targets:
                        potential_targets.extend(journalist_info_targets)
                    elif suspicious_low_trust:
                        potential_targets.extend(suspicious_low_trust[:2])

                    shoot_probability = player.traits["Aggressive"] * (1 - player.traits["Cautiousness"])
                    if self.time_unit == "Night":
                        shoot_probability *= 0.8

                    target_to_shoot = None
                    if potential_targets and random.random() < 0.7:
                        target_to_shoot = random.choice(potential_targets)
                    elif targets and random.random() < player.traits["Paranoia"] * 0.2:
                        target_to_shoot = random.choice(targets)

                    if target_to_shoot:
                        self.game_narrative.append(f"{player.name} (Officer) takes action against {target_to_shoot.name}.")
                        target_to_shoot.alive = False
                        player.officer_bullets -= 1
                        if target_to_shoot.role == "Terrorist":
                            self.terrorists_alive -= 1
                            self.round_history.append("terrorist_killed")
                            for other_player in self.get_alive_players():
                                if other_player != player:
                                    other_player.update_trust(player, "positive")
                        elif target_to_shoot.role != "Terrorist":
                            self.round_history.append("innocent_killed")
                            for other_player in self.get_alive_players():
                                if other_player != player:
                                    other_player.update_trust(player, "negative")
                        for p in self.players:
                            if p == target_to_shoot:
                                p.suspicion += 2
                    else:
                        self.game_narrative.append(f"{player.name} remained watchful.")
            else:
                self.game_narrative.append(f"{player.name} is out of bullets.")

        elif player.role == "Researcher":
            targets = [p for p in self.get_alive_players() if not p.tested]
            if targets:
                test_target = random.choice(targets)
                self.game_narrative.append(f"[{self.format_time()}] {player.name} (Researcher) is examining {test_target.name}.")
                if player.traits["Paranoia"] > 0.7:
                    suspicious_untested = [t for t in targets if t.suspicion > 0.6]
                    test_target = random.choice(suspicious_untested) if suspicious_untested else test_target
                test_target.tested = True
                self.game_narrative.append(f"[{self.format_time()}] {player.name} tested {test_target.name}.")
                if test_target == self.antidote_holder:
                    print(f"[{self.format_time()}] Researcher {player.name} found the antidote with {test_target.name}!")
                    player.adjust_traits_based_on_investigation(True)
                    self.game_over = True
                    self.winner = "Citizens"
                    return
                else:
                    player.adjust_traits_based_on_investigation(False)
            elif self.get_alive_players():
                test_target = random.choice(self.get_alive_players())
                self.game_narrative.append(f"[{self.format_time()}] {player.name} (Researcher) re-examines {test_target.name}.")
                self.game_narrative.append(f"[{self.format_time()}] {player.name} re-tested {test_target.name}.")

        elif player.role == "Journalist":
            targets = [p for p in self.get_alive_players() if not p.investigated and p != player]
            if targets:
                investigate_target = random.choice(targets)
                self.game_narrative.append(f"[{self.format_time()}] {player.name} (Journalist) is observing {investigate_target.name}.")
                found_role = investigate_target.role
                investigation_successful = False
                if (player.traits["Observance"] > 0.6 and found_role == "Terrorist") or \
                   (player.traits["Skeptical"] > 0.7 and found_role != "Terrorist" and investigate_target.suspicion > 0.5):
                    investigation_successful = True
                player.adjust_traits_based_on_investigation(investigation_successful)
                investigate_target.investigated = True
                self.journalist_investigations[investigate_target.name] = found_role
                print(f"[{self.format_time()}] {player.name} investigated {investigate_target.name} and found they are the {found_role}.")
                self.game_narrative.append(f"{player.name} investigated {investigate_target.name} and found they are the {found_role}.")
                for p in self.players:
                    if p == investigate_target:
                        p.suspicion += 1
            elif not self.journalist_revealed and self.round >= 5 and self.get_alive_players() and player.traits["Helpfulness"] < 0.3 and player.traits["Cautiousness"] < 0.7:
                print(f"[{self.format_time()}] !!! Journalist {player.name} takes a risk and reveals their identity !!!")
                self.journalist_revealed = True
                self.game_narrative.append(f"{player.name} revealed their identity as the Journalist!")

        elif player.role == "Fanatic":
            provoke_chance = player.traits["Deception"] * (1 - player.traits["Cautiousness"])
            if random.random() < provoke_chance:
                self.game_narrative.append(f"{player.name} (Fanatic) acts provocatively.")
            else:
                self.game_narrative.append(f"{player.name} (Fanatic) subtly hopes for their demise.")

        elif player.role == "Ordinary Citizen":
            suspicion_increase = 0.01 * player.traits["Paranoia"] - 0.005 * player.traits["Cautiousness"]
            player.suspicion += suspicion_increase
            self.game_narrative.append(f"{player.name} (Ordinary Citizen) looks around with {'heightened suspicion' if player.traits['Paranoia'] > 0.5 else 'nervousness'}.")

    def apply_virus_effects(self):
        infected_alive = [p for p in self.get_alive_players() if p.infected]
        for player in infected_alive:
            infection_risk = 0.1 + 0.05 * player.traits["Vulnerability"] - 0.02 * player.traits["Resistance"]
            if random.random() < infection_risk:
                print(f"[{self.format_time()}] !!! {player.name} succumbed to the virus !!!")
                self.game_narrative.append(f"{player.name} succumbed to the virus.")
                player.alive = False
                if player.role == "Terrorist":
                    self.terrorists_alive -= 1

    def check_win_conditions(self):
        terrorists_alive = sum(1 for p in self.players if p.role == "Terrorist" and p.alive)
        officer_alive = any(p.role == "Officer" and p.alive for p in self.players)
        researcher_alive = any(p.role == "Researcher" and p.alive for p in self.players)

        if terrorists_alive >= sum(1 for p in self.players if p.role != "Terrorist" and p.alive):
            self.game_over = True
            self.winner = "Terrorists"
            return True
        elif not terrorists_alive and (officer_alive or researcher_alive or any(p.role == "Journalist" and p.alive for p in self.players)):
            self.game_over = True
            self.winner = "Citizens"
            return True
        elif not self.get_alive_players():
            self.game_over = True
            self.winner = "Nobody"
            return True
        return False

    def play_round(self):
        self.clear_screen()
        self.display_game_info()
        self.display_players()
        self.display_narrative()

        self.round += 1
        print(f"\n--- Round {self.round} Begins ---")
        alive_players = self.get_alive_players()
        random.shuffle(alive_players)

        for player in alive_players:
            self.player_action(player)

        self.apply_virus_effects()

        if self.check_win_conditions():
            self.clear_screen()
            self.display_game_info()
            self.display_players()
            print(f"\n--- Game Over! {self.winner} Win! ---")
            return

        self.rounds_without_terrorist_kill += 1
        if any(p.role == "Terrorist" and p.alive for p in self.players) and self.rounds_without_terrorist_kill >= 7 and not self.journalist_revealed and self.journalist:
            print(f"[{self.format_time()}] !!! Growing desperation! The Journalist might be forced to act...")
            self.player_action(self.journalist)

        if not self.game_over:
            pause_duration = random.uniform(2, 5)
            time.sleep(pause_duration)
            print(f"[{self.format_time()}] --- End of Round Pause ---")
            if random.random() < 0.3:
                self.player_interactions()

        for player in self.players:
            if player.alive:
                player.suspicion += 0.001 * (player.traits["Paranoia"] - player.traits["Observance"])
                player.suspicion = max(0, min(1, player.suspicion))
                player.learn_from_suspicion(self.round_history[-1] if self.round_history else None)

    def start_game(self):
        print("--- The Virus Game ---")
        self.setup_game()
        self.display_players()
        self.game_over = False
        self.winner = None
        self.rounds_without_terrorist_kill = 0

        while not self.game_over:
            self.play_round()
            if self.game_over:
                break
            if not any(p.role == "Terrorist" and p.alive for p in self.players):
                self.game_over = True
                self.winner = "Citizens"
            elif not any(p.role not in ["Terrorist", "Fanatic"] and p.alive for p in self.players):
                self.game_over = True
                self.winner = "Terrorists"
            elif self.round > 30: # Increased failsafe rounds
                print("\n--- The situation has become too stagnant. The game ends in a draw. ---")
                self.game_over = True
                self.winner = "Draw"
                break

        print("\n--- Game Over ---")
        print(f"Winner: {self.winner}")

if __name__ == "__main__":
    game = Game()
    game.start_game()
