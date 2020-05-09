class GameController:
    def __init__(self):
        self.game = Game()

        whitePlayer = Player("white")
        blackPlayer = Player("black")
        whitePlayer.game = self.game
        blackPlayer.game = self.game
        self.game.players.append(whitePlayer)
        self.game.players.append(blackPlayer)
        self.game.activePlayer = whitePlayer

        self.game.board = self.init_board()
        
        self.init_piece(Rook, whitePlayer, 0, 0)
        self.init_piece(Rook, whitePlayer, 7, 0)
        self.init_piece(Rook, blackPlayer, 0, 7)
        self.init_piece(Rook, blackPlayer, 7, 7)
        
    def init_piece(self, constructor, player, x, y):
        piece = constructor()
        piece.player = player
        player.pieces.append(piece)
        field = self.game.board.fields[x][y]
        piece.set_field(field)

    def init_board(self):
        board = Board()

        cols = "ABCDEFGH"
        rows  = "12345678"
        for x in range(8):
            field_row = []
            for y in range(8):
                name = cols[x] + rows[y]
                field = Field()
                field.name = name
                field.board = board
                field.x = x
                field.y = y

                field_row.append(field)
            board.fields.append(field_row)
        return board

    def get_possible_piece_moves(self, piece):
        possible_moves = []
        for y in reversed(range(8)):
            for x in range(8):
                field = self.game.board.fields[x][y]
                if piece.can_move_to(field):
                    possible_moves.append(field)
        return possible_moves

    def print_possible_moves(self, piece):
        possible_moves = ""
        for y in reversed(range(8)):
            for x in range(8):
                field = self.game.board.fields[x][y]
                if field.piece == piece:
                    possible_moves += " o"
                    continue
                possible_move = piece.can_move_to(field)
                #possible_moves += field.name
                possible_moves += " ." if possible_move else " x"
            possible_moves += '\n'
        print(possible_moves)

    def get_possible_moves(self):
        """ Returns all possible moves for the active player. 
            Returns a list of tuples (piece, moves) where moves is a list of fields where piece can be moved to.
        """
        possible_moves = []
        player = self.game.activePlayer
        for piece in player.pieces:
            moves = self.get_possible_piece_moves(piece)
            possible_moves.append((piece, moves))
        return possible_moves

    def move(self, start, target, verbose=True):
        """ Move a piece based on coordinates. Start and target must be tuples (x,y) of field indices. """
        xs, ys = start
        xt, yt = target
        piece = self.game.board.fields[xs][ys].piece
        field = self.game.board.fields[xt][yt]
        return self.move_piece(piece, field, verbose=verbose)

    def move_piece(self, piece, field, check_possible_move=True, verbose=True):
        # Check whether game is already finished.
        if self.game.winner is not None:
            print("Game is already finished.")
            return False

        # Check whether the piece belongs to the active player.
        if piece.player != self.game.activePlayer:
            print("Cannot move piece of inactive player!")
            return False
            
        # Check whether the piece can be moved to the target field.
        # For performance reasons, we can deactivate this.
        # Generated possible moves have already been checked.
        if check_possible_move and not piece.can_move_to(field):
            print("Move to field not possible°")
            return False
        
        # Piece at the target location gets beaten.
        if field.piece is not None:
            beaten_piece = field.piece
            field.piece = None
            beaten_piece.player.pieces.remove(beaten_piece)
            self.game.beatenPieces.append(beaten_piece)
            if verbose:
                print("Beaten piece")
        piece.set_field(field)

        # New active player.
        self.switch_active_player()

        # Check whether the game is finished.
        winner = self.check_winner()
        if winner is not None:
            self.game.winner = winner
            #print("Game finished. Winner is " + str(winner))
        return True

    def check_winner(self):
        if self.game.is_finished():
            for player in self.game.players:
                if len(player.pieces) != 0:
                    return player
        return None

    def switch_active_player(self):
        for player in self.game.players:
            if player != self.game.activePlayer:
                self.game.activePlayer = player
                return

    def get_deep_copy(self):
        from copy import deepcopy
        return deepcopy(self)

