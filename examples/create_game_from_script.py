"""Create a game from a script."""

from pathlib import Path
import shutil
import subprocess


script = Path(r"C:\Users\Lio\pygame_cards\examples\solitaire.py")
examples_dir = Path(r"C:\Users\Lio\pygame_cards\examples")

if __name__ == "__main__":
    # remove the previous folders

    shutil.rmtree(examples_dir / "dist" / script.stem, ignore_errors=True)
    shutil.rmtree(examples_dir / "build" / script.stem, ignore_errors=True)
    (examples_dir / script.stem).with_suffix(".spec").unlink(missing_ok=True)

    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--windowed",
            str(script.name),
        ],
        cwd=str(script.parent),
        stdout=subprocess.PIPE,
    )
