import os
import sys
import subprocess
import shutil

def main():
    print("Starting build process for Audio/Video Merger...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    script_path = os.path.join("media", "audio-video-merge", "audio-video-merge.py")
    if not os.path.exists(script_path):
        # Fallback if run from inside 'media' folder
        if os.path.basename(os.getcwd()) == 'media':
            script_path = os.path.join("audio-video-merge", "audio-video-merge.py")
        else:
            print(f"Error: Could not find {script_path}. Make sure you are in the project root directory.")
            sys.exit(1)

    print(f"Building executable for {sys.platform}...")
    
    # Base command for PyInstaller
    command = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--noconfirm"
    ]
    
    # Platform specific flags
    if sys.platform == 'win32':
        command.append("--noconsole")
    elif sys.platform == 'darwin':
        # macOS specific
        command.append("--windowed")
    else:
        # Linux specific
        command.append("--noconsole")
        
    command.append(script_path)
    
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command)
    
    if result.returncode == 0:
        print("\nBuild successful!")
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            files = os.listdir(dist_dir)
            if files:
                print(f"Executable can be found in the '{dist_dir}' folder: {files[0]}")
    else:
        print("\nBuild failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