class Game:
    def __init__(self):
        self.players = [] 
        self.activePlayer = None
        self.board = None
        self.winner = None
        self.beatenPieces = []
    
    def is_finished(self):
        for player in self.players:
            if len(player.pieces) == 0:
                return True
        return False
    
    def status(self, field_names=False):
        status = ""
        for y in reversed(range(8)):
            for x in range(8):
                field = self.board.fields[x][y]
                if field_names:
                    status += field.name
                if field.piece is None:
                    status += " ."
                elif field.piece.player.color == "black":
                    status += " o"
                else:
                    status += " x"
            status += "\n"
        status += "Active Player: " + str(self.activePlayer) + "\nWinner: " + str(self.winner)
        return status

class Player:
    def __init__(self, color):
        self.color = color
        self.pieces = [] 
        self.game = None

    def __str__(self):
        return self.color
        

class Board:
    def __init__(self):
        # Fields are two-dimensional and indexed by fields[x][y]. First is column (letters) then row. fields[0][0] is A1. fields[7][7] is H8.
        self.fields = []

    def is_space_free(self, start_field, target_field):
        # Start and target are the same. Return False (since this means, we cannot move).
        if start_field.x == target_field.x and start_field.y == target_field.y:
            return True

        # There is already a piece by the same player at the target position. Movement is not possible.
        if target_field.piece is not None and start_field.piece is not None and start_field.piece.player == target_field.piece.player:
            return False 


        # Determine iterator "next_field", which gives the coordinates of the next field depending on movement in column, row or diagonal.
        # Movement in same column
        if start_field.x == target_field.x:
            if target_field.y > start_field.y:
                next_field = lambda x, y: (x, y+1)
            else:
                next_field = lambda x, y: (x, y-1)

        # Movement in same row
        if start_field.y == target_field.y:
            if target_field.x > start_field.x:
                next_field = lambda x, y: (x+1, y)
            else:
                next_field = lambda x, y: (x-1, y)

        # Diagonal Movement in both directions
        # TODO for none-towers        


        # Iterate over fields and find whether the space between start and target is free.
        field = start_field
        x, y = next_field(field.x, field.y)
        field = self.fields[x][y]
        while field != target_field:
            # Piece is on field between start and target.
            if field.piece is not None:
                return False
            x, y = next_field(field.x, field.y)
            field = self.fields[x][y]
        # Iterated up to the target field. Now space is free if target is free or enemy piece is on the space.
        return field.piece is None or field.piece.player != start_field.piece.player
           
class Field:
    def __init__(self):
        self.name = None
        self.piece = None
        self.board = None
        self.x = 0 # (0,0) is A1, (7,7) is H8
        self.y = 0
    
    def set_piece(self, piece):
        # Remove previous association to self.
        if self.piece is not None:
            self.piece.field = None

        # Set association to None.
        if piece is None:
            self.piece = None
            return

        # Set new association with referential integrity.
        self.piece = piece
        if piece.field != self:
            piece.set_field(self)
    
    def coordinates(self):
        return self.x, self.y

class Piece:
    """ An abstract game piece. """
    def __init__(self):
        self.player = None
        self.field = None

    def set_field(self, field):
        if self.field is not None:
            self.field.piece = None

        if field is None:
            self.piece = None
            return

        self.field = field
        if field.piece != self:
            field.set_piece(self)

    def coordinates(self):
        return self.field.coordinates()

    def can_move_to(self, field):
        raise NotImplementedError

class Rook(Piece):
    def can_move_to(self, field):
        return (field.x == self.field.x and field.y != self.field.y or field.y == self.field.y and field.x != self.field.x) and self.field.board.is_space_free(self.field, field)
