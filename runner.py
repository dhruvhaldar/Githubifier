import githubifier

# --- Configuration ---
# Update these paths to your specific needs.
# Use raw strings (r"path") to avoid issues with backslashes.
SOURCE_DIR = r"C:\Path\To\Your\Source\Folder"
DEST_DIR = r"C:\Path\To\Your\Destination\Folder"
SPLIT_SIZE = "40m"

# Set to False to actually perform the compression
DRY_RUN = True 

if __name__ == "__main__":
    githubifier.run_custom_task(SOURCE_DIR, DEST_DIR, SPLIT_SIZE, DRY_RUN)
