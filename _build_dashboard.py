"""Helper: builds dashboard.html with embedded base64 images."""
import base64, os

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

sd = b64("score_distribution.png")
cm = b64("correlation_matrix.png")

# Read the template
with open("_dashboard_template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("__SD_B64__", sd).replace("__CM_B64__", cm)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"dashboard.html written ({len(html)//1024} KB)")
