import random
import time


class Agent:
    def __init__(self, agent_id, initial_traits=None):
        self.id = agent_id
        self.alive = True
        self.health = 100
        self.energy = 100
        self.trust = {}
        self.traits = initial_traits if initial_traits else {
            "bravery": random.uniform(0, 1),
            "cunning": random.uniform(0, 1),
            "empathy": random.uniform(0, 1),
            "aggression": random.uniform(0, 1),
            "risk_aversion": random.uniform(0, 1),
            "strength": random.uniform(0, 1),
            "teamwork": random.uniform(0, 1),
            "observation": random.uniform(0, 1),
            "deception": random.uniform(0, 1)
        }
        self.memory = []

    def __repr__(self):
        return f"Agent {self.id} (Alive: {self.alive})"

    def perceive(self, environment, current_game):
        """
        Placeholder for agent's perception of the environment.
        Eventually, this would involve processing sensory data.
        """
        pass

    def decide_action(self, game_state, current_game):
        if current_game == "red_light_green_light":
            if game_state.get("is_green_light", False):
                # More likely to move on green
                return random.choices(["move", "stop"], weights=[0.8, 0.2], k=1)[0]
            else:
                # More likely to stop on red, but with a small chance of moving
                return random.choices(["stop", "move"], weights=[0.95, 0.05], k=1)[0]
        elif current_game == "honeycomb":
            return random.choice(["try_cut_carefully", "try_cut_fast"])
        elif current_game == "tug_of_war":
            return random.choice(["pull_hard", "pull_strategically"])
        elif current_game == "marbles":
            return random.choice(["guess_even", "guess_odd"])
        elif current_game == "glass_bridge":
            return random.choice(["choose_left", "choose_right", "push"])
        elif current_game == "squid_game":
            return random.choice(["attack", "defend"])
        return "idle"

    def act(self, action, environment, current_game, target=None):
        """
        Placeholder for game-specific actions.
        """
        print(f"Agent {self.id} performs action: {action} in {current_game}")

    def interact(self, other_agent, environment):
        """
        Placeholder for interaction logic between agents.
        Trust levels and relationships would be updated here (using ML later).
        """
        print(f"Agent {self.id} interacts with Agent {other_agent.id}")
        # Basic trust update (to be replaced with ML model)
        if other_agent.id not in self.trust:
            self.trust[other_agent.id] = 0.5
        if random.random() > 0.5:
            self.trust[other_agent.id] += 0.05
        else:
            self.trust[other_agent.id] -= 0.05
        self.trust[other_agent.id] = max(0, min(1, self.trust[other_agent.id]))
        self.memory.append(f"Interacted with Agent {other_agent.id}")

    def update_state(self, outcome, current_game, eliminated_by=None):
        """
        State updates based on game outcomes.
        """
        if outcome == "eliminated":
            self.alive = False
            print(f"Agent {self.id} was eliminated in {current_game}" + (f" by Agent {eliminated_by.id}" if eliminated_by else ""))
        self.memory.append(f"Experienced outcome: {outcome}")

