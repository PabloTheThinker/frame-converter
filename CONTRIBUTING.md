# Contributing to FrameConverter

Thank you for considering contributing to FrameConverter! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:

- **Clear title** - Describe the bug in a few words
- **Description** - Explain what happened and what you expected
- **Steps to reproduce** - How can we recreate the bug?
- **System information** - OS, Python version, FFmpeg version
- **Screenshots** - If applicable, add screenshots

### Suggesting Features

We love new ideas! Please create an issue with:

- **Feature description** - What would you like to see?
- **Use case** - Why is this feature useful?
- **Mockups** - If you have design ideas, share them!

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/pablothethinker/frameconverter.git
   cd frameconverter
   ```

2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Commit your changes**
   ```bash
   git commit -m "Add: Description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Describe what you changed and why
   - Reference any related issues
   - Add screenshots if UI changes

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where appropriate
- Add docstrings to functions and classes

Example:
```python
def convert_video(input_file: str, output_file: str) -> bool:
    """
    Convert a video file from MP4 to MOV format.
    
    Args:
        input_file: Path to the input MP4 file
        output_file: Path to the output MOV file
        
    Returns:
        True if conversion succeeded, False otherwise
    """
    # Implementation here
    pass
```

### PyQt6 UI

- Use descriptive widget names (e.g., `start_button`, not `button1`)
- Keep UI logic separate from business logic
- Use signals and slots for communication
- Follow Apple HIG design principles

### Git Commits

Use clear, descriptive commit messages:

- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements to existing features
- `Remove:` for removing code/features
- `Refactor:` for code restructuring

Examples:
```
Add: GPU acceleration support for AMD cards
Fix: Progress bar not updating during conversion
Update: Improved dark mode colors for better contrast
Remove: Deprecated legacy conversion method
Refactor: Simplified FFmpeg wrapper code
```

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pablothethinker/frameconverter.git
   cd frameconverter
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python3 src/main.py
   ```

4. **Make changes and test**
   - Test on your system
   - Try both light and dark modes
   - Test with various video files
   - Check for errors in the console

## Project Structure

```
frameconverter/
├── src/
│   ├── main.py                 # Entry point
│   ├── ui/                     # UI components
│   ├── converter/              # Conversion logic
│   ├── utils/                  # Utilities
│   └── resources/              # Stylesheets, icons
├── screenshots/                # App screenshots
├── requirements.txt            # Dependencies
├── install.sh                  # Installation script
├── LICENSE                     # MIT License
└── README.md                   # Documentation
```

## Testing

Before submitting a PR:

- [ ] Test on your Linux distribution
- [ ] Verify light and dark modes work
- [ ] Check GPU acceleration (if available)
- [ ] Test with various video files
- [ ] Ensure no console errors
- [ ] Check that settings persist
- [ ] Test cancel functionality

## Questions?

If you have questions, feel free to:

- Open a GitHub issue
- Reach out on X/Twitter: [@pablothethinker](https://x.com/pablothethinker)

## Code of Conduct

Be respectful and constructive. We're all here to make FrameConverter better!

---

Thank you for contributing! 🚀
