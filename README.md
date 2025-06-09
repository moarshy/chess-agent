# 🏆 LLM Chess Arena

A sophisticated chess game system that allows Large Language Models (LLMs) to compete against each other, featuring enhanced visual animations and comprehensive game analytics.

![Chess Animation Preview](https://img.shields.io/badge/Chess-Animation-blue?style=for-the-badge&logo=chess&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![LLM Support](https://img.shields.io/badge/LLM-Multi--Model-green?style=for-the-badge&logo=openai&logoColor=white)

## 🎯 Features

### 🤖 Multi-LLM Support
- **Universal LLM Integration**: Support for GPT-4, Claude, and other models via LiteLLM
- **Intelligent Move Parsing**: Advanced regex-based move extraction from LLM responses
- **Error Recovery**: Automatic retry system with contextual feedback for illegal moves
- **Fallback Strategies**: Configurable behavior when LLMs fail (abort or random move)

### 🎬 Enhanced Visual Animations
- **High-Quality Rendering**: 500px board size with smooth animations
- **Professional UI**: Modern design with gradient backgrounds and rounded elements
- **Rich Information Display**: 
  - Player statistics and illegal move tracking
  - Real-time game state indicators
  - Captured pieces visualization
  - Check/checkmate alerts
- **Responsive Layout**: Side panel with comprehensive game information
- **Multiple Font Support**: Cross-platform font detection (macOS, Linux, Windows)

### 📊 Comprehensive Analytics
- **Performance Metrics**: Thinking time tracking per player
- **Move Quality Analysis**: Illegal move counting and statistics
- **Material Advantage**: Real-time piece value calculations
- **Game History**: Complete move history with SAN notation

### ⚙️ Flexible Configuration
- **Player Types**: LLM players and human players
- **Model Selection**: Easy switching between different AI models
- **Animation Settings**: Customizable FPS and output formats
- **Game Parameters**: Configurable retry limits and failure strategies

## 🚀 Quick Start

### Prerequisites

#### Using pip:
```bash
# Install required packages
pip install chess python-chess litellm cairosvg imageio[ffmpeg] pillow tqdm python-dotenv
```

#### Using conda (recommended for Cairo dependencies):
```bash
# Install Cairo and cairosvg via conda-forge (recommended)
conda install -c conda-forge cairo cairosvg

# Then install remaining packages via pip
pip install chess python-chess litellm imageio[ffmpeg] pillow tqdm python-dotenv
```

### Environment Setup

Create a `.env` file in the project root:

```env
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Add other API keys as needed
```

### Basic Usage

```python
from chess_agent.game import Game
from chess_agent.players import LLMPlayer

# Create two LLM players
white_player = LLMPlayer(model_name="gpt-4")
black_player = LLMPlayer(model_name="anthropic/claude-3-sonnet-20240229")

# Start the game
game = Game(white_player=white_player, black_player=black_player)
game.run()
```

## 🎮 Running a Game

### Simple LLM vs LLM Match

```bash
cd chess_agent
python main.py
```

### Custom Configuration

```python
from chess_agent.game import Game
from chess_agent.players import LLMPlayer, HumanPlayer

# Configure players with custom settings
gpt_player = LLMPlayer(
    model_name="gpt-4-turbo",
    max_retries=5,
    on_failure='random'  # or 'abort'
)

claude_player = LLMPlayer(
    model_name="anthropic/claude-3-opus-20240229",
    render_board=True,
    max_retries=3
)

# Mix LLM and human players
human_player = HumanPlayer()

game = Game(white_player=gpt_player, black_player=human_player)
game.run()
```

## 🎨 Animation Features

The enhanced animation system creates professional-quality chess game recordings:

### Visual Elements
- **Board Rendering**: High-resolution chess board with coordinate labels
- **Move Highlighting**: Last move visualization with colored squares
- **Player Information**: Detailed player cards with statistics
- **Game State**: Real-time indicators for check, captures, and game status
- **Professional Styling**: Modern UI with consistent color scheme

### Output Formats
- **Animated GIF**: Optimized with subrectangle compression
- **Custom Timing**: Adjustable frame rate (default: 1.5 FPS for readability)
- **Multiple Endings**: Extended final frame display for game results

### File Naming
Games are automatically saved with timestamps:
```
game_20240101-143022.gif
```

## 🔧 Configuration Options

### LLMPlayer Parameters

```python
LLMPlayer(
    model_name="gpt-4",           # Model identifier
    render_board=True,            # Include ASCII board in prompts
    max_retries=3,                # Maximum retry attempts for illegal moves
    on_failure='abort'            # Strategy when retries exhausted ('abort' or 'random')
)
```

### Supported Models

The system supports any model available through LiteLLM:

- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-opus-20240229`, `anthropic/claude-3-sonnet-20240229`
- **Local Models**: Any model supported by LiteLLM
- **Custom Endpoints**: Configurable API endpoints

### Animation Customization

```python
create_game_animation(
    move_history,
    white_player_name,
    black_player_name,
    white_illegal_moves,
    black_illegal_moves,
    white_total_time,
    black_total_time,
    output_filename="custom_game.gif",
    fps=2.0  # Adjust playback speed
)
```

## 📁 Project Structure

```
chess-agent/
├── chess_agent/
│   ├── __init__.py
│   ├── game.py          # Core game logic and statistics
│   ├── players.py       # Player implementations (LLM, Human)
│   ├── llm.py          # LLM communication interface
│   ├── renderer.py     # Enhanced animation system
│   └── main.py         # Entry point and configuration
├── .env                # API keys and configuration
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🎯 Example Games

### GPT-4 vs Claude-3

```python
from chess_agent.game import Game
from chess_agent.players import LLMPlayer

gpt4 = LLMPlayer("gpt-4")
claude3 = LLMPlayer("anthropic/claude-3-sonnet-20240229")

game = Game(white_player=gpt4, black_player=claude3)
game.run()
```

### Tournament Setup

```python
models = [
    "gpt-4",
    "gpt-4-turbo", 
    "anthropic/claude-3-opus-20240229",
    "anthropic/claude-3-sonnet-20240229"
]

for i, white_model in enumerate(models):
    for j, black_model in enumerate(models):
        if i != j:
            white = LLMPlayer(white_model)
            black = LLMPlayer(black_model)
            
            print(f"\n🏁 {white_model} vs {black_model}")
            game = Game(white_player=white, black_player=black)
            game.run()
```

## 🛠️ Advanced Features

### Custom Prompting
Modify the system prompts in `players.py` to experiment with different playing styles:

```python
SYSTEM_PROMPT = """You are a grandmaster chess player. 
Analyze positions deeply and play aggressively..."""
```

### Performance Monitoring
The system tracks comprehensive statistics:
- Total thinking time per player
- Number of illegal moves attempted
- Material advantage tracking
- Move-by-move timing analysis

### Error Handling
Robust error handling for:
- API failures and rate limits
- Invalid move formats
- Network connectivity issues
- Font rendering problems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for public methods
- Test with multiple LLM providers
- Ensure cross-platform compatibility

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Dependencies

- **chess**: Chess game logic and move validation
- **litellm**: Universal LLM API interface
- **cairosvg**: SVG to PNG conversion for board rendering
- **imageio**: GIF creation and optimization
- **Pillow**: Image processing and text rendering
- **tqdm**: Progress bars for animation generation
- **python-dotenv**: Environment variable management

## 🚨 Troubleshooting

### Common Issues

**Font Rendering Problems**
```bash
# macOS: Install system fonts
# Linux: sudo apt-get install fonts-dejavu
# Windows: Fonts should be available by default
```

**API Key Errors**
```bash
# Verify your .env file contains valid API keys
# Check API key permissions and billing status
```

**Animation Failures**

For **conda users** (recommended):
```bash
# Install Cairo and cairosvg via conda-forge
conda install -c conda-forge cairo cairosvg
```

For **pip users**:
```bash
# Ensure Cairo is properly installed first
pip install cairosvg

# Platform-specific Cairo installation:
# macOS: brew install cairo
# Ubuntu/Debian: sudo apt-get install libcairo2-dev
# CentOS/RHEL: sudo yum install cairo-devel
```

### Performance Tips
- Use smaller board sizes for faster rendering
- Reduce FPS for smaller file sizes
- Enable subrectangle compression for GIF optimization

## 🎉 Acknowledgments

- Built with the excellent [python-chess](https://github.com/niklasf/python-chess) library
- Powered by [LiteLLM](https://github.com/BerriAI/litellm) for universal LLM support
- Enhanced visual rendering with Cairo and Pillow

---

**Happy Chess Playing! 🎯♟️**
