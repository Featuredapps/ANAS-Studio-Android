from pathlib import Path
import re
import subprocess
import sys
import tempfile

html = Path(sys.argv[1]).read_text(encoding="utf-8")
scripts = re.findall(r"<script\b[^>]*>([\s\S]*?)</script\s*>", html, flags=re.I)
if not scripts:
    raise SystemExit("No inline JavaScript found")
combined = "\n;\n".join(block for block in scripts if block.strip())
required = [
    "function exportStudioBackup()",
    "function importStudioBackup(event)",
    "function updateScriptEditorMetrics()",
    "function restoreProjectAudioAssets()",
    "function startCompleteRender(",
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit("Missing required app features: " + ", ".join(missing))
with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
    tmp.write(combined)
    path = tmp.name
result = subprocess.run(["node", "--check", path], text=True, capture_output=True)
if result.returncode:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(result.returncode)
print(f"Validated {len(scripts)} inline script block(s); required studio features found.")
