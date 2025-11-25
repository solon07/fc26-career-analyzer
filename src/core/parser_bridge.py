"""
Bridge between Python and Node.js parser.
Handles calling the Node.js fifa-career-save-parser.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any


class ParserBridge:
    """
    Bridge to call Node.js parser from Python.
    """

    def __init__(self):
        self.parser_dir = Path(__file__).parent.parent.parent / "parser"
        self.parser_script = self.parser_dir / "test_parser.js"
        self.output_file = self.parser_dir / "output" / "test_parse.json"

    def parse_save(self, save_path: str = None) -> Dict[str, Any]:
        """
        Parse FC 26 save file using Node.js parser.

        Args:
            save_path: Path to save file (optional, uses .env default if not provided)

        Returns:
            Dictionary with parsed tables

        Raises:
            RuntimeError: If parser fails
            FileNotFoundError: If parser script or output not found
        """
        print("Calling Node.js parser...")

        # Verify parser script exists
        if not self.parser_script.exists():
            raise FileNotFoundError(f"Parser script not found: {self.parser_script}")

        # Call Node.js parser
        try:
            # Run parser script
            result = subprocess.run(
                ["node", str(self.parser_script)],
                cwd=str(self.parser_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,  # 60 second timeout
            )

            # Check if parser succeeded
            if result.returncode != 0:
                print("Parser failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                raise RuntimeError(f"Parser exited with code {result.returncode}")

            print("Parser completed successfully")
            print(result.stdout)  # Show parser output

        except subprocess.TimeoutExpired:
            raise RuntimeError("Parser timed out after 60 seconds")
        except Exception as e:
            raise RuntimeError(f"Failed to run parser: {e}")

        # Read JSON output
        if not self.output_file.exists():
            raise FileNotFoundError(f"Parser output not found: {self.output_file}")

        print(f"Reading parsed data from: {self.output_file}")

        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Merge list of databases if necessary
        if isinstance(data, list):
            merged_data = {}
            for db in data:
                merged_data.update(db)
            data = merged_data

        print(f"Loaded {len(data)} tables from parser output")

        return data


# Singleton instance
parser_bridge = ParserBridge()
