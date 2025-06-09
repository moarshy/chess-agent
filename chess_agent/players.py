# players.py

import chess
import chess.svg
import re
import random
import io
import cairosvg
from llm import get_llm_completion, encode_image_to_base64, create_multimodal_content, check_vision_support

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
    SYSTEM_PROMPT_TEXT = """You are a specialized chess move execution engine. Your output is parsed directly by a computer program. It is critical that you follow the output format precisely. Any deviation will result in a system error.

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

    SYSTEM_PROMPT_IMAGE = """You are a specialized chess move execution engine. Your output is parsed directly by a computer program. It is critical that you follow the output format precisely. Any deviation will result in a system error.

**Instructions:**
1.  Analyze the chess board position shown in the image provided.
2.  Consider the game context (FEN, move history) provided in the text.
3.  Determine the single best move for your color.
4.  Your response MUST BE ONLY the move in Standard Algebraic Notation (SAN).

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

    def __init__(self, model_name: str, input_type: str = 'ascii', max_retries: int = 3, on_failure: str = 'abort'):
        """
        Initializes the LLM Player.
        Args:
            model_name: The name of the model to use (e.g., 'gpt-4o', 'gpt-4-vision-preview').
            input_type: Type of board input - 'ascii' for text board or 'image' for rendered PNG.
            max_retries: The maximum number of times to retry after an illegal move.
            on_failure: Strategy if max_retries is reached. 'abort' or 'random'.
        """
        self.model = model_name
        self.input_type = input_type.lower()
        self.max_retries = max_retries
        self.on_failure = on_failure
        
        if self.input_type not in ['ascii', 'image']:
            raise ValueError("input_type must be 'ascii' or 'image'")
        
        # Validate vision support for image input
        if self.input_type == 'image':
            if not check_vision_support(self.model):
                print(f"⚠️ Warning: {self.model} may not support vision capabilities.")
                print("   Consider using a vision-capable model like gpt-4o, gpt-4-vision-preview, or claude-3-opus")
                print("   The player will attempt to use image input anyway, but may fall back to ASCII.")
        
        input_type_display = "🖼️ Image" if self.input_type == 'image' else "📝 ASCII"
        print(f"🤖 Initialized LLMPlayer with model: {self.model}")
        print(f"   📊 Input Type: {input_type_display}")
        print(f"   🔄 Max Retries: {self.max_retries}, On Failure: {self.on_failure}")

    def _render_board_as_image(self, board: chess.Board, last_move: chess.Move = None) -> bytes:
        """
        Renders the current board state as a PNG image.
        
        Args:
            board: Current chess board state
            last_move: Optional last move to highlight
            
        Returns:
            PNG image as bytes
        """
        try:
            # Generate SVG of the current board state
            svg_data = chess.svg.board(
                board=board,
                lastmove=last_move,
                size=400,
                coordinates=True
            )
            
            # Convert SVG to PNG bytes
            png_bytes = cairosvg.svg2png(bytestring=svg_data)
            return png_bytes
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to render board image: {e}")
            print("   Falling back to ASCII representation")
            return None

    def _create_initial_user_prompt(self, board: chess.Board, history: list[str]) -> dict:
        """Creates the initial user message with board state (text or image)."""
        player_color = "White" if board.turn == chess.WHITE else "Black"
        
        # Create text content
        text_content = f"You are playing as {player_color}.\n\n"
        text_content += f"Current board state (FEN):\n{board.fen()}\n\n"
        text_content += f"Move history:\n{' '.join(history) if history else 'No moves yet.'}\n\n"
        
        if self.input_type == 'image':
            # Try to render board as image
            last_move = board.peek() if len(history) > 0 else None
            image_bytes = self._render_board_as_image(board, last_move)
            
            if image_bytes:
                # Encode image to base64
                image_base64 = encode_image_to_base64(image_bytes, "PNG")
                text_content += "Please analyze the board position shown in the image."
                
                # Create multimodal content using correct LiteLLM format
                multimodal_content = create_multimodal_content(text_content, image_base64)
                
                return {
                    "role": "user",
                    "content": multimodal_content
                }
            else:
                # Fallback to ASCII if image rendering fails
                text_content += f"ASCII Board:\n{str(board)}\n"
                print("🔄 Falling back to ASCII board representation")
        else:
            # ASCII representation
            text_content += f"ASCII Board:\n{str(board)}\n"
        
        return {
            "role": "user", 
            "content": text_content
        }

    def _create_retry_prompt(self, board: chess.Board, illegal_move: str) -> dict:
        """Creates a retry prompt after an illegal move."""
        legal_moves = [board.san(m) for m in board.legal_moves]
        text_content = f"""Your previous move '{illegal_move}' was illegal. 
The current board state is FEN: {board.fen()}.
You must adhere to the output format rules and provide a move from the following list of legal moves: {legal_moves}"""
        
        if self.input_type == 'image':
            # Include updated board image for retry
            image_bytes = self._render_board_as_image(board)
            if image_bytes:
                image_base64 = encode_image_to_base64(image_bytes, "PNG")
                text_content += "\n\nPlease refer to the updated board image."
                
                # Create multimodal content using correct LiteLLM format
                multimodal_content = create_multimodal_content(text_content, image_base64)
                
                return {
                    "role": "user",
                    "content": multimodal_content
                }
        
        return {
            "role": "user",
            "content": text_content
        }

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
        # Choose system prompt based on input type
        system_prompt = self.SYSTEM_PROMPT_IMAGE if self.input_type == 'image' else self.SYSTEM_PROMPT_TEXT
        
        turn_messages = [
            {"role": "system", "content": system_prompt},
            self._create_initial_user_prompt(board, move_history)
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
                
                # Create retry prompt with updated board state
                retry_message = self._create_retry_prompt(board, move_to_try)
                turn_messages.append(retry_message)
        
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