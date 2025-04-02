import sys
import os
import json

# Import the module where the needed scripts are.
#Directory where the BRIDGE repository is
bridge_path="D:/Redaedes/CONTAGIO/WP2/task2.2/code/DataPlatform/BRIDGE"
##!!!!Uncomment to set the path to the BRDIGE repository directory
BRIDGE =os.path.dirname(os.path.realpath(bridge_path))
sys.path.append(BRIDGE)

from BRIDGE import arch
import archtranslation
import ListTranslation
#get the versions from arch repository
all_versions, most_recent_version_str = arch.getARCHVersions()
#print(all_versions)
print("***")
#Code to generate on github repository. uncomment when on github repository
#root_arch='https://raw.githubusercontent.com/ISARICResearch/DataPlatform/main/ARCH/'
#root_arch_t='https://raw.githubusercontent.com/ISARICResearch/ARC-Translations/main/ARCH/'

#code to run locally. uncomment when run locally 
root_arch='ARCH/'
root_arch_t='D:/Redaedes/CONTAGIO/WP2/task2.2/code/ARC-Translations'

###Translations parameters:
#Language definitions to translate [('Language', 'Lang code')]
langs=[('French', 'fr'),('Spanish', 'es'),('Portuguese', 'pt')]

#Translation parameters to set before
#for arch file
arch_file_path_src=root_arch+most_recent_version_str+'/ARCH.csv'
arch_dir_path_des=root_arch_t+'/'+most_recent_version_str+'/'
arch_col_translate=['Form', 'Section', 'Question', 'Answer Options', 'Definition', 'Completion Guideline']
#for paper details file
paper_file_path_src=root_arch+most_recent_version_str+'/paper_like_details.csv'
paper_col_translate=['Paper-like section','Text']
#for lists
lists_file_path_src=root_arch+most_recent_version_str+'/Lists/'
#Lists in the format[('list',['columns'])]. Columns list should be all the possible name of columns to be translated of each list file
lists=[
	('conditions',['Condition']), 
	('demographics',['Region', 'Country', 'Disease']), 
	('drugs', ['Drugs (Generic)', 'Drugs', 'IV fluids']), 
	('inclusion', ['Disease']), 
	('outcome', ['Outcome']), 
	('pathogens', ['Microorganism'])
]

#Translation execution
for lang in langs:
	print("start lang: "+lang[0])
	for li in lists:
		ListTranslation.translate_lists(f'{lists_file_path_src}/', li[0], li[1], arch_dir_path_des, lang)
	archtranslation.translate_arch(paper_file_path_src, paper_col_translate, arch_dir_path_des, lang)
	archtranslation.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang)
	print("--------")