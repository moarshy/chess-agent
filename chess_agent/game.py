# game.py

import chess
import time
from players import Player
from renderer import create_game_animation

class Game:
    """Manages a single chess game between two players, with stats tracking."""
    
    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    def __init__(self, white_player: Player, black_player: Player):
        self.board = chess.Board()
        self.move_history = []
        self.players = {chess.WHITE: white_player, chess.BLACK: black_player}
        
        self.stats = {
            'illegal_moves': {chess.WHITE: 0, chess.BLACK: 0},
            'total_time': {chess.WHITE: 0.0, chess.BLACK: 0.0}
        }

    def _calculate_material_advantage(self) -> tuple[int, int]:
        white_material = sum(self.PIECE_VALUES[piece.piece_type] for piece in self.board.piece_map().values() if piece.color == chess.WHITE)
        black_material = sum(self.PIECE_VALUES[piece.piece_type] for piece in self.board.piece_map().values() if piece.color == chess.BLACK)
        return white_material, black_material
        
    def _display_turn_header(self, player_color_str: str):
        move_num = self.board.fullmove_number
        
        print("\n" + "="*40)
        print(f"  Move: {move_num}   |   Player: {player_color_str}")
        print("="*40)
        
        print(self.board)
        print(f"FEN: {self.board.fen()}")

        white_mat, black_mat = self._calculate_material_advantage()
        print(f"Material: White ({white_mat}) - Black ({black_mat})")
        
    def _display_turn_stats(self, move_time: float, player_color_str: str, player_color_code: bool):
        total_time = self.stats['total_time'][player_color_code]
        illegal_moves = self.stats['illegal_moves'][player_color_code]
        
        print(f"Time for this move: {move_time:.2f} seconds")
        print(f"Total thinking time for {player_color_str}: {total_time:.2f} seconds")
        print(f"Total illegal moves for {player_color_str}: {illegal_moves}")

    def run(self):
        """Starts and runs the game loop until the game is over."""
        while not self.board.is_game_over(claim_draw=True):
            player_color_code = self.board.turn
            player_color = "White" if player_color_code == chess.WHITE else "Black"
            current_player = self.players[player_color_code]
            
            self._display_turn_header(player_color)
            
            start_time = time.time()
            move, illegal_attempts = current_player.get_move(self.board, self.move_history)
            end_time = time.time()
            
            move_time = end_time - start_time
            self.stats['illegal_moves'][player_color_code] += illegal_attempts
            self.stats['total_time'][player_color_code] += move_time

            if move:
                self.board.push_san(move)
                self.move_history.append(move)
                print(f"\n{player_color} plays: {move}")
                self._display_turn_stats(move_time, player_color, player_color_code)
            else:
                print(f"\n🔴 {player_color} ({type(current_player).__name__}) failed to provide a valid move. Game aborted.")
                return

        self._display_final_summary()

    def _display_final_summary(self):
        """Displays the final game summary and renders the animation."""
        print("\n" + "#"*40)
        print(" " * 14 + "GAME OVER")
        print("#"*40)
        
        print(f"\nResult: {self.board.result(claim_draw=True)}")
        print("Final Board:")
        print(self.board)

        print("\n--- Final Statistics ---")
        for color_code, color_name in [(chess.WHITE, "White"), (chess.BLACK, "Black")]:
            player = self.players[color_code]
            player_name = type(player).__name__
            model_name = getattr(player, 'model', '')
            full_name = f"{player_name} {model_name}".strip()
            total_time = self.stats['total_time'][color_code]
            illegal_moves = self.stats['illegal_moves'][color_code]

            print(f"\nPlayer {color_name} ({full_name}):")
            print(f"  Total thinking time: {total_time:.2f} seconds")
            print(f"  Total illegal moves: {illegal_moves}")
            
        print("\n🎥 Rendering game animation...")
        try:
            white_player = self.players[chess.WHITE]
            black_player = self.players[chess.BLACK]
            white_name = f"{type(white_player).__name__} {getattr(white_player, 'model', '')}".strip()
            black_name = f"{type(black_player).__name__} {getattr(black_player, 'model', '')}".strip()

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"game_{timestamp}.gif"

            # --- UPDATED FUNCTION CALL ---
            create_game_animation(
                self.move_history,
                white_name,
                black_name,
                self.stats['illegal_moves'][chess.WHITE],
                self.stats['illegal_moves'][chess.BLACK],
                self.stats['total_time'][chess.WHITE],
                self.stats['total_time'][chess.BLACK],
                filename,
                fps=2
            )
        except Exception as e:
            print(f"🔴 Could not render animation: {e}")