import os
import sys
import subprocess
import shutil
import platform
import signal
import unittest
import argparse
import tempfile
from pathlib import Path

# --- Configuration ---
DEFAULT_SPLIT_SIZE = "40m"
COMPRESSION_LEVEL = "9"  # 9 = Ultra
COMPRESSION_METHOD = "lzma2"

class GithubifierError(Exception):
    """Custom exception for Githubifier errors."""
    pass

def find_7z_binary():
    """
    Locates the 7z executable based on the operating system.

    Returns:
        str: The full path to the 7z executable if found.
        None: If the executable cannot be located.

    Examples:
        >>> find_7z_binary()
        'C:\\Program Files\\7-Zip\\7z.exe'
    """
    # 1. Check system PATH
    seven_z_cmd = shutil.which("7z") or shutil.which("7za")
    if seven_z_cmd:
        return seven_z_cmd

    # 2. Check standard Windows locations
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe"
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    return None

def check_dependencies():
    """
    Checks if all required external dependencies are installed.
    Exits with error if dependencies are missing.
    """
    # 1. Check Python Version
    if sys.version_info < (3, 6):
        print(f"[ERROR] Python 3.6+ is required. You are using {platform.python_version()}")
        sys.exit(1)

    # 2. Check 7-Zip
    if not find_7z_binary():
        print("[ERROR] Critical dependency missing: 7-Zip.")
        print("  - Please install 7-Zip from https://www.7-zip.org/")
        print("  - Ensure '7z' is in your PATH or in a standard install location.")
        print("  - Ensure '7z' is in your PATH or in a standard install location.")
        sys.exit(1)

    # 3. Check Git
    if not shutil.which("git"):
        print("[ERROR] Critical dependency missing: git.")
        print("  - Please install Git from https://git-scm.com/")
        print("  - Ensure 'git' is in your PATH.")
        sys.exit(1)

def check_permissions(source, dest_dir):
    """
    Validates read/write permissions for source and destination.
    """
    # 1. Source Read Check
    if not os.access(source, os.R_OK):
        print(f"[ERROR] Source is not readable: {source}")
        return False
        
    # 2. Destination Write Check
    # Check if we can write to the destination directory or its parent(s)
    chk_path = dest_dir
    while not chk_path.exists():
        # Go up one level
        parent = chk_path.parent
        if parent == chk_path: # Root reached
             break
        chk_path = parent

    if not os.access(chk_path, os.W_OK):
        print(f"[ERROR] Destination path is not writable: {chk_path}")
        return False
             
    return True

def get_dir_size(path):
    """
    Recursively calculates the total size of a directory in bytes.

    Args:
        path (Path or str): The path to the directory.

    Returns:
        int: Total size in bytes.

    Examples:
        >>> get_dir_size("C:/Projects/CFD_Case")
        104857600  # Returns 100 MB in bytes
    """
    total = 0
    try:
        # Use scandir for better performance on large directories
        path_obj = Path(path)
        if not path_obj.exists():
            return 0
            
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry.path)
    except PermissionError:
        print(f"[WARN] Permission denied accessing: {path}")
    return total

def cleanup_partial_files(dest_dir, archive_name_base):
    """
    Removes partial archive files (e.g., .001, .002) if the process fails.

    Args:
        dest_dir (Path): The directory where files were being created.
        archive_name_base (str): The base name of the archive (e.g., 'data.7z').

    Examples:
        >>> cleanup_partial_files(Path("C:/Out"), "data.7z")
        # Deletes C:/Out/data.7z.001, C:/Out/data.7z.002, etc.
    """
    print("\n[SAFETY] Cleaning up partial files...")
    # 7z split files follow pattern: name.7z.001, name.7z.002
    pattern = f"{archive_name_base}.*"
    for f in dest_dir.glob(pattern):
        try:
            f.unlink()
            print(f" - Deleted: {f.name}")
        except OSError as e:
            print(f" - Failed to delete {f.name}: {e}")

