import subprocess, time, datetime

def sh(cmd, check=True):
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=check)

# --- Make sure repo exists & is on main ---
inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
if inside.returncode != 0:
    sh(["git", "init"])

try:
    current = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
except subprocess.CalledProcessError:
    current = "main"

if current == "HEAD":
    sh(["git", "checkout", "-B", "main"])
elif current != "main":
    sh(["git", "checkout", "-B", "main"])

# --- Always use a brand-new file with timestamp ---
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
fname = f"heartbeat_{timestamp}.md"

with open(fname, "w") as f:
    f.write(f"# Heartbeat log created at {timestamp}\n")

sh(["git", "add", fname])
sh(["git", "commit", "-m", f"chore: init {fname}"])

# --- Make 11 commits ---
for i in range(1, 12):
    with open(fname, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} — ping {i}\n")
    sh(["git", "add", fname])
    sh(["git", "commit", "-m", f"chore: ping {i}"])
    time.sleep(0.2)

# --- Pull safely (no stash needed because new file won't conflict) ---
sh(["git", "pull", "--rebase", "origin", "main"])

# --- Push to remote ---
sh(["git", "push", "-u", "origin", "main"])

print(f"\n✅ Done — 11 commits pushed using {fname}")