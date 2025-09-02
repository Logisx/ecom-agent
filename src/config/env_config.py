import os
import sys

class EnvConfig:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            print("ERROR: GOOGLE_API_KEY environment variable is not set.", file=sys.stderr)
            sys.exit(1)
