from .chess import GameController, Game

def shuffle(l):
    import random
    result = l[:]
    random.shuffle(result)
    return result

class MCTS:
    """ Implementation of Monte Carlo Tree Search.
        The current game state is passed to this.
        A game state must implement the following methods:
        is_final() - Returns true, if the game is in a final state, where no further moves can be done.
        successors() - Returns possible subsequent states together with the moves that led to them (i.e., a list of pairs (state, move)). 
        perform_random_action() - Do a random action and return the state.
        winner(i) - Whether the player (depending on the node level i) has won the game or not.
    """
    def __init__(self, state):
        # The full tree (i.e., also nodes that have been already done).
        # Using this, we can save the tree for future games.
        # Not using this, we can save memory.
        # For now, we use it.
        self.tree = Node(state)
        # The current game state.
        self.node = self.tree 

    def selection(self):
        """ Starting from the current game state, the root node R, select a leaf node L from which to expand the game tree. """
        import random
        l = self.node
        while l.has_children():
            max_score, max_child = -1, None
            for child in shuffle(l.children):
                score = child.get_uct()
                if score > max_score:
                    max_score = score
                    max_child = child
            l = max_child
        return l 

    def expansion(self, l, n_children = 3):
        """ Expand the game tree to a new node C, if the selected leave node is not from a final state. """
        import random
        if not l.state.is_final():
            possible_moves = l.state.successors()
            next_states = random.sample(possible_moves, k=min(len(possible_moves), n_children))
            for next_state, move in next_states:
                c = Node(next_state)
                c.move = move
                l.add_child(c)
            return c
        return None

    def simulation(self, c, verbose=False):
        """ Simulate a random playout from C. """
        state = c.state
        i = c.node_level
        while not state.is_final():
            state = state.perform_random_action()
            if verbose:
                print(state.ctl.game.status())
        winner = state.winner(i)
        return winner

    def backpropagation(self, c, winner):
        """ Backpropagate the result of the playout up the path to the root node R. """
        c.inc_simulations(winner)

    def run(self, n_simulations=1000, verbose=True, print_every=50, n_children=100):
        """ Runs the full Monte Carlo tree search. 
            n_simulations: The number of simulations to run.
            verbose: Whether to print stats (number of simulations).
            print_every: After how many simulations to print the current status.
            n_children: how many child nodes to expand from a node at most.
        """
        for i in range(n_simulations):
            l = self.selection()
            c = self.expansion(l, n_children=n_children)
            
            # When l was a final state already, expansion returns None.
            # In this case we only run another "simulation" starting from l (which just returns the winner of l).
            # Altogether, the result is another backpropagation of the winner in l.
            if c is None:
                c = l
            winner = self.simulation(c, verbose=False)
            self.backpropagation(c, winner)
            if verbose and i%print_every == 0:
                print(f"{i} simulations run.")

    def best_moves(self):
        return self.node.rank_child_nodes()

class Node:
    """ A node of the tree.
        A node holds a game state, the move that led to this state, 
        the number of wins of the active player, the number of simulations run, the child nodes and the parent node.
    """
    def __init__(self, state, move=None, copystate=False):
        from copy import deepcopy
        if copystate:
            state = deepcopy(state)
        self.state = state
        self.node_level = 0
        self.move = move
        self.wins = 0
        self.simulations = 0
        self.children = []
        self.parent = None

    def add_child(self, node):
        self.children.append(node)
        node.parent = self
        node.node_level = self.node_level + 1

    def inc_simulations(self, win):
        self.simulations += 1
        if win:
            self.wins += 1

        # Backpropagate simulations up the tree.
        # In the parent node, the other player is active. Hence, a win in the current node is a loss in the parent node.
        if self.parent is not None:
            self.parent.inc_simulations(not win)

    def get_uct(self):
        if self.parent is None:
            raise Exception("Calculation of uct is not valid for a root node.")
        import math
        if self.simulations == 0:
            return float("inf")
        exploitation = self.wins/self.simulations 
        c = math.sqrt(2)
        exploration = c*math.sqrt(math.log(self.parent.simulations)/self.simulations)
        return exploration + exploitation
    
    def has_children(self):
        return len(self.children) > 0

    def status(self):
        return self.state.ctl.game.status()

    def print_moves_to(self):
        node = self
        moves = [node]
        while node.parent is not None:
            node = node.parent
            moves = [node] + moves
        for m in moves:
            print(m)
            print(m.status())

    def rank_child_nodes(self):
        # Child nodes are ranked by the number of simulations run. Best actions have more simulations.
        return sorted([c for c in self.children], reverse=True, key=lambda c: c.simulations )

    def best_child(self):
        if self.has_children():
            return self.rank_child_nodes()[0]
        return None

    def __repr__(self):
        result = ""
        result += "Node level: " + str(self.node_level) + "\n"
        result += "Wins: " + str(self.wins) + "/" + str(self.simulations)
        return result
