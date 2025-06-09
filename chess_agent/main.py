# main.py

from game import Game
from players import LLMPlayer
from dotenv import load_dotenv

load_dotenv()

def main():
    """Configures and runs a single chess game."""
    print("👑 Welcome to the LLM Chess Arena! 👑")

    # --- Configure your players here ---

    # To have two LLMs compete:
    gpt_player = LLMPlayer(model_name="gpt-4.1")
    # anthropic_player = LLMPlayer(model_name="anthropic/claude-sonnet-4-20250514")
    gemini_player = LLMPlayer(model_name="gemini/gemini-2.0-flash")

    # --- Start the game ---
    game = Game(white_player=gemini_player, black_player=gpt_player)
    game.run()

if __name__ == "__main__":
    main()