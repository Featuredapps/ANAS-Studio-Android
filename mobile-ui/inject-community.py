from pathlib import Path
import sys
html_path, js_path = Path(sys.argv[1]), Path(sys.argv[2])
html = html_path.read_text(encoding="utf-8")
js = js_path.read_text(encoding="utf-8")
if "ANAS_COMMUNITY_READY" in html:
    raise SystemExit("Community UI already injected; refusing duplicate insertion.")
pos = html.lower().rfind("</body>")
if pos < 0:
    raise SystemExit("Closing body tag not found.")
html_path.write_text(html[:pos] + '<script id="anas-community-script">\n' + js + '\n</script>\n' + html[pos:], encoding="utf-8")
print("Injected community engagement and notification UI.")
