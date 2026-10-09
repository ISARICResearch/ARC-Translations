import json
import os
import urllib.request
from urllib.error import HTTPError
from urllib.parse import quote
import shutil


'''

    This file generates a source English folder for the core ARC-Translations code to use.
    It uses the bridge api to get the commit sha and ARC.csv
    Then just asks 

'''

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "repo-folder-copier",  # GitHub rejects requests without a User-Agent
}

# _MAIN_ that generates a source english folder that will be translated
def generate_english_source(path, arc, version_v, prev_path):
    # 1. get commit sha
    commit_sha = arc.get_arc_version_sha("v1.6.1")

    # 2. Get ARC.csv with bridge API
    print("Retrieving english arc.csv, " + version_v)
    arc_full = arc.get_dataframe_arc_sha(commit_sha, version_v)
    arc_columns=['Form', 'Section', 'Variable', 'Question', 'Answer Options', 'Definition', 'Completion Guideline']   
    arc_short = arc_full[arc_columns]
    raw_path = os.path.join(path, 'ARCH.csv')
    arc_short.to_csv(raw_path, index=False)

    # 3. Get other arc files that are needed, outside of "ARC.csv"
    print("Retrieving english other CSVs, " + version_v)
    otherFiles = {"Lists", "crf_metadata.csv", "paper_like_details.csv"}
    get_arc_other_csvs(commit_sha, path, otherFiles);   

    # 4. Pull in most recent supplemental phrases
    print("Copying supplumental phrases...")
    retrieve_supplemental_phrases(path, prev_path);
    
   

# _primary_ download csvs using custom connection to Github; separate from Bridge API
def get_arc_other_csvs(sha, path, wanted):
    '''
        branch_data = get_json(f"https://api.github.com/repos/ISARICResearch/ARC/branches/main")
        print("commit_data")
        print(commit_data)
        print("tree_url")
        print(tree_url)
    '''

    # Get branch json data
    commit_data = get_json(f"https://api.github.com/repos/ISARICResearch/ARC/git/commits/{sha}")
    tree_url = commit_data["tree"]["url"]
    tree_json = get_json(tree_url) 

    # Debug contents
    #for item in tree_json["tree"]: print(f"{item['type']:<5} {item['path']}")

    # Download each item from json contents that is also "Wanted"
    found = set()
    for item in tree_json["tree"]:
        name = item["path"]
        if name not in wanted: continue
        
        found.add(name)

        if item["type"] == "blob": download_file(name, sha, path)

        elif item["type"] == "tree":
            # one call returns everything under this folder
            sub = get_json(f"{item['url']}?recursive=1")
            if sub.get("truncated"):
                print(f"Warning: {name} tree was truncated")
            for sub_item in sub["tree"]:
                if sub_item["type"] == "blob":
                    if sub_item['path'].endswith(".csv"):
                        download_file(f"{name}/{sub_item['path']}", sha, path)

    missing = wanted - found
    if missing:
        print(f"Warning: not found in repo root: {', '.join(sorted(missing))}")

# _utility_ to get json from url
def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except HTTPError as e:
        raise RuntimeError(f"Fetch error {e.code} for {url}") from e

# _utility_ to download from sha and path
def download_file(path: str, sha: str, dest: str):
    url = f"https://raw.githubusercontent.com/ISARICResearch/ARC/{sha}/{quote(path)}"
    local_path = os.path.join(dest, path)
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "repo-folder-copier"})
    with urllib.request.urlopen(req) as resp, open(local_path, "wb") as f:
        f.write(resp.read())
    #print(f"Copied {path}")

# _primary_ copy supplemental phrases as they are stored in the last version.
def retrieve_supplemental_phrases(new_path, old_path):
    copy = new_path+"supplemental_phrases.csv";
    original = old_path+"supplemental_phrases.csv";
    # if it exists in new path, end
    if os.path.isfile(copy): return;
    # if the original exists, copy it to new path
    if os.path.isfile(original): shutil.copy2(original, copy)
        