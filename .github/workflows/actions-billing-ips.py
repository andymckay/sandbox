import re
import requests
import subprocess
import sys
import time

from actions_ips import ips

ip_regex = re.compile(r"^\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
source_file = "lib/github/config/actions_runner_ips.rb"

# This is parsing the ruby file and will be fragile depending upon
# changes in the ruby file.
with open(source_file, "rb") as infile:
    header, footer = [], []
    ip_found = False
    for line in infile.readlines():
        line = line.decode("utf-8")
        if not ip_regex.match(line):
            footer.append(line) if ip_found else header.append(line)
        else:
            ip_found = True

with open(source_file, "w") as outfile:
    outfile.writelines(header)
    for ip in ips.cidrs():
        outfile.writelines("        %s\n" % ip)
    outfile.writelines(footer)
    outfile.close()

def cmd(*args):
    res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print("Error occurred on calling: %s" % ' '.join(args))
        print(res.stderr.decode("utf-8"))
        sys.exit(res.returncode)
    return res

# Diff what we've just got against whats in this repo, see if it has changed.
res = cmd("git", "diff", source_file)
if res.stdout:
    print("The files have differed. Creating a PR.")
    print(res.stdout.decode("utf-8"))
    # Some git shenanigans to create a pull request.
    cmd("git", "checkout", "-b", "update-ips-%s" % time.time())
    cmd("git", "config", "user.email", "andymckay@github.com")
    cmd("git", "config", "user.name", "Andy McKay")
    cmd("git", "commit", "-m", "Auto update billing", source_file)
    cmd(
        "gh",
        "pr",
        "create",
        "-t",
        "Update IPs for Actions billing",
        "-b",
        "This is a script that updates the IP address we use for billing, please see https://github.com/github/c2c-actions-experience/blob/master/doc/actions-ip-addresses.md for next steps.",
    )
    print("Successfully created PR.")

else:
    print("The files are not different, exiting successfully.")