def ensure_git_init(dest_dir):
    """
    Ensures the destination directory is a git repository.
    If not, initializes it.
    """
    git_dir = dest_dir / ".git"
    if not git_dir.exists():
        print(f"\n[GIT] Initializing new git repository in: {dest_dir}")
        try:
            subprocess.run(["git", "init"], cwd=dest_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Failed to initialize git repository: {e}")
            # We don't raise error here, as compression can still succeed
    else:
        print(f"\n[GIT] Destination is already a git repository.")

def githubify_safe(source_path, output_dir, split_size=DEFAULT_SPLIT_SIZE, dry_run=False):
    """
    Compresses a source directory into a split 7-Zip archive with safety checks.

    Args:
        source_path (str): Path to the folder to compress.
        output_dir (str): Path where the archive parts will be saved.
        split_size (str): Size of split volumes (e.g., "40m", "100m").
        dry_run (bool): If True, simulates the process without writing files.

    Raises:
        GithubifierError: If validation, compression, or verification fails.

    Examples:
        # Standard Usage
        >>> githubify_safe("C:/CFD/Case1", "D:/Backup", split_size="40m")
        
        # Dry Run (Safe Test)
        >>> githubify_safe("C:/CFD/Case1", "D:/Backup", dry_run=True)
        
        # Large Split Size
        >>> githubify_safe("C:/CFD/Case1", "D:/Backup", split_size="2g")
    """
    source = Path(source_path).resolve()
    dest_dir = Path(output_dir).resolve()
    archive_name = f"{source.name}.7z"
    output_file_path = dest_dir / archive_name
    
    # --- 1. Validation Checks ---
    print(f"--- 1. Pre-flight Checks: {source.name} ---")
    
    
    # Permission Check
    if not check_permissions(source, dest_dir):
        raise GithubifierError("Permission check failed.")

    # Create output dir if needed (Skip in dry run if it doesn't exist)
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        ensure_git_init(dest_dir)
    else:
        print(f"[DRY RUN] Would create directory: {dest_dir}")

    # Check for existing archives to avoid overwrite
    if (dest_dir / f"{archive_name}.001").exists():
        raise GithubifierError(f"Archive already exists in destination: {archive_name}.001")

    # Locate 7-Zip
    seven_z_exe = find_7z_binary()
    if not seven_z_exe:
        raise GithubifierError("7-Zip executable not found. Please install it.")

    # --- 2. Space Check ---
    print("Calculating source size...", end="", flush=True)
    source_size = get_dir_size(source)
    print(f" {source_size / (1024*1024):.2f} MB")
    
    # Check free space on destination drive
    # Only check if destination exists or we are not in dry run
    if dest_dir.exists():
        _, _, free_space = shutil.disk_usage(dest_dir)
        
        # Heuristic: Warn if free space is less than uncompressed source size
        if free_space < source_size:
            print(f"[WARN] Low disk space! Free: {free_space//(1024*1024)}MB, Source: {source_size//(1024*1024)}MB")
            
            if not dry_run:
                # In non-interactive modes (e.g. CI/CD), you might want to force fail here
                if sys.stdin.isatty():
                    confirm = input("Compression might fail or fill the disk. Continue? (y/n): ")
                    if confirm.lower() != 'y':
                        raise GithubifierError("Operation cancelled by user due to disk space.")
                else:
                     print("[WARN] Non-interactive mode: Proceeding despite low disk space warning.")
    else:
        print(f"[DRY RUN] Destination drive space check skipped (dir doesn't exist yet).")

    # --- 3. Compression ---
    print(f"\n--- 2. Compressing & Splitting (Max: {split_size}) ---")
    
    # 7-Zip Command Construction
    cmd = [
        seven_z_exe, "a", 
        str(output_file_path), 
        str(source),
        "-t7z", 
        f"-mx={COMPRESSION_LEVEL}", 
        f"-m0={COMPRESSION_METHOD}",
        "-ms=on", 
        f"-v{split_size}"
    ]

    if dry_run:
        print(f"[DRY RUN] Command to be executed:")
        print(f"  {' '.join(cmd)}")
        print(f"[DRY RUN] This would create files like:")
        print(f"  - {archive_name}.001")
        print(f"  - {archive_name}.002")
        print(f"  - ...")
        return True

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n[INTERRUPT] Process cancelled by user.")
        cleanup_partial_files(dest_dir, archive_name)
        sys.exit(0)
    
    # Register signal only if running in main thread
    try:
        signal.signal(signal.SIGINT, signal_handler)
    except ValueError:
        pass # Signal only works in main thread

    try:
        # Run compression
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        cleanup_partial_files(dest_dir, archive_name)
        raise GithubifierError(f"7-Zip failed with error code {e.returncode}")
    except Exception as e:
        cleanup_partial_files(dest_dir, archive_name)
        raise e

    # --- 4. Integrity Check ---
    print("\n--- 3. Verifying Integrity ---")
    # We test the first volume; 7z automatically follows the split chain
    first_vol = dest_dir / f"{archive_name}.001"
    
    if not first_vol.exists():
        # Edge case: If file was small enough to not split, it might just be .7z
        # But -v switch usually forces .001 even for single files in newer 7z versions
        if (dest_dir / archive_name).exists():
             first_vol = dest_dir / archive_name
        else:
             raise GithubifierError("Created archive file not found for verification.")

    verify_cmd = [seven_z_exe, "t", str(first_vol)]
    
    try:
        subprocess.run(verify_cmd, check=True, stdout=subprocess.DEVNULL)
        print("[SUCCESS] Archive verified successfully.")
    except subprocess.CalledProcessError:
        print("[CRITICAL ERROR] Archive verification failed! Data may be corrupt.")
        cleanup_partial_files(dest_dir, archive_name)
        raise GithubifierError("Integrity check failed.")

    print(f"\n[DONE] Archive saved to: {dest_dir}")
    return True

def run_custom_task(source_dir, dest_dir, split_size, dry_run=True):
    """
    Wrapper for running Githubifier from a custom runner script.
    Handles user interaction, validation, and error reporting.
    """
    print("--- Githubifier Runner ---")
    print(f"Source:      {source_dir}")
    print(f"Destination: {dest_dir}")
    print(f"Split Size:  {split_size}")
    print(f"Mode:        {'DRY RUN (No files will be created)' if dry_run else 'LIVE EXECUTION'}")
    print("-" * 30)

    # Basic validity check for the default placeholder value
    # We check if the path contains 'Path\To\Your' as a heuristic for unmodified template
    if not os.path.exists(source_dir) or "Path\\To\\Your" in str(source_dir):
         print(f"[ERROR] Source path is invalid or does not exist: {source_dir}")
         print("        Please update 'SOURCE_DIR' in your runner script.")
         return

    # Check dependencies
    try:
        check_dependencies()
    except SystemExit:
        return 

    try:
        githubify_safe(source_dir, dest_dir, split_size=split_size, dry_run=dry_run)
    except GithubifierError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")

    input("\nPress Enter to exit...")

# --- Unit Tests ---
class TestGithubifier(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.source_dir = Path(self.test_dir.name) / "source_data"
        self.output_dir = Path(self.test_dir.name) / "output_data"
        
        self.source_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create dummy files
        with open(self.source_dir / "test.txt", "w") as f:
            f.write("This is a test file for Githubifier." * 100)
        
    def tearDown(self):
        # Cleanup temporary directory
        self.test_dir.cleanup()

    def test_find_7z(self):
        """Test that 7z binary is found."""
        binary = find_7z_binary()
        if binary:
             self.assertTrue(os.path.exists(binary))

    def test_dry_run(self):
        """Test that dry run completes without error and creates no files."""
        githubify_safe(self.source_dir, self.output_dir, dry_run=True)
        # Verify no archive was created
        self.assertFalse((self.output_dir / "source_data.7z.001").exists())

if __name__ == "__main__":
    # --- CLI ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(
        description="Githubifier: Compress and split folders for GitHub/Cloud Storage.",
        epilog="Example: python githubifier_v5.py C:/MyData C:/Backups --split 95m"
    )
    
    parser.add_argument("source", nargs="?", help="Source folder path to compress")
    parser.add_argument("destination", nargs="?", help="Destination folder for output files")
    parser.add_argument("--split", default=DEFAULT_SPLIT_SIZE, help=f"Split size (e.g., 10m, 1g). Default: {DEFAULT_SPLIT_SIZE}")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without writing files")
    parser.add_argument("--test", action="store_true", help="Run internal unit tests")

    args = parser.parse_args()

    # Mode 1: Unit Tests
    if args.test:
        print("Running internal unit tests...")
        # Clear args so unittest module doesn't get confused
        sys.argv = [sys.argv[0]]
        unittest.main()
        sys.exit(0)

    # Mode 2: Missing Arguments (Show Help)
    if not args.source or not args.destination:
        parser.print_help()
        sys.exit(1)

    # Mode 3: Normal Execution
    check_dependencies()
    try:
        githubify_safe(args.source, args.destination, args.split, args.dry_run)
    except GithubifierError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        sys.exit(1)