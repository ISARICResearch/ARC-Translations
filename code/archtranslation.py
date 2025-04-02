import pandas as pd
from deep_translator import (GoogleTranslator, PonsTranslator, ChatGptTranslator)
import sys
import os

def translate_arch(file_path, columns_df, arch_dir_path_des, lang):
    """
    Translate a specific columns in a CSV file to French.

    Args:
    file_path (str): Path to the CSV file to translate.
    columns_df (list): Name of the columns to translate. e.g ["Text", "Description", ...]
    arch_dir_path_des (str): Path to directory where the output CSV file would be.
    lang (dictionary (lang,code)): Language (s) to be translated to in a dictionary format. e.g ("Spanish","es")

    """
    filename = os.path.basename(file_path)
    # Read the CSV file
    df = pd.read_csv(file_path, sep=',')
    #Generate df with only the columns needed
    if filename == 'paper_like_details.csv':
        df_final = df
    elif filename == 'ARCH.csv':
        df_final = df[['Variable']]
        df_final = df[df_final.columns.union(columns_df, False)]

    for column_name in columns_df:
        #Translate the specified column
        if filename == 'paper_like_details.csv':
            column_name1 = column_name+"_translation"
            column_name2 = column_name
        else:
            column_name1 = column_name
            column_name2 = column_name

        df_final[column_name1] = df_final[column_name2].apply(
            lambda x:GoogleTranslator(source='en', target=lang[1]).translate(text=x) if (pd.notnull(x) and len(x)<5000) else x
        )    
    df_final.loc[:,'Language Speaker Reviewed'] = None
    df_final.loc[:,'Clinical Language Speaker Reviewed'] = None
    
    #Create folder structure
    try:
        #first the version folder if it not created
        os.makedirs(arch_dir_path_des, exist_ok=True)
        #second: the language folder
        arch_dir_path_des_dir=arch_dir_path_des+lang[0]+"/"
        os.makedirs(arch_dir_path_des_dir, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=arch_dir_path_des_dir, err=e))

    # Save the updated DataFrame to a new CSV file
    arch_file_path_des=arch_dir_path_des_dir+filename
    df_final.to_csv(arch_file_path_des, index=False)
    print(f"Translation complete. Output saved to {arch_file_path_des}")
    print("**********")