import sys
import os
import json
import re
from bridge.arc.arc_api import ArcApiClient
from utils import init_dir

def _extract_version_nums(s):# return tuple of integer for ARC versioning "ARCH1.2.2-beta" -> (1,2,2)
    nums = re.findall(r'\d+', s)
    return tuple(int(n) for n in nums) if nums else tuple()

def get_previous_version(all_versions, current_version):
    """
    Find the immediate previous version (by numeric components) to current_version among all_versions.
    Returns the original version string or None if not found.
    """
    most_recent_num = _extract_version_nums(current_version)
    #print("Most recent version numeric:", most_recent_num)
    if not most_recent_num:
        return None
    pairs = []
    for v in all_versions:
        k = _extract_version_nums(v)
        if k:
            pairs.append((k, v))
    #print(pairs)
    pairs.sort(key=lambda kv: kv[0])
    prev = None
    for k, v in pairs:
        if k < most_recent_num:
            prev = v
        else:
            break# once we hit a version >= current, the last prev is the immediate previous
    return prev

'''

# Import the module where the needed scripts are.
#code to run locally. uncomment when run locally 
root_arch_t='F:/UAD/CONTAGIO/WP2/task2.2/code/ARC-Translations' #this is the directory where the translations are
#Directory where the BRIDGE repository is
bridge_path="F:/UAD/CONTAGIO/WP2/task2.2/code/BRIDGE"
sys.path.insert(0, bridge_path)  # Use insert(0) for priority
from bridge.arc.arc_api import ArcApiClient
'''

# Get the project root path
root_arch_t = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("root_arch_t:"+root_arch_t)

import translation.ArchTranslation as ArchTranslation, translation.PaperTranslation as PaperTranslation, translation.ListTranslation as ListTranslation

#get the versions from arch repository
arc_client = ArcApiClient()
all_versions = arc_client.get_arc_version_list()
#print("All versions:", all_versions)
most_recent_version_str = all_versions[0] if all_versions else None
#most_recent_version_str = "v1.3.0"#solo para prueba
print("Most recent version:", most_recent_version_str)
previous_version_str = all_versions[1] if len(all_versions) > 1 else None
print("previous_version_str:", previous_version_str)






###Translations parameters:
#Language definitions to translate [('Language', 'Lang code')]
#langs=[('French', 'fr'),('Spanish', 'es'),('Portuguese', 'pt')]
langs=[('Spanish', 'es')]
arch_dir_path_des=root_arch_t+'/'+arc_client.get_arch_version_string(most_recent_version_str)+'/' #directory where the translations will be saved.
init_dir(arch_dir_path_des)


#for ARC file
arch_file_path_src=arch_dir_path_des+'English/ARCH.csv'
init_dir(arch_file_path_src+'English/')

##arch_file_path_src=arch_dir_path_des+'/English/ARCH.csv'##Solo para pruebas
arch_col_translate=['Form', 'Section', 'Question', 'Answer Options', 'Definition', 'Completion Guideline']



#for paper details file
paper_file_path_src=arch_dir_path_des+'English/paper_like_details.csv'
##paper_file_path_src=arch_dir_path_des+'/English/paper_like_details.csv'##Solo para pruebas
paper_col_translate=['Paper-like section','Text']



#for lists
lists_file_path_src=arch_dir_path_des+'English/Lists/'
init_dir(lists_file_path_src)

lists = sorted([    
    folder for folder in os.listdir(lists_file_path_src)
    if os.path.isdir(os.path.join(lists_file_path_src, folder)) and not folder.startswith('.')
])


'''

Adding this. Need to save it as english arch.csv

'''
print("commit_sha")
commit_sha = ArcApiClient().get_arc_version_sha(most_recent_version_str)
print("df_datadicc")
df_datadicc = ArcApiClient().get_dataframe_arc_sha(commit_sha, most_recent_version_str)

raw_path = os.path.join(arch_file_path_src+'English/', 'ARCH_raw.csv')
df_datadicc.to_csv(raw_path, index=False)

#get_arc = arc_client.get_dataframe_arc_sha(sha, version)(most_recent_version_str)

print(df_datadicc)
print("***")





#Translation execution
for lang in langs:
    print("start lang: "+lang[0])
    while True:
        previous_version_str=get_previous_version(all_versions, most_recent_version_str)
        arch_dir_path_prev = root_arch_t+'/'+arc_client.get_arch_version_string(previous_version_str)+'/'
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
    #ux=input("Quiere continuar con la siguiente?")##solo para pruebas
    
    # If this doesn't work, we can just comment it out for now
    paper_t=PaperTranslation.translate_paper(paper_file_path_src, paper_col_translate, arch_dir_path_des, lang, None, None)
    print(f"PAPER_LIKE: Total vars found in previous translations vs total: {paper_t[0]}/{paper_t[1]}")
    #ux=input("Quiere continuar con la siguiente?")##solo para pruebas    
    arch_t=ArchTranslation.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang, arc_translated_file, arch_dir_path_prev)    
    print(f"ARCH: Total vars found in previous translations vs total: {arch_t[0]}/{arch_t[1]}")
    print("--------")