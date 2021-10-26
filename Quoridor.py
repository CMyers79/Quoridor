# Author: Coder Myers
# Date: 8/9/2021
# Description:  Contains Quoridor, a two player board game on a 9x9 game board.  The players start with pawns centered
# on rows 0 and 8, and must move their pawn to the opposite player's starting row to win.  Players may either move their
# pawn or place one of their 10 fences each turn.  Players may not move through fences or outside the board.  Pawns may
# be moved one space, or if pawns are adjacent, a pawn may be jumped straight over if there is no fence behind the other
# pawn, or diagonally where there is is a fence behind, but no fence to the side of the other pawn.

class QuoridorGame:
    """Contains a game of Quoridor.  Methods include move_pawn, which validates moves with _is_legal_move,
    place_fence, which validates plays with _is_fair_play and _is_legal_move, is_winner checks for a win condition,
    and print_board displays current pawn and fence positions for debugging purposes.  Initializes with a list of 3
    81 element 2D arrays for pawn and fence position."""

    def __init__(self):
        """Initializes a Quoridor game, each player with 10 fences, pawns at (4,0) and (4,8), and player 1's turn."""
        # generate empty 3-element nested list for position arrays
        self._board = [[], [], []]

        # populate 3 position arrays with 9x9 elements, initialized to 0
        for array in range(3):
            for index in range(9):
                self._board[array].append([])
                for element in range(9):
                    self._board[array][index].append(0)

        # initialize pawn starting positions
        self._board[0][4][0] = 1
        self._board[0][4][8] = 2

        # initialize player fence counts
        self._player_one_fences = 10
        self._player_two_fences = 10

        # initialize player turn flag
        self._first_player_turn = True

    def move_pawn(self, player, destination):
        """Returns False if a player has already won, if called with the wrong player for the current turn, or if called
        with an invalid destination.  Otherwise, returns True, updates the pawn position array and player turn flag."""
        # return False if game is won or it is not player's turn
        if not self._player_may_move(player):
            return False

        # return False if move destination is illegal
        if not self._is_legal_move(player, destination):
            return False

        # update arrays with legal move, flip turn counter, return True
        self._first_player_turn = not self._first_player_turn
        self._board[0][self._position(player)[0]][self._position(player)[1]] = 0
        self._board[0][destination[0]][destination[1]] = player
        return True

    def place_fence(self, player, orientation, coords):
        """Returns False if a player has already won, if called with the wrong player for the current turn, or current
        player has no fences remaining, or if called with invalid coordinates.  Otherwise, returns True and updates the
        fence position array, player fence count, and player turn flag."""
        # return False if game is won or it is not player's turn
        if not self._player_may_move(player):
            return False

        # disallow move if player has no fences remaining
        if player == 1 and self._player_one_fences == 0:
            return False
        elif player == 2 and self._player_two_fences == 0:
            return False

        # set index for fence orientation
        if orientation == "v":
            fence_index = 1
        elif orientation == "h":
            fence_index = 2
        else:
            return False

        # return False if coordinates passed are not inside the board edges
        if fence_index == 1 and (not 1 <= coords[0] <= 8 or not 0 <= coords[1] <= 8):
            return False
        elif fence_index == 2 and (not 0 <= coords[0] <= 8 or not 1 <= coords[1] <= 8):
            return False

        # return False if fence exists in coordinates passed
        if self._board[fence_index][coords[0]][coords[1]] == 1:
            return False

        # return warning string if fair play rule is broken
        if not self._is_valid_path(player, fence_index, coords):
            return 'breaks the fair play rule'

        # update position array for legal fence placement
        # noinspection PyTypeChecker
        self._board[fence_index][coords[0]][coords[1]] = 1

        # decrement player fence count
        if player == 1:
            self._player_one_fences -= 1
        elif player == 2:
            self._player_two_fences -= 1

        # flip turn flag
        self._first_player_turn = not self._first_player_turn

        return True

    def _player_may_move(self, player):
        """Returns True if it is player's turn and the game has not been won."""
        # disallow move after game has been won
        if self.is_winner(1) or self.is_winner(2):
            return False

        # disallow move during opponent's turn
        if player == 1 and not self._first_player_turn:
            return False
        if player == 2 and self._first_player_turn:
            return False

        return True

    def _position(self, player):
        """Returns pawn position of player."""
        # iterate through board columns and rows, return player pawn position as tuple
        for column in range(9):
            if player in self._board[0][column]:
                for row in range(9):
                    if self._board[0][column][row] == player:
                        return column, row

    def _is_adjacent(self, origin, target):
        """Returns True if target square is adjacent to origin."""

        adjacent_squares = [(origin[0], origin[1] + 1), (origin[0], origin[1] - 1), (origin[0] + 1, origin[1]),
                            (origin[0] - 1, origin[1])]

        return target in adjacent_squares

    def _is_legal_move(self, player, destination):
        """Returns True if a player pawn movement to destination is a legal move, otherwise returns False."""
        # return False if destination is outside the board
        if not 0 <= destination[0] <= 8 or not 0 <= destination[1] <= 8:
            return False

        if player == 1:
            opponent = 2
        else:
            opponent = 1

        if self._is_adjacent(self._position(player), self._position(opponent)):
            # if pawns are adjacent
            if not self._is_adjacent(self._position(player), destination):
                # and destination is not adjacent to current player, check for legal jump move
                return self._is_legal_jump(player, destination)

        # otherwise return False if destination is not adjacent to current position
        if not self._is_adjacent(self._position(player), destination):
            return False

        # return False if fence, edge, or pawn blocks move
        if self._move_blocked(self._position(player), destination):
            return False

        return True

    def _move_blocked(self, origin, destination):
        """Returns True if move to adjacent destination is blocked by a pawn, fence or edge, otherwise return False."""
        if self._first_player_turn:
            opponent = 2
        else:
            opponent = 1

        # return False is destination is occupied by opponent's pawn
        if self._position(opponent) == destination:
            return True

        # if vertical move
        if origin[0] == destination[0]:
            # check for horizontal fence at origin if upward move, else check fence at coordinates below origin
            if destination[1] < origin[1]:
                if self._board[2][origin[0]][origin[1]]:
                    return True
            else:
                if self._board[2][origin[0]][origin[1] + 1]:
                    return True
        # if horizontal move
        else:
            # check for vertical fence at origin if leftward move, else check fence at coordinates to the right
            if destination[0] < origin[0]:
                if self._board[1][origin[0]][origin[1]]:
                    return True
            else:
                if self._board[1][origin[0] + 1][origin[1]]:
                    return True

        return False

    def _is_legal_jump(self, player, target):
        """Returns True if player pawn can make a valid jump move to target, otherwise returns False."""
        if self._first_player_turn:
            opponent = 2
        else:
            opponent = 1
        # assign current pawn coordinates to variables
        play_x = self._position(player)[0]
        play_y = self._position(player)[1]
        opp_x = self._position(opponent)[0]
        opp_y = self._position(opponent)[1]

        # if move is a straight vertical jump, check for horizontal fences and opponent's pawn
        if play_x == target[0] == opp_x:
            # if downward move
            if target[1] == play_y + 2 and opp_y == play_y + 1:
                if self._board[2][target[0]][target[1]] == 0 and self._board[2][target[0]][target[1] - 1] == 0:
                    return True
            # if upward move
            elif target[1] == play_y - 2 and self._position(opponent)[1] == play_y - 1:
                if self._board[2][target[0]][target[1] + 1] == 0 and self._board[2][target[0]][target[1] + 2] == 0:
                    return True

        # if straight horizontal jump, check for vertical fences and opponent's pawn
        elif play_y == target[1] == opp_y:
            # if rightward move
            if target[0] == play_x + 2 and opp_x == play_x + 1:
                if self._board[1][target[0]][target[1]] == 0 and self._board[1][target[0]][target[1] - 1] == 0:
                    return True
            # if leftward move
            elif target[0] == play_x - 2 and opp_x == play_x - 1:
                if self._board[1][target[0]][target[1] + 1] == 0 and self._board[1][target[0]][target[1] + 2] == 0:
                    return True
        # if no straight jump detected, look for diagonal jump
        else:
            return self._is_legal_diagonal(player, target)

    def _is_legal_diagonal(self, player, target):
        """returns True if player pawn can make a legal diagonal jump to target, otherwise returns False."""
        # split methods conform to method size restriction for project
        return self._is_legal_diagonal_from_column(player, target) or self._is_legal_diagonal_from_row(player, target)

    def _is_legal_diagonal_from_column(self, player, target):
        """returns True if player pawn can make a legal diagonal jump over opponent pawn on the same column, otherwise
        returns False."""
        if self._first_player_turn:
            opponent = 2
        else:
            opponent = 1

        # assign current pawn coordinates to variables
        play_x = self._position(player)[0]
        play_y = self._position(player)[1]
        opp_x = self._position(opponent)[0]
        opp_y = self._position(opponent)[1]

        # if pawns in same column
        if opp_x == play_x:
            # if opponent pawn above player pawn and horizontal fence above opponent pawn
            if opp_y == target[1] == play_y + 1 and self._board[2][opp_x][opp_y]:
                # player may jump to upper right or upper left
                if target[0] == opp_x + 1:
                    # if upper rightward jump, check for vertical fence
                    if not self._board[1][opp_x + 1][opp_y]:
                        return True
                elif target[0] == opp_x - 1:
                    # if upper leftward jump, check for vertical fence
                    if not self._board[1][opp_x][opp_y]:
                        return True

            # if opponent pawn below player pawn and horizontal fence below opponent pawn
            elif opp_y == target[1] == play_y - 1 and self._board[2][opp_x][opp_y + 1]:
                # player may jump to lower right or lower left
                if target[0] == opp_x + 1:
                    # if lower rightward jump, check for vertical fence
                    if not self._board[1][opp_x + 1][opp_y]:
                        return True
                elif target[0] == opp_x - 1:
                    # if lower leftward jump, check for vertical fence
                    if not self._board[1][opp_x][opp_y]:
                        return True

        return False

    def _is_legal_diagonal_from_row(self, player, target):
        """returns True if player pawn can make a legal diagonal jump over opponent pawn on the same row, otherwise
        returns False."""
        if self._first_player_turn:
            opponent = 2
        else:
            opponent = 1

        # assign current pawn coordinates to variables
        play_x = self._position(player)[0]
        play_y = self._position(player)[1]
        opp_x = self._position(opponent)[0]
        opp_y = self._position(opponent)[1]

        # if pawns in same row
        if opp_y == play_y:
            # if opponent pawn right of player pawn and vertical fence right of opponent pawn
            if opp_x == target[0] == play_x + 1 and self._board[1][opp_x + 1][opp_y]:
                # player may jump to upper right or lower right
                if target[1] == opp_y + 1:
                    # if upper rightward jump, check for horizontal fence
                    if not self._board[2][opp_x][opp_y]:
                        return True
                elif target[1] == opp_y - 1:
                    # if lower rightward jump, check for horizontal fence
                    if not self._board[2][opp_x][opp_y + 1]:
                        return True

            # if opponent pawn left of player pawn and vertical fence left of opponent pawn
            elif opp_x == target[0] == play_x - 1 and self._board[1][opp_x][opp_y]:
                # player may jump to upper left or lower left
                if target[1] == opp_y + 1:
                    # if upper leftward jump, check for horizontal fence
                    if not self._board[2][opp_x][opp_y]:
                        return True
                elif target[1] == opp_y - 1:
                    # if lower leftward jump, check for horizontal fence
                    if not self._board[2][opp_x][opp_y + 1]:
                        return True

        return False

    def _is_valid_path(self, player, fence_index, coords):
        """Returns True if, after placing a new fence with passed parameters, the other player has a path to the current
        player's base row, otherwise returns False."""
        if player == 1:
            opponent = 2
            win_row = 0
        else:
            opponent = 1
            win_row = 8

        # place proposed fence into the board
        # noinspection PyTypeChecker
        self._board[fence_index][coords[0]][coords[1]] = 1

        start_x = self._position(opponent)[0]
        start_y = self._position(opponent)[1]
        start = (start_x, start_y)

        # call recursive method to search for path
        result = self._rec_is_valid_path([start], win_row)

        # reset proposed fence location before returning
        # noinspection PyTypeChecker
        self._board[fence_index][coords[0]][coords[1]] = 0

        return result

    def _rec_is_valid_path(self, space_list, end_row):
        """Searches adjacent, unblocked spaces with recursion, returns True when end_row is found, False if not found"""
        # first base condition occurs when no spaces are added to space_list during the function call
        add_counter = 0
        # second base condition occurs when a space in end_row exists in space_list
        for space in space_list:
            if space[1] == end_row:
                return True

            # try to add all adjacent spaces to space_list
            up_space = (space[0], space[1] + 1)
            down_space = (space[0], space[1] - 1)
            left_space = (space[0] - 1, space[1])
            right_space = (space[0] + 1, space[1])
            new_list = [up_space, down_space, left_space, right_space]

            # test if new spaces are unblocked by fences and are inside the board edges
            for new_space in new_list:
                if 0 <= new_space[0] <= 8 and 0 <= new_space[1] <= 8:
                    if not self._move_blocked(space, new_space):
                        if new_space not in space_list:
                            space_list.append(new_space)
                            add_counter += 1

        if add_counter == 0:
            return False

        # recursive call with updated space_list if neither base condition is satisfied
        return self._rec_is_valid_path(space_list, end_row)

    def is_winner(self, player):
        """Returns True if the player passed in has won by reaching the opponent's baseline row.  Otherwise, returns
        False."""
        # check player pawn row, return True if it matches opponent's base row
        if player == 1 and self._position(player)[1] == 8:
            return True
        if player == 2 and self._position(player)[1] == 0:
            return True

        return False

    def print_board(self):
        """prints current board layout for debugging"""

        for row in range(9):

            for column in range(9):
                # print an underscore for every 1 in horizontal fence array
                if self._board[2][column][row]:
                    fence = "_"
                else:
                    fence = " "
                print(" ", fence, end=' ')
            print()

            for column in range(9):
                # print a pipe for every 1 in vertical fence array
                if self._board[1][column][row]:
                    fence = "|"
                else:
                    fence = " "
                print(fence, self._board[0][column][row], end=' ')
            print()
        print()
