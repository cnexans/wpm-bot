# WPM Bot 🤖⌨️

An automated bot that plays the typing game at [wpm.silver.dev](https://wpm.silver.dev).

## What it does

1. Opens the WPM typing game website
2. Types "start" to begin the game
3. Types "python" to select the Python language
4. Captures the code snippet displayed on screen
5. Automatically types the code at superhuman speed

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with default typing speed (very fast)
python wpm_bot.py

# Run with custom typing speed (seconds per character)
python wpm_bot.py 0.05   # Slower, more human-like
python wpm_bot.py 0.01   # Super fast
```

## Requirements

- Python 3.7+
- Chrome browser installed
- Internet connection

## How it works

The bot uses Selenium to control Chrome browser:
- Navigates to the game website
- Simulates keyboard input to start the game
- Extracts the code snippet from the DOM
- Types each character with configurable delays

## Typing Speed

The `typing_speed` parameter controls delay between keystrokes:
- `0.01` = ~100 characters/second (superhuman)
- `0.05` = ~20 characters/second (fast human)
- `0.1` = ~10 characters/second (average human)

## Notes

- The browser window must stay focused during typing
- First run may take longer as it downloads ChromeDriver
- Press Ctrl+C to stop the bot at any time
- **WebGL Support**: The game requires WebGL. Headless mode is disabled by default as it may cause WebGL issues
- The bot uses `undetected-chromedriver` by default to avoid detection

