import pandas as pd
import requests

print("✅ VS Code environment ready!")
print("Pandas version:", pd.__version__)

r = requests.get("https://api.github.com")
print("GitHub API status:", r.status_code)