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
    "function saveProjectAudioAsset(",
    "function scheduleStudioAutosave()",
    "window.addEventListener('pagehide'",
    "PROJECT_AUDIO_STORE.set = function(projectId, audio)",
    "function startCompleteRender(",
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit("Missing required app features: " + ", ".join(missing))

# Script-editor hardening is applied opportunistically by the enhancement patcher.
# Some supported project archive revisions already implement equivalent save/restore
# flows with different syntax, so don't require patch-specific local variable names.
if "function saveScriptEditorChanges(" not in html:
    raise SystemExit("Script editor save handler missing")
if "SCRIPTS = restored" not in html:
    raise SystemExit("Project backup restore handler missing")

with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
    tmp.write(combined)
    path = tmp.name
result = subprocess.run(["node", "--check", path], text=True, capture_output=True)
if result.returncode:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(result.returncode)
print(f"Validated {len(scripts)} inline script block(s); required studio features found.")
