class GameControllerAdapter:
    def __init__(self, ctl):
        self.ctl = ctl
    
    def is_final(self):
        return self.ctl.game.winner != None
    
    def successors(self):
        # Actions consist of pairs of pieces and target fields.
        # Beware that actions are valid only for the specific game state instance!
        # I.e., we cannot execute this action on a different instance of the same game state.
        # Instead, we need to use the coordinates of the start- and target field.
        successors = []
        actions = self.ctl.get_possible_moves()
        for action in actions:
            piece, targets = action
            for target in targets:
                newState = self.ctl.get_deep_copy()
                newState.move(piece.coordinates(), target.coordinates(), verbose=False)
                newState = GameControllerAdapter(newState)
                successors.append((newState, (piece, target)))
        return successors
    
    def perform_random_action(self):
        moves = self.ctl.get_possible_moves()
        moves = [(piece, target) for piece, targets in moves for target in targets]
        import random
        random_move = random.choice(moves)
        newState = self.ctl.get_deep_copy()
        piece, target = random_move
        newState.move(piece.coordinates(), target.coordinates(), verbose=False)
        return GameControllerAdapter(newState)
    
    def winner(self, i):
        # Even node levels of the game tree correspond to the black player.
        player_to_value = self.ctl.game.players[(i+1)%2]
        if self.ctl.game.winner is None:
            raise Exception("Game not finished yet.")
        return player_to_value == self.ctl.game.winner
