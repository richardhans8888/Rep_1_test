import subprocess, time, os, sys, datetime

def sh(cmd, check=True):
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=check)

# make sure we’re on main and have at least one file tracked
if not os.path.exists("heartbeat.md"):
    with open("heartbeat.md", "w") as f:
        f.write("# Heartbeat log\n")
    sh(["git","add","heartbeat.md"])
    sh(["git","commit","-m","chore: init heartbeat"])

# 1) make 10 quick commits that change a single file
for i in range(1, 11):
    with open("heartbeat.md", "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} — ping {i}\n")
    sh(["git","add","heartbeat.md"])
    sh(["git","commit","-m", f"chore: ping {i}"])
    time.sleep(0.2)  # tiny delay so timestamps differ

# 2) push main
sh(["git","push","-u","origin","main"])

# 3) create a branch, make a change, push it
branch = "feat/mini-tweak"
sh(["git","checkout","-b", branch])
with open("heartbeat.md", "a") as f:
    f.write("\nPR tweak line\n")
sh(["git","add","heartbeat.md"])
sh(["git","commit","-m","feat: tiny tweak for PR"])
sh(["git","push","-u","origin", branch])

# 4) open a pull request (using GitHub CLI) and auto-merge it
#    requires: `gh auth login`
sh(["gh","pr","create","--fill"], check=False)            # opens PR with default title/body
sh(["gh","pr","merge","--squash","--auto"], check=False)  # auto-merge when checks pass

# 5) open a few issues (these count on your activity wheel)
for n in range(1, 4):
    sh([
        "gh","issue","create",
        "--title", f"Tracking issue {n}",
        "--body",  f"utomated issue {n} to light up the graph."
    ], check=False)

print("\nAll done. Enjoy the green 🌱")# PR demo line
