# Playing chess through Monte Carlo tree search (MCTS).
This is an implementation of the Monte Carlo tree search algorithm, together with (a so-far slightly simplified version of) the game chess.

Through Monte Carlo tree search, an AI learns the game by playing matches against itself. More specifically, starting from a current game situation, a game tree of possible subsequent situations (states) is built. Each node in the tree holds statistics about the current game situation, which determine the value of the action that led to it.

## Jupyter Notebooks
[Monte Carlo tree search playing chess](MCTS.ipynb)

[Chess Implementation](Chess.ipynb)

## Monte Carlo Tree Search
MCTS consists of the following steps:
1. **Selection.** A leaf <img src="https://render.githubusercontent.com/render/math?math=L"> in the game tree is selected by some criterion. The criterion used is the *upper confidence bound applied to trees* (UCT).
2. **Expansion.** Starting from <img src="https://render.githubusercontent.com/render/math?math=L">. the game tree is expanded (i.e., child nodes with subsequent game states are added). A random child node <img src="https://render.githubusercontent.com/render/math?math=C"> is selected.
3. **Simulation (Rollout).** Starting from <img src="https://render.githubusercontent.com/render/math?math=C">, a full match of the game is simulated.
4. **Backpropagation.** The winner of the simulation is backpropagated up the tree. The statistics for each node in the path upwards until the root node are updated.

The simulation here is done (as is common) through random actions. However, other methods are possible, e.g., guiding the AI through heuristics, using reinforcement learning or determining some value function which rates a state (e.g., based on statistics from chess match data sets). Hence, instead of determining the winner of a simulation, some other *score* or *value* for a game situation <img src="https://render.githubusercontent.com/render/math?math=C"> can be backpropagated.


## Further steps
### AI Performance
- Use something different from random simulations.
  - Heuristics for beating opponent's pieces.
  - Calculating some value for a game situation based on values for pieces.
  
### Performance (speed)
- "Generate" possible moves of each chess piece instead of checking for each field and piece whether a move is possible.
- The logic for this already is in *is_space_free*.
### Game Logic
- Disallow moves after which the own king is under attack. Currently the game is won through taking the enemy king instead of through checkmate.
- Castling.
- En passant.
- Retrieving a new piece.
