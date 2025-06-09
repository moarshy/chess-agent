# players.py

import chess
import re
import random
from llm import get_llm_completion

class Player:
    """Base class for all player types."""
    def get_move(self, board: chess.Board, move_history: list[str]) -> tuple[str | None, int]:
        """
        Given the current board state, return a valid move and the number of
        illegal attempts made during the turn.
        
        Returns:
            A tuple containing (valid_move, num_illegal_attempts).
        """
        raise NotImplementedError

class LLMPlayer(Player):
    """A player controlled by a Large Language Model with advanced error handling."""
    SYSTEM_PROMPT = """You are a specialized chess move execution engine. Your output is parsed directly by a computer program. It is critical that you follow the output format precisely. Any deviation will result in a system error.

**Instructions:**
1.  Analyze the position provided in the user prompt (FEN, history, etc.).
2.  Determine the single best move.
3.  Your response MUST BE ONLY the move in Standard Algebraic Notation (SAN).

**Output Format Rules:**
- DO NOT include any explanations, commentary, or conversational text (e.g., "The best move is...").
- DO NOT use markdown, code blocks, or quotation marks.
- Your response must be a single, plain text string representing the move.

**Examples of CORRECT output:**
e4
Nf3
Bxg7
O-O
a8=Q

**Examples of INCORRECT output:**
The best move is e4.
"Nf3"
`Bxg7`
"""

    def __init__(self, model_name: str, render_board: bool = True, max_retries: int = 3, on_failure: str = 'abort'):
        """
        Initializes the LLM Player.
        Args:
            model_name: The name of the model to use (e.g., 'gpt-4o').
            render_board: Flag to include ASCII board in the prompt.
            max_retries: The maximum number of times to retry after an illegal move.
            on_failure: Strategy if max_retries is reached. 'abort' or 'random'.
        """
        self.model = model_name
        self.render_board = render_board
        self.max_retries = max_retries
        self.on_failure = on_failure
        print(f"🤖 Initialized LLMPlayer with model: {self.model} (Max Retries: {self.max_retries}, On Failure: {self.on_failure})")

    def _create_initial_user_prompt(self, board: chess.Board, history: list[str]) -> str:
        """Creates the dynamic part of the prompt with turn-specific data."""
        player_color = "White" if board.turn == chess.WHITE else "Black"
        user_prompt = f"You are playing as {player_color}.\n\n"
        user_prompt += f"Current board state (FEN):\n{board.fen()}\n\n"
        user_prompt += f"Move history:\n{' '.join(history) if history else 'No moves yet.'}\n\n"
        if self.render_board:
            user_prompt += f"ASCII Board:\n{str(board)}\n"
        return user_prompt

    def _extract_san_from_response(self, text: str) -> str | None:
        """Uses regex to find a chess move in SAN format from the LLM's response."""
        # This regex looks for standard chess moves, including castling and promotions.
        san_pattern = r'\b([NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O-O|O-O)\b'
        match = re.search(san_pattern, text)
        if match:
            return match.group(0)
        return None

    def get_move(self, board: chess.Board, move_history: list[str]) -> tuple[str | None, int]:
        """
        Manages the conversation with the LLM to get a valid move, with retries.
        """
        turn_messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": self._create_initial_user_prompt(board, move_history)}
        ]
        
        illegal_attempts = 0
        for attempt in range(self.max_retries):
            assistant_response = get_llm_completion(turn_messages, self.model)
            if assistant_response is None:
                return None, illegal_attempts

            # Attempt to extract a clean move from a potentially messy response
            extracted_move = self._extract_san_from_response(assistant_response)
            move_to_try = extracted_move if extracted_move else assistant_response.strip()

            turn_messages.append({"role": "assistant", "content": assistant_response})

            board_copy = board.copy()
            try:
                board_copy.push_san(move_to_try)
                # If successful, the move is valid
                return move_to_try, illegal_attempts
            except ValueError:
                illegal_attempts += 1
                print(f"🔴 LLM provided an illegal move: '{move_to_try}'. Retrying (Attempt {attempt + 1}/{self.max_retries})...")
                
                # Create a more detailed, corrective prompt for the next attempt
                legal_moves = [board.san(m) for m in board.legal_moves]
                error_feedback = f"""Your previous move '{move_to_try}' was illegal. 
The current board state is FEN: {board.fen()}.
You must adhere to the output format rules and provide a move from the following list of legal moves: {legal_moves}"""
                turn_messages.append({"role": "user", "content": error_feedback})
        
        # If the loop finishes, max_retries was reached
        print(f"🔴 LLM failed to provide a valid move after {self.max_retries} attempts.")
        if self.on_failure == 'random':
            random_move = random.choice([board.san(m) for m in board.legal_moves])
            print(f"Falling back to random move: {random_move}")
            return random_move, illegal_attempts
        else: # 'abort' is the default
            return None, illegal_attempts

class HumanPlayer(Player):
    """A player controlled by a human via the console."""
    def get_move(self, board: chess.Board, move_history: list[str]) -> tuple[str | None, int]:
        illegal_attempts = 0
        while True:
            legal_moves_str = [board.san(m) for m in board.legal_moves]
            print("\nYour turn. Legal moves:", legal_moves_str)
            move = input("Enter your move in SAN: ")
            if move in legal_moves_str:
                return move, illegal_attempts
            else:
                illegal_attempts += 1
                print(f"🔴 Illegal move '{move}'. Please try again.")