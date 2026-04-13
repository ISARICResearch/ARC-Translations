import sys
import os
import json
import re
def _extract_version_nums(s):# return tuple of integer for ARC versioning "ARCH1.2.2-beta" -> (1,2,2)
    nums = re.findall(r'\d+', s)
    return tuple(int(n) for n in nums) if nums else tuple()

def get_previous_version(all_versions, current_version):
    """
    Find the immediate previous version (by numeric components) to current_version among all_versions.
    Returns the original version string or None if not found.
    """
    most_recent_num = _extract_version_nums(current_version)
    if not most_recent_num:
        return None
    pairs = []
    for v in all_versions:
        k = _extract_version_nums(v)
        if k:
            pairs.append((k, v))
    pairs.sort(key=lambda kv: kv[0])
    prev = None
    for k, v in pairs:
        if k < most_recent_num:
            prev = v
        else:
            break# once we hit a version >= current, the last prev is the immediate previous
    return prev

# Import the module where the needed scripts are.
#Directory where the BRIDGE repository is
bridge_path="F:/UAD/CONTAGIO/WP2/task2.2/code/DataPlatform/BRIDGE"
##!!!!Uncomment to set the path to the BRDIGE repository directory
BRIDGE = os.path.dirname(os.path.realpath(bridge_path))
sys.path.append(BRIDGE)

from BRIDGE import arch
import archtranslation_lastversion
import ListTranslation
#get the versions from arch repository
all_versions, most_recent_version_str = arch.getARCHVersions()
#most_recent_version_str = "ARCH1.2.0"##solo para pruebas
previous_version_str=get_previous_version(all_versions, most_recent_version_str)
print("most_recent_version_str: "+most_recent_version_str)
print("previous_version_str: "+previous_version_str)
print("***")

#code to run locally. uncomment when run locally 
root_arc='F:/UAD/CONTAGIO/WP2/task2.2/code/ARC' #this is the directory where the last version of ARC file is located. It should contain the ARC.csv, paper_like_details.csv and Lists/ directory
root_arch_t='F:/UAD/CONTAGIO/WP2/task2.2/code/ARC-Translations' #this is the directory where the translations will be saved

###Translations parameters:
#Language definitions to translate [('Language', 'Lang code')]
langs=[('French', 'fr'),('Spanish', 'es'),('Portuguese', 'pt')]

#for ARC file
arch_file_path_src=root_arc+'/ARC.csv'
##arch_file_path_src=root_arch_t+'/'+most_recent_version_str+'/English/ARCH.csv'##Solo para pruebas
arch_dir_path_des=root_arch_t+'/'+most_recent_version_str+'/' #directory where the translations will be saved.
##arch_dir_path_des='F:/UAD/CONTAGIO/WP2/task2.2/ARC-Translations_bu2025/'+most_recent_version_str+'/'##Solo para pruebas
arch_col_translate=['Form', 'Section', 'Question', 'Answer Options', 'Definition', 'Completion Guideline']

#for paper details file
paper_file_path_src=root_arc+'/paper_like_details.csv'
##paper_file_path_src=root_arch_t+'/'+most_recent_version_str+'/English/paper_like_details.csv'##Solo para pruebas
paper_col_translate=['Paper-like section','Text']

#for lists
lists_file_path_src=root_arc+'/Lists/'
##lists_file_path_src=root_arch_t+'/'+most_recent_version_str+'/English/Lists/'##Solo para pruebas
lists = sorted([
    folder for folder in os.listdir(lists_file_path_src)
    if os.path.isdir(os.path.join(lists_file_path_src, folder)) and not folder.startswith('.')
])

#Translation execution
for lang in langs:
    print("start lang: "+lang[0])
    while True:
        previous_version_str=get_previous_version(all_versions, most_recent_version_str)
        arch_dir_path_prev = root_arch_t+'/'+previous_version_str+'/'
        arc_translated_file=arch_dir_path_prev+lang[0]+'/ARCH.csv'
        lists_translated_dir=arch_dir_path_prev+lang[0]+'/Lists/'
        ##Paper_like_details not included
        if os.path.exists(arc_translated_file):
            print("Previous translation directory found: "+arch_dir_path_prev+lang[0])
            break
        else:
            most_recent_version_str = previous_version_str
            if previous_version_str == None:
                print("Previous translation directory is None: ")
                break
    ttl=0#counter for total variables in lists
    ttt=0#counter for total variables not translated because found in previous translations in lists
    for li in lists:
        total=ListTranslation.translate_lists(f'{lists_file_path_src}/', li, arch_dir_path_des, lang, lists_translated_dir)
        print("LIST: "+li+" Translations found in previous: "+str(total[0])+" out of "+str(total[1]))
        ttt=ttt+total[0]
        ttl=ttl+total[1]
    print(f"TOTAL LISTS: # variables found translated: "+str(ttt)+" out of total variables in lists: "+str(ttl))
    ##ux=input("Quiere continuar con la siguiente?")##solo para pruebas
    paper_t=archtranslation_lastversion.translate_arch(paper_file_path_src, paper_col_translate, arch_dir_path_des, lang, None, None)
    print(f"PAPER_LIKE: Total vars found in previous translations vs total: {paper_t[0]}/{paper_t[1]}")
    ##ux=input("Quiere continuar con la siguiente?")##solo para pruebas
    arch_t=archtranslation_lastversion.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang, arc_translated_file, None)    
    print(f"ARC: Total vars found in previous translations vs total: {arch_t[0]}/{arch_t[1]}")
    print("--------")
