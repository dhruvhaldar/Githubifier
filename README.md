# Githubifier

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/github/license/dhruvhaldar/Githubifier)
![Issues](https://img.shields.io/github/issues/dhruvhaldar/Githubifier)
![PRs](https://img.shields.io/github/issues-pr/dhruvhaldar/Githubifier)

**Githubifier** is a robust Python utility designed to solve the problem of uploading large directories (like CFD cases, datasets, or heavy repos) to GitHub or cloud storage. It compresses a source folder into a multi-part 7-Zip archive, ensuring each part stays within file size limits (e.g., GitHub's 100MB max).

## Key Features

- **Automated Splitting**: Splits large archives into chunks (default 40MB) compatible with GitHub.
- **Safety First**:
    - **Dry Run Mode**: Preview what will happen without writing any files.
    - **Disk Space Checks**: Warns if the destination drive is running low on space.
    - **Read-Only**: Verify source is readable before starting.
- **Integrity Verification**: Automatically verifies the created archive after compression to ensure no data corruption.
- **Clean Fallback**: Automatically cleans up partial files if the process is interrupted or fails.
- **Cross-Platform**: Designed for Windows but compatible with Linux/macOS (requires `7z` or `7za` in PATH).

## Prerequisites
- **Python 3.6+**
- **7-Zip** installed and available in your system PATH or default Install location.
    - *Windows Default Paths Checked:* `C:\Program Files\7-Zip\7z.exe`, `C:\Program Files (x86)\7-Zip\7z.exe`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dhruvhaldar/Githubifier.git
cd Githubifier
```

### 2. Set Up a Virtual Environment (Recommended)
Using a virtual environment keeps your dependencies isolated and your system clean.

**On Windows:**
```powershell
# Create the virtual environment (only do this once)
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
# Note: You may need to run 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser' if you get a permission error.

# Alternatively, using CMD:
# venv\Scripts\activate.bat
```

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

*You know you are in the virtual environment when you see `(venv)` at the start of your command prompt.*

### 3. Install Requirements
This script uses standard Python libraries. However, if you are setting up a development environment:
```bash
pip install -r requirements.txt
# This ensures consistency, though currently there are no external Python dependencies.
```

## Usage

Basic command syntax:
```bash
python githubifier.py [SOURCE_DIR] [DESTINATION_DIR] [OPTIONS]
```

### Examples

**1. Compress a folder with default settings (40MB split):**
```bash
python githubifier.py "C:\MyLargeDataset" "D:\Backups"
```

**2. Preview the operation (Dry Run):**
```bash
python githubifier.py "C:\MyLargeDataset" "D:\Backups" --dry-run
```

**3. Customize split size (e.g., 95MB for GitHub):**
```bash
python githubifier.py "C:\MyLargeDataset" "D:\Backups" --split 95m
```

**4. Use a large split size for local backup:**
```bash
python githubifier.py "C:\MyLargeDataset" "D:\Backups" --split 2g
```

## Troubleshooting

- **"7-Zip executable not found"**:
    - Ensure 7-Zip is installed.
    - Add the directory containing `7z.exe` to your system's PATH environment variable.
- **"Permission denied"**:
    - Run your terminal as Administrator if you are writing to a protected folder (like C:\Program Files).
- **Execution Policy Error (PowerShell)**:
    - If `.\venv\Scripts\Activate.ps1` fails, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Pro Tip: Using runner.py
If typing long paths in the command line is tedious, execute:
```bash
python runner.py
```
Edit `runner.py` to set your `SOURCE_DIR` and `DEST_DIR` once, and run it easily!

## License
[MIT License](LICENSE). Feel free to use and modify!