class GameEnvironment:
    def __init__(self, num_agents):
        self.agents = [Agent(i) for i in range(num_agents)]
        self.current_game_index = 0
        self.games = ["red_light_green_light", "honeycomb", "tug_of_war", "marbles", "glass_bridge", "squid_game"]
        self.game_state = {} # Game-specific state

    def start_game(self):
        print("--- Squid Game Simulation Started ---")
        while self.current_game_index < len(self.games) and sum(1 for a in self.agents if a.alive) > 1:
            current_game = self.games[self.current_game_index]
            print(f"\n--- Starting Game: {current_game.upper()} ---")
            self.play_game(current_game)
            if sum(1 for a in self.agents if a.alive) <= 1:
                break
            self.current_game_index += 1

        print("\n--- Simulation Ended ---")
        remaining_agents = [agent for agent in self.agents if agent.alive]
        print(f"Remaining Agents: {len(remaining_agents)}")
        if len(remaining_agents) == 1:
            print(f"Winner: {remaining_agents[0]}")
        else:
            print("No clear winner.")

    def play_game(self, game_name):
        if game_name == "red_light_green_light":
            self.play_red_light_green_light()
        elif game_name == "honeycomb":
            self.play_honeycomb()
        elif game_name == "tug_of_war":
            self.play_tug_of_war()
        elif game_name == "marbles":
            self.play_marbles()
        elif game_name == "glass_bridge":
            self.play_glass_bridge()
        elif game_name == "squid_game":
            self.play_squid_game()
        else:
            print(f"Unknown game: {game_name}")

    def play_red_light_green_light(self):
        print("\n--- RED LIGHT, GREEN LIGHT (ASCII GUI) ---")
        game_round = 0
        finish_line = 50
        agent_positions = {agent.id: 0 for agent in self.agents if agent.alive}
        eliminated_this_game = []

        while any(agent.alive and agent_positions[agent.id] < finish_line for agent in self.agents) and game_round < 100:
            game_round += 1
            is_green_light = random.choice([True, False])
            call = "GREEN LIGHT!" if is_green_light else "RED LIGHT!"
            print(f"\nRound {game_round}: **{call}**")
            self.game_state["is_green_light"] = is_green_light
            agents_moved_this_round = {}
            for agent in self.agents:
                if agent.alive and agent_positions[agent.id] < finish_line:
                    action = agent.decide_action(self.game_state, "red_light_green_light")
                    agent.act(action, self, "red_light_green_light", None)
                    if is_green_light and action == "move":
                        move_amount = int(random.uniform(1, 5) * agent.traits["bravery"])
                        agent_positions[agent.id] += move_amount
                        agents_moved_this_round[agent.id] = move_amount
                    elif not is_green_light and action == "move":
                        if agent not in eliminated_this_game:
                            agent.update_state("eliminated", "red_light_green_light")
                            eliminated_this_game.append(agent)

            # --- ASCII GUI ---
            print("-" * (finish_line + 10))
            for agent in self.agents:
                if agent.alive:
                    pos = agent_positions[agent.id]
                    progress_bar = "[" + "=" * pos + ">" + " " * (finish_line - pos) + "]"
                    print(f"Agent {agent.id:3}: {progress_bar} ({pos}/{finish_line})")
            print("-" * (finish_line + 10))

            for agent_id, moved in agents_moved_this_round.items():
                pass # We've shown movement in the GUI

            time.sleep(0.5)
            winners = [agent_id for agent_id, pos in agent_positions.items() if pos >= finish_line]
            if winners:
                print(f"\nWinners reached the finish line: {winners}")
                break

        print("\nRed Light, Green Light ended.")
        if eliminated_this_game:
            print("\nEliminated this round:")
            for agent in eliminated_this_game:
                print(f"Agent {agent.id}")

        self.agents = [a for a in self.agents if a.alive and a not in eliminated_this_game]

    def play_honeycomb(self):
        print("\n--- HONEYCOMB/DALGONA (SQUAD GUI) ---")
        shapes = ["circle", "triangle", "star", "umbrella"]
        shape_difficulties = {"circle": 0.1, "triangle": 0.2, "star": 0.35, "umbrella": 0.5}
        chosen_shape = random.choice(shapes)
        difficulty = shape_difficulties[chosen_shape]
        print(f"The shape is: **{chosen_shape.upper()}** (Difficulty: {difficulty:.2f})")
        eliminated_this_round = []
        alive_agents = [agent for agent in self.agents if agent.alive]
        num_alive = len(alive_agents)

        if num_alive < 4:
            print("Not enough players to form 4 teams. Proceeding with individual attempts.")
            # Fallback to the previous individual attempt GUI
            print("\nTarget Shape:")
            if chosen_shape == "circle": print("   @@@   \n  @   @  \n @     @ \n @     @ \n  @   @  \n   @@@   ")
            elif chosen_shape == "triangle": print("    ^    \n   / \\   \n  /   \\  \n /_____\\ ")
            elif chosen_shape == "star": print("    * \n   * * \n  ***** \n   * * \n    * ")
            elif chosen_shape == "umbrella": print("   _.-._   \n  / \\_/ \\  \n | |   | | \n |_|   |_| \n   \\ /   \n    '    ")
            print("-" * 20)
            for agent in alive_agents:
                strategy = agent.decide_action(self.game_state, "honeycomb")
                agent.act(strategy, self, "honeycomb", chosen_shape)
                cunning_factor = agent.traits["cunning"]
                success_chance = 0.6 + cunning_factor * 0.3 - difficulty
                success_chance = max(0.05, min(0.95, success_chance))
                result = "SUCCESS" if random.random() <= success_chance else "**BROKE**"
                print(f"Agent {agent.id:3}: Attempting... [{'O' if result == 'SUCCESS' else 'X'}] ({result})")
                if result == "**BROKE**":
                    agent.update_state("eliminated", "honeycomb")
                    eliminated_this_round.append(agent)
                time.sleep(0.4)
            print("-" * 20)
        else:
            teams = []
            symbols = ["@", "#", "$", "%"]
            random.shuffle(alive_agents)
            agents_per_team = num_alive // 4
            remaining_agents = num_alive % 4
            start_index = 0

            print("\n--- TEAMS ---")
            for i in range(4):
                team_size = agents_per_team + (1 if i < remaining_agents else 0)
                team = alive_agents[start_index : start_index + team_size]
                teams.append(team)
                team_symbol = symbols[i]
                team_ids = [agent.id for agent in team]
                print(f"Team {team_symbol}: Agents {team_ids}")
                start_index += team_size
            print("-" * 20)
            print("\nTarget Shape:")
            if chosen_shape == "circle": print("   @@@   \n  @   @  \n @     @ \n @     @ \n  @   @  \n   @@@   ")
            elif chosen_shape == "triangle": print("    ^    \n   / \\   \n  /   \\  \n /_____\\ ")
            elif chosen_shape == "star": print("    * \n   * * \n  ***** \n   * * \n    * ")
            elif chosen_shape == "umbrella": print("   _.-._   \n  / \\_/ \\  \n | |   | | \n |_|   |_| \n   \\ /   \n    '    ")
            print("-" * 20)

            team_results = {symbols[i]: 0 for i in range(4)} # 0 = ongoing, 1 = success, -1 = failure

            for i in range(4):
                team = teams[i]
                team_symbol = symbols[i]
                print(f"\nTeam {team_symbol} is attempting...")
                team_success = True
                for agent in team:
                    strategy = agent.decide_action(self.game_state, "honeycomb")
                    agent.act(strategy, self, "honeycomb", chosen_shape)
                    cunning_factor = agent.traits["cunning"]
                    success_chance = 0.6 + cunning_factor * 0.3 - difficulty
                    success_chance = max(0.05, min(0.95, success_chance))
                    result = "SUCCESS" if random.random() <= success_chance else "**BROKE**"
                    print(f"  Agent {agent.id:3} ({team_symbol}): [{'O' if result == 'SUCCESS' else 'X'}] ({result})")
                    if result == "**BROKE**":
                        team_success = False
                        agent.update_state("eliminated", "honeycomb")
                        eliminated_this_round.append(agent)
                    time.sleep(0.3)

                if team_success:
                    team_results[team_symbol] = 1
                    print(f"\nTeam {team_symbol} **SUCCEEDED**!")
                else:
                    team_results[team_symbol] = -1
                    print(f"\nTeam {team_symbol} **FAILED**!")

            print("\n--- TEAM RESULTS ---")
            for symbol, result in team_results.items():
                if result == 1:
                    print(f"Team {symbol}: **SURVIVED**")
                elif result == -1:
                    print(f"Team {symbol}: **ELIMINATED**")
                else:
                    print(f"Team {symbol}: Result unclear (shouldn't happen)")

        if eliminated_this_round:
            print("\nEliminated this round:")
            for agent in eliminated_this_round:
                print(f"Agent {agent.id}")

        self.agents = [a for a in self.agents if a.alive and a not in eliminated_this_round]

    def play_tug_of_war(self):
        print("\n--- TUG-OF-WAR (ASCII GUI) ---")
        alive_agents = [a for a in self.agents if a.alive]
        num_alive = len(alive_agents)

        if num_alive < 2:
            print("Not enough players for Tug-of-War.")
            return

        random.shuffle(alive_agents)
        team1 = alive_agents[:num_alive // 2]
        team2 = alive_agents[num_alive // 2:]

        team1_ids = [a.id for a in team1]
        team2_ids = [a.id for a in team2]

        print(f"Team 1: Agents {team1_ids}")
        print(f"Team 2: Agents {team2_ids}")
        print("-" * 30)
        print("        Team 1        |        Team 2        ")
        print("       ( <--- )       |       ( ---> )       ")
        print("-" * 30)

        pulling_power1 = sum(a.traits["strength"] + a.traits["teamwork"] * 0.5 for a in team1)
        pulling_power2 = sum(a.traits["strength"] + a.traits["teamwork"] * 0.5 for a in team2)

        rope_position = 0  # 0 is center, negative is Team 1 advantage, positive is Team 2 advantage
        pulls = 0
        max_pulls = 20

        while abs(rope_position) < 10 and pulls < max_pulls and any(a.alive for a in self.agents if a in team1 or a in team2):
            pulls += 1
            action1 = random.choice(["pull_hard", "pull_strategically"]) # Basic team actions for now
            action2 = random.choice(["pull_hard", "pull_strategically"])

            pull_strength1 = pulling_power1 * random.uniform(0.8, 1.2)
            pull_strength2 = pulling_power2 * random.uniform(0.8, 1.2)

            difference = pull_strength1 - pull_strength2
            rope_position -= difference * 0.1  # Adjust rope position based on strength difference

            # --- ASCII GUI for Rope Position ---
            gui_length = 30
            center = gui_length // 2
            rope_visual = " " * gui_length
            rope_index = int(center - rope_position)
            if 0 <= rope_index < gui_length:
                rope_visual = rope_visual[:rope_index] + "|" + rope_visual[rope_index + 1:]

            team1_label = "Team 1"
            team2_label = "Team 2"
            visual_output = f"{team1_label:^15} <---{rope_visual}---> {team2_label:^15}"
            print(f"Pull {pulls:2}: {visual_output}")
            time.sleep(0.5)

        eliminated_team = None
        if rope_position <= -10:
            eliminated_team = team2
            print("\nTeam 1 wins!")
        elif rope_position >= 10:
            eliminated_team = team1
            print("\nTeam 2 wins!")
        else:
            # In case of a draw after max pulls (unlikely with the continuous rope movement)
            if pulling_power1 > pulling_power2:
                eliminated_team = team2
                print("\nTeam 1 wins (by slight advantage)!")
            elif pulling_power2 > pulling_power1:
                eliminated_team = team1
                print("\nTeam 2 wins (by slight advantage)!")
            else:
                eliminated_team = random.choice([team1, team2])
                print("\nIt's a draw! Team", 1 if eliminated_team == team1 else 2, "loses by chance!")

        if eliminated_team:
            print("Eliminated from the losing team:")
            for agent in eliminated_team:
                agent.update_state("eliminated", "tug_of_war")
            self.agents = [a for a in self.agents if a not in eliminated_team]
        else:
            print("No eliminations in this round (very unlikely).")


    def play_marbles(self):
        print("\n--- MARBLES (ASCII GUI) ---")
        alive_agents = [a for a in self.agents if a.alive]
        if not alive_agents:
            print("No players alive to play Marbles.")
            return

        random.shuffle(alive_agents)
        pairs = [(alive_agents[i], alive_agents[i+1]) for i in range(0, len(alive_agents) - 1, 2)]
        eliminated_this_round = []
        self.game_state['marbles_pairs'] = [(player1.id, player2.id) for player1, player2 in pairs] # Store pairs

        print("\nPairs for the Marbles game:")
        for player1, player2 in pairs:
            print(f"Agent {player1.id} vs Agent {player2.id}")

        print("\nThe Marbles games begin...")
        time.sleep(1)

        for player1, player2 in pairs:
            if not player1.alive or not player2.alive:
                continue

            print(f"\n--- Match: Agent {player1.id} vs Agent {player2.id} ---")
            # Each player starts with a random number of marbles (between 1 and 10)
            marbles1 = random.randint(1, 10)
            marbles2 = random.randint(1, 10)
            print(f"Agent {player1.id} has {marbles1} marbles, Agent {player2.id} has {marbles2} marbles")

            # A simple guessing game for marbles
            for round_num in range(3):  # Give each pair a few rounds
                print(f"\n--- Round {round_num + 1} ---")
                guess1 = player1.decide_action(self.game_state, "marbles")
                guess2 = player2.decide_action(self.game_state, "marbles")

                print(f"Agent {player1.id} guesses {guess1}.")
                print(f"Agent {player2.id} guesses {guess2}.")

                if guess1 == "guess_even":
                    if marbles2 % 2 == 0:
                        print(f"Agent {player1.id} wins this round.")
                        marbles1 += marbles2
                        marbles2 = 0
                    else:
                        print(f"Agent {player2.id} wins this round.")
                        marbles2 += marbles1
                        marbles1 = 0
                elif guess1 == "guess_odd":
                    if marbles2 % 2 != 0:
                        print(f"Agent {player1.id} wins this round.")
                        marbles1 += marbles2
                        marbles2 = 0
                    else:
                        print(f"Agent {player2.id} wins this round.")
                        marbles2 += marbles1
                        marbles1 = 0

                elif guess2 == "guess_even":
                    if marbles1 % 2 == 0:
                        print(f"Agent {player2.id} wins this round.")
                        marbles2 += marbles1
                        marbles1 = 0
                    else:
                        print(f"Agent {player1.id} wins this round.")
                        marbles1 += marbles2
                        marbles2 = 0
                elif guess2 == "guess_odd":
                    if marbles1 % 2 != 0:
                        print(f"Agent {player2.id} wins this round.")
                        marbles2 += marbles1
                        marbles1 = 0
                    else:
                        print(f"Agent {player1.id} wins this round.")
                        marbles1 += marbles2
                        marbles2 = 0
                else: # tie
                    print("Its a tie")

                print(f"Agent {player1.id} has {marbles1} marbles, Agent {player2.id} has {marbles2} marbles")
                time.sleep(1)

            # Determine winner of the pair
            if marbles1 > marbles2:
                winner = player1
                loser = player2
            elif marbles2 > marbles1:
                winner = player2
                loser = player1
            else: #ran out of rounds
                if player1.traits["cunning"] > player2.traits["cunning"]: # tie breaker
                  winner = player1
                  loser = player2
                else:
                  winner = player2
                  loser = player1

            print(f"Agent {winner.id} wins the match!")
            loser.update_state("eliminated", "marbles", eliminated_by=winner)
            eliminated_this_round.append(loser)

        self.agents = [a for a in self.agents if a.alive and a not in eliminated_this_round]
        print("Marbles ended.")


    def play_glass_bridge(self):
        print("\n--- GLASS BRIDGE ---")
        alive_agents = [a for a in self.agents if a.alive]
        random.shuffle(alive_agents)
        num_steps = 10
        fragile_panels = random.sample(range(num_steps), num_steps // 2)
        agents_crossed = []
        agents_fallen = []

        print("\nOrder of crossing:")
        for agent in alive_agents:
            print(f"Agent {agent.id}")

        for agent in alive_agents:
            if not agent.alive or agent in agents_crossed or agent in agents_fallen:
                continue
            print(f"\nAgent {agent.id} is now crossing the Glass Bridge...")
            for step in range(num_steps):
                choice = agent.decide_action(self.game_state, "glass_bridge")
                agent.act(choice, self, "glass_bridge")
                panel_type = "fragile" if step in fragile_panels else "safe"
                print(f"Agent {agent.id} chooses to step {'left' if choice == 'choose_left' else 'right'} on step {step + 1} ({panel_type})")
                if panel_type == "fragile" and random.random() > (0.3 + agent.traits["observation"] * 0.4):
                    print(f"**CRACK!** Agent {agent.id} fell!")
                    agent.update_state("eliminated", "glass_bridge")
                    agents_fallen.append(agent)
                    break
                else:
                    print(f"Agent {agent.id} made it across step {step + 1}.")
                time.sleep(0.7)
            if agent.alive and agent not in agents_fallen:
                print(f"\nAgent {agent.id} has crossed the Glass Bridge!")
                agents_crossed.append(agent)

        self.agents = [a for a in self.agents if a in agents_crossed]

    def play_squid_game(self):
        print("\n--- SQUID GAME ---")
        remaining_agents = [a for a in self.agents if a.alive]
        if len(remaining_agents) == 2:
            player1, player2 = remaining_agents[0], remaining_agents[1]
            print(f"\nFinal Confrontation: Agent {player1.id} vs Agent {player2.id}")
            round_num = 0
            while player1.alive and player2.alive and round_num < 10:
                round_num += 1
                action1 = player1.decide_action(self.game_state, "squid_game")
                action2 = player2.decide_action(self.game_state, "squid_game")
                player1.act(action1, self, "squid_game", player2)
                player2.act(action2, self, "squid_game", player1)

                attack_power1 = player1.traits["aggression"] + player1.traits["bravery"] * random.uniform(0.8, 1.2)
                defense_power2 = player2.traits["bravery"] + (1 - player2.traits["aggression"]) * random.uniform(0.8, 1.2)
                attack_power2 = player2.traits["aggression"] + player2.traits["bravery"] * random.uniform(0.8, 1.2)
                defense_power1 = player1.traits["bravery"] + (1 - player1.traits["aggression"]) * random.uniform(0.8, 1.2)

                print(f"\n--- Round {round_num} ---")
                print(f"Agent {player1.id} chooses to {action1}, Agent {player2.id} chooses to {action2}")

                if action1 == "attack" and attack_power1 > defense_power2 + 0.1:
                    print(f"Agent {player1.id} attacks successfully!")
                    player2.update_state("eliminated", "squid_game", eliminated_by=player1)
                    break
                elif action2 == "attack" and attack_power2 > defense_power1 + 0.1:
                    print(f"Agent {player2.id} attacks successfully!")
                    player1.update_state("eliminated", "squid_game", eliminated_by=player2)
                    break
                else:
                    print("No successful attack this round.")
                time.sleep(1)

            winner = [a for a in [player1, player2] if a.alive]
            if winner:
                print(f"\nWinner of Squid Game: Agent {winner[0].id}")
                self.agents = winner
            else:
                print("\nIt's a draw! No winner.")
                self.agents = []

        elif len(remaining_agents) == 1:
            print(f"\nAgent {remaining_agents[0].id} is the sole survivor!")
            self.agents = remaining_agents
        else:
            print("\nSomething went wrong, more than 2 or no survivors reached the final game.")
            self.agents = remaining_agents

        print("Squid Game ended.")

# --- Initializing and Running the Sequential Simulation with Rules ---
num_agents = 456
environment = GameEnvironment(num_agents)
environment.start_game()
