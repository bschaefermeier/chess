from .chess import GameController, Game

def shuffle(l):
    import random
    return random.shuffle(l[:])

class MCTS:
    """ Implementation of Monte Carlo Tree Search.
        The current game state is passed to this.
        A game state must implement the following methods:
        is_final() - Returns true, if the game is in a final state, where no further moves can be done.
        successors() - Returns possible subsequent states.
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
            max_score, max_child = 0, None
            for child in shuffle(l.children):
                score = child.get_uct()
                if score > max_score:
                    max_score = score
                    max_child = child
            l = max_child
        return l 

    def expansion(self, l, n_children = 1):
        """ Expand the game tree to a new node C, if the selected leave node is not from a final state. """
        if not l.state.is_final():
            next_state = shuffle(l.state.successors())[:n_children]
            c = Node(next_state)
            l.add_child(c)
            return c
        return None

    def simulation(self, c):
        """ Simulate a random playout from C. """
        state = c.state
        i = c.node_level
        while not state.is_final():
            state = state.perform_random_action()
            i += 1
        winner = state.winner(i)
        return winner

    def backpropagation(self, c, winner):
        """ Backpropagate the result of the playout up the path to the root node R. """
        c.inc_simulations(winner)

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
            self.parent.inc_simulations(self, not win)

    def get_uct(self):
        if self.parent is None:
            raise Exception("Calculation of uct is not valid for a root node.")
        import math
        exploration = self.wins/self.simulations 
        c = math.sqrt(2)
        exploitation = c*math.sqrt(math.log(self.parent.simulations)/self.simulations)
        return exploration + exploitation
    
    def has_children(self):
        return len(self.children) > 0
