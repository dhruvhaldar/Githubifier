# Githubifier

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/github/license/dhruvhaldar/Githubifier)
![Issues](https://img.shields.io/github/issues/dhruvhaldar/Githubifier)
![PRs](https://img.shields.io/github/issues-pr/dhruvhaldar/Githubifier)

**Githubifier** is a robust Python utility designed to solve the problem of uploading large directories (like CFD cases, datasets, or heavy repos) to GitHub or cloud storage. It compresses a source folder into a multi-part 7-Zip archive, ensuring each part stays within file size limits (e.g., GitHub's 100MB max).

## Key Features

- **Automated Splitting**: Splits large archives into chunks (default 40MB) compatible with GitHub.
- **Smart Repository Batching**: Automatically checks if your target GitHub repository exceeds 4.5GB. If so, it creates a new "batch" repository (e.g., `MyRepo_batch_2`) to store the new archive, keeping your data organized and within limits.
- **Safe Push Technology**: Implements chunked uploading to avoid timeouts and "RPC failed" errors. Large datasets are pushed in safe batches (approx. 500MB each), ensuring reliability even on slower connections.
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
- **GitHub CLI (`gh`)** (Optional but Recommended): Required for automatic repository creation, pushing, and checking remote repository sizes to enable smart batching.

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

### Automatic Batching & Limits
When using Githubifier, your files are organized into batch subfolders (e.g., `Destination/RepoName`, `Destination/RepoName_batch_2`) to manage separate git repositories. This ensures that no single repository exceeds the 4.5GB limit.

Furthermore, Githubifier respects **GitHub Push Limits** to avoid timeouts:
- **Safe Zone (< 500MB)**: Pushes are chunked into batches of roughly 500MB.
- **Caution Zone (500MB - 2GB)**: Avoided by chunking.
- **Danger Zone (> 2GB)**: Strictly avoided.

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

**5. Automatically Push to GitHub (New!):**
This requires the GitHub CLI (`gh`) to be installed and authenticated.
```bash
python githubifier.py "C:\MyLargeDataset" "D:\Backups\MyRepo" --push
```
*This will create a private repository named `MyRepo` and push the archives.*

## Pushing to GitHub

### Option A: Automatic (Recommended)
Use the `--push` flag as shown in Example 5. This handles:
1. Initializing the git repository.
2. Creating a private repository on GitHub.
3. Adding, committing, and pushing the files.

### Option B: Manual (Classic Git)
If you prefer to do it yourself or don't have the GitHub CLI:
1. Create a new repository on GitHub (Manual).
2. Open a terminal in your destination folder.
3. Run:
   ```bash
   git init
   git add .
   git commit -m "Add split archives"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin master
   ```

### Option C: Manual (with gh CLI)
You can also run the commands output by the script manually:
```bash
cd destination_folder
git init
git add .
git commit -m "Add split archives"
gh repo create <repo_name> --private --source=. --remote=origin
git push -u origin master
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
If typing long paths in the command line is tedious, you can use a runner script:
1. Copy `runner.py.example` to `runner.py`.
2. Edit `runner.py` to set your `SOURCE_DIR` and `DEST_DIR`.
3. Run it easily:
```bash
python runner.py
```
*Note: `runner.py` is ignored by git, so your local paths won't be committed.*

## License
[MIT License](LICENSE). Feel free to use and modify!
