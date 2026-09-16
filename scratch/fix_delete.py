import re

file_path = "userbot.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern to remove `await asyncio.sleep(X)` followed by `try: await prog.delete() except Exception: pass`
pattern = r"(\s+await asyncio\.sleep\(\d+\)\s+try:\s+await prog\.delete\(\)\s+except Exception:\s+pass)"
new_content = re.sub(pattern, "", content)

# Also fix the `await prog.delete()` when `.play` fails and wants to disappear? Maybe keep it for failed? No, let's let failed messages stay so user sees error.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done replacing.")
