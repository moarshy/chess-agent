# renderer.py

import chess
import chess.svg
import cairosvg
import imageio
import os
import io
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

# --- Style and Layout Constants ---
BOARD_SIZE = 400
# Increased header height to fit more information
HEADER_HEIGHT = 85
FOOTER_HEIGHT = 40
CANVAS_WIDTH = BOARD_SIZE
CANVAS_HEIGHT = BOARD_SIZE + HEADER_HEIGHT + FOOTER_HEIGHT
BACKGROUND_COLOR = "#2c2f33"
TEXT_COLOR = "#ffffff"
TEXT_COLOR_SUBTLE = "#bbbbbb" # A lighter grey for secondary info

def _find_font(size: int) -> ImageFont.FreeTypeFont | None:
    """Tries to find a common system font and returns a Pillow font object."""
    font_paths = [
        '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        'C:/Windows/Fonts/arial.ttf',  # Windows
        'Arial.ttf' # Fallback
    ]
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if not font_path:
        print("⚠️ Warning: Could not find a system font. Text will not be rendered.")
        return None
    
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"⚠️ Warning: Could not load font at {font_path}. Text will not be rendered.")
        return None

def create_game_animation(
    move_history: list[str],
    white_player_name: str,
    black_player_name: str,
    white_final_illegal: int,
    black_final_illegal: int,
    white_total_time: float,
    black_total_time: float,
    output_filename: str = "chess_game.gif",
    fps: int = 2
):
    """Renders a game from a move history into an annotated animated GIF."""
    temp_dir = "temp_render"
    os.makedirs(temp_dir, exist_ok=True)

    image_paths = []
    board = chess.Board()

    # --- Load Fonts ---
    font_player = _find_font(18)
    font_stats = _find_font(14) # Smaller font for stats
    font_info = _find_font(16)
    if not font_player or not font_info or not font_stats:
        return # Abort if fonts can't be loaded

    print("Generating frames for animation...")
    
    # --- Create a frame for each move in the history ---
    for i in tqdm(range(len(move_history) + 1), desc="Rendering Moves"):
        canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
        
        last_move = board.peek() if i > 0 else None
        board_svg = chess.svg.board(board=board, lastmove=last_move, size=BOARD_SIZE)
        board_png_data = cairosvg.svg2png(bytestring=board_svg)
        board_image = Image.open(io.BytesIO(board_png_data))

        canvas.paste(board_image, (0, HEADER_HEIGHT))

        # --- Draw Text Information on the Canvas ---
        draw = ImageDraw.Draw(canvas)
        padding = 10
        y_pos = padding

        # --- Header Section ---
        # White Player Info
        draw.text((padding, y_pos), f"White: {white_player_name}", font=font_player, fill=TEXT_COLOR)
        y_pos += 22
        white_stats_text = f"Time: {white_total_time:.2f}s | Illegal Moves: {white_final_illegal}"
        draw.text((padding, y_pos), white_stats_text, font=font_stats, fill=TEXT_COLOR_SUBTLE)
        y_pos += 20

        # Black Player Info
        draw.text((padding, y_pos), f"Black: {black_player_name}", font=font_player, fill=TEXT_COLOR)
        y_pos += 22
        black_stats_text = f"Time: {black_total_time:.2f}s | Illegal Moves: {black_final_illegal}"
        draw.text((padding, y_pos), black_stats_text, font=font_stats, fill=TEXT_COLOR_SUBTLE)

        # --- Footer Section ---
        move_num_str = f"Move: {(i // 2) + 1 if i > 0 else 1}"
        player_turn = "White" if board.turn == chess.WHITE else "Black"
        status_str = f"{move_num_str} | Turn: {player_turn}"
        draw.text((padding, HEADER_HEIGHT + BOARD_SIZE + padding), status_str, font=font_info, fill=TEXT_COLOR)

        frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
        canvas.save(frame_path)
        image_paths.append(frame_path)

        if i < len(move_history):
            board.push_san(move_history[i])

    # Create the GIF
    print("Stitching frames into a GIF...")
    with imageio.get_writer(output_filename, mode='I', fps=fps) as writer:
        for path in tqdm(image_paths, desc="Creating GIF"):
            writer.append_data(imageio.imread(path))
    
    # Clean up temporary files
    print("Cleaning up temporary files...")
    for path in image_paths:
        os.remove(path)
    os.rmdir(temp_dir)

    print(f"✅ Animation successfully saved to {output_filename}")