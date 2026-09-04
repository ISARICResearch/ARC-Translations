# get_version_path.py
import os
from bridge.arc.arc_api import ArcApiClient

arc_client = ArcApiClient()
all_versions = arc_client.get_arc_version_list()
most_recent_version_str = all_versions[0] if all_versions else None

path = "ARCH" + (most_recent_version_str[1:])
print(f"path found: {path}")

with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"version={most_recent_version_str}\n")