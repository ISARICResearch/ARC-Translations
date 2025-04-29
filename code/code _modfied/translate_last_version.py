import sys
import os
import json


import archtranslation
import ListTranslation


#code to run locally. uncomment when run locally 
root_arch='C:/Users/sduquevallejo/Documents/GitHub/DataPlatform/ARCH/'

root_arch_t='C:/Users/sduquevallejo/Documents/GitHub/ARC-Translations'

most_recent_version_str='ARCH1.1.0'

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
	('demographics',['Region', 'Country', 'Disease','Race']), 
	('drugs', ['Drugs (Generic)', 'Drugs', 'IV fluids']), 
	('inclusion', ['Disease']), 
	('outcome', ['Outcome','Disease']), 
	('pathogens', ['Microorganism','Sample_Type']),
    ('followup', ['Outcome','Sequelae'])
]

#Translation execution
for lang in langs:
    print("start lang: "+lang[0])
    for li in lists:
        ListTranslation.translate_lists(f'{lists_file_path_src}/', li[0], li[1], arch_dir_path_des, lang)
	#archtranslation.translate_arch(paper_file_path_src, paper_col_translate, arch_dir_path_des, lang)
    archtranslation.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang)
    print("--------")