import subprocess, time, os, datetime, sys

REMOTE_URL = os.environ.get("REMOTE_URL") or "git@github.com:<YOUR_USER>/<YOUR_REPO>.git"

def sh(cmd, check=True):
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=check)

def out(cmd):
    return subprocess.check_output(cmd, text=True).strip()

# 0) ensure repo + main branch
inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
if inside.returncode != 0:
    sh(["git", "init"])

try:
    current = out(["git", "rev-parse", "--abbrev-ref", "HEAD"])
except subprocess.CalledProcessError:
    current = "main"

if current == "HEAD":
    sh(["git", "checkout", "-B", "main"])
elif current != "main":
    sh(["git", "checkout", "-B", "main"])

# 0.1) ensure remote
have_origin = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True)
if have_origin.returncode != 0:
    if "<YOUR_USER>" in REMOTE_URL:
        print(">> Please set REMOTE_URL env var to your repo URL before running.")
        sys.exit(1)
    sh(["git", "remote", "add", "origin", REMOTE_URL])

# make sure we’re on main and have at least one file tracked
if not os.path.exists("heartbeat.md"):
    with open("heartbeat.md", "w") as f:
        f.write("# Heartbeat log\n")
    sh(["git", "add", "heartbeat.md"])
    sh(["git", "commit", "-m", "chore: init heartbeat"])

# 1) 4 quick commits on main
for i in range(1, 5):
    with open("heartbeat.md", "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} — ping {i}\n")
    sh(["git", "add", "heartbeat.md"])
    sh(["git", "commit", "-m", f"chore: ping {i}"])
    time.sleep(0.2)

# 2) push main (1st push)
sh(["git", "push", "-u", "origin", "main"])

# helper: does branch exist?
def branch_exists(name: str) -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", name], capture_output=True).returncode == 0

# helper: does upstream exist?
def upstream_exists(name: str) -> bool:
    return subprocess.run(["git", "rev-parse", "--abbrev-ref", f"{name}@{{upstream}}"], capture_output=True).returncode == 0

# 3) create/switch 14 branches → 14 pushes (total pushes = 15)
for j in range(1, 15):
    branch = f"feat/tweak-{j}"

    # create if missing, else checkout
    if branch_exists(branch):
        sh(["git", "checkout", branch])
    else:
        sh(["git", "checkout", "-b", branch])

    # make a small change
    with open("heartbeat.md", "a") as f:
        f.write(f"\nPR tweak line {j}\n")

    sh(["git", "add", "heartbeat.md"])
    sh(["git", "commit", "-m", f"feat: tiny tweak {j}"])

    # push (set upstream only once)
    if upstream_exists(branch):
        sh(["git", "push", "origin", branch])
    else:
        sh(["git", "push", "-u", "origin", branch])

    sh(["git", "checkout", "main"])

print("\nAll done. Exactly 15 pushes total 🌱")