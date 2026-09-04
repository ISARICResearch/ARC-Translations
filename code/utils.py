'''

utils.py was created to prevent possible circular dependencies.

It was created originally for one simple helper function, but could be extended to anything that 
is useful in several scripts.

'''

import os

def version_to_path(arc_version):
    return ("ARCH" + (arc_version[1:]))

# Create directory if it doesn't already exist.
def init_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")


'''
    
    @ AIDAN !!  
        ->  We may not need this. First solve how English source is supposed to be filled out.

    Create a CSV file if it doesn't already exist.
    Optionally writes a header row.

'''
import csv

# Create CSV if it doesn't already exist.
def init_csv(path, headers=None):
    if not os.path.exists(path):
        # make sure the parent directory exists too
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if headers:
                writer = csv.writer(f)
                writer.writerow(headers)
        print(f"Created CSV: {path}")
    else:
        print(f"CSV already exists: {path}")