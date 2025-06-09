# main.py

from game import Game
from players import LLMPlayer
from dotenv import load_dotenv

load_dotenv()

def main():
    """Configures and runs a single chess game."""
    print("👑 Welcome to the LLM Chess Arena! 👑")
    print("🎯 Now with enhanced visual input support!")

    # --- Configure your players here ---
    
    # Example 1: ASCII vs Image input comparison
    print("\n🔬 Demonstrating different input types:")
    
    # Player with ASCII board representation (traditional)
    gpt_ascii = LLMPlayer(
        model_name="gpt-4o", 
        input_type="ascii",
        max_retries=3
    )
    
    # Player with visual board representation (new!)
    # Note: Use vision-capable models like gpt-4-vision-preview, gpt-4o, claude-3-opus, etc.
    gpt_vision = LLMPlayer(
        model_name="gpt-4o", 
        input_type="image",
        max_retries=3
    )
    
    # Example configurations:
    
    # Traditional text-only game
    # game = Game(white_player=gpt_ascii, black_player=claude_ascii)
    
    # Mixed input types (ASCII vs Image)
    game = Game(white_player=gpt_vision, black_player=gpt_ascii)
    
    # Both players using visual input
    # gpt_vision = LLMPlayer(model_name="gpt-4o", input_type="image")
    # game = Game(white_player=gpt_vision, black_player=claude_vision)
    
    # Other vision model examples:
    # claude_opus_vision = LLMPlayer(model_name="anthropic/claude-3-opus-20240229", input_type="image")
    # gemini_vision = LLMPlayer(model_name="gemini/gemini-1.5-pro", input_type="image")
    
    print("\n🚀 Starting game with mixed input types:")
    print(f"   White: {gpt_vision.model} (🖼️ Image input)")
    print(f"   Black: {gpt_ascii.model} (📝 ASCII input)")
    
    # --- Start the game ---
    game.run()

if __name__ == "__main__":
    main()