import os
import pandas as pd
from deep_translator import GoogleTranslator  # Puedes cambiar aquí si usas otro traductor
import sys

def translate_lists(dir_path, list_item, columns_df, output_dir_path, lang):
    """
    Translate specific columns in CSV files to the target language.

    Args:
        dir_path (str): Parent directory containing lists (e.g. "ARCH.1.0.1/Lists")
        list_item (str): Name of the subdirectory to translate
        columns_df (list): List of column names to translate
        output_dir_path (str): Base path to save translated output
        lang (tuple): Target language in format ("French", "fr")
    """

    def safe_translate(x):
        if pd.notnull(x):
            try:
                return GoogleTranslator(source='en', target=lang[1]).translate(text=str(x))
            except Exception as e:
                print(f"[WARNING] Could not translate '{x}': {e}")
                return x
        return x

    dir_path_item = os.path.join(dir_path, list_item)

    for path, folders, files in os.walk(dir_path_item):
        for filename in files:
            # Read the CSV file
            file_path = os.path.join(dir_path_item, filename)
            df = pd.read_csv(file_path, sep=',')
            df_final = df.copy()

            # Translate specified columns
            for column_name in columns_df:
                if column_name in df.columns:
                    df_final[column_name] = df[column_name].apply(safe_translate)

            # Add empty columns for review
            df_final['Language Speaker Reviewed'] = None
            df_final['Clinical Language Speaker Reviewed'] = None

            # Create output directories
            try:
                os.makedirs(output_dir_path, exist_ok=True)
                output_dir_path_l = os.path.join(output_dir_path, lang[0])
                os.makedirs(output_dir_path_l, exist_ok=True)
                output_dir_path_l2 = os.path.join(output_dir_path_l, "Lists")
                os.makedirs(output_dir_path_l2, exist_ok=True)
                output_dir_path_l3 = os.path.join(output_dir_path_l2, list_item)
                os.makedirs(output_dir_path_l3, exist_ok=True)
            except OSError as e:
                sys.exit(f"Can't create {output_dir_path_l3}: {e}")

            # Save translated DataFrame
            output_file_path = os.path.join(output_dir_path_l3, filename)
            df_final.to_csv(output_file_path, index=False)
            print(f"✅ List translation complete. Output saved to {output_file_path}")

'''
import os
import pandas as pd
from deep_translator import  (GoogleTranslator, PonsTranslator, ChatGptTranslator)

def translate_lists(dir_path, list_item, columns_df, output_dir_path, lang):
    """
    Translate a specific columns in a CSV file to French.

    Args:
    dir_path (str): Path to the directory where lists are to translate (Parent directory). e.g: ARCH.1.0.1/Lists
    list_item (Str): Name of the specific list (directory) to translate
    columns_df (list): Name of the columns within the list csv file to translate. e.g ["Text", "Description", ...]
    output_dir_path (str): Path to directory where the output CSV file would be.
    lang (dictionary (lang,code)): Language (s) to be translated to in a dictionary format. e.g ("Spanish","es")

    """
    #going through directory dir_path + list_item
    dir_path_item=dir_path+"/"+list_item
    for path, folders, files in os.walk(dir_path_item):
        for filename in files:
            # Read the CSV file
            df = pd.read_csv(os.path.join(dir_path_item,filename), sep=',')
            df_final = df
            for column_name in columns_df:
                if column_name in df.columns:
                    df_final[column_name] = df[column_name].apply(
                        lambda x:GoogleTranslator(source='en', target=lang[1]).translate(text=x) if pd.notnull(x) else x
                    )
            #lambda x:GoogleTranslator(source='en', target=lang[1]).translate(text=x) if pd.notnull(x) else x
            #lambda x:PonsTranslator(source='en', target=lang[1]).translate(x) if pd.notnull(x) else x
            #lambda x:ChatGptTranslator(api_key=openaiKey, source='en', target=lang[1]).translate(text=x) if pd.notnull(x) else x
            df_final.loc[:,'Language Speaker Reviewed'] = None
            df_final.loc[:,'Clinical Language Speaker Reviewed'] = None
            try:
                #first the version folder if it not created
                os.makedirs(output_dir_path, exist_ok=True)
                #second: the language folder
                output_dir_path_l=output_dir_path+lang[0]+"/"
                os.makedirs(output_dir_path_l, exist_ok=True)
                #third: the lists folder
                output_dir_path_l2=output_dir_path_l+"Lists/"
                os.makedirs(output_dir_path_l2, exist_ok=True)
                #fourth: the specific list folder
                output_dir_path_l3=output_dir_path_l2+list_item+"/"
                os.makedirs(output_dir_path_l3, exist_ok=True)
            except OSError as e:
                sys.exit("Can't create {dir}: {err}".format(dir=output_dir_path_l3, err=e))
            
            # Save the updated DataFrame to a new CSV file
            df_final.to_csv(os.path.join(output_dir_path_l3,filename), index=False)
            #print(df.columns)
            print(f"List Translation complete. Output saved to {output_dir_path_l3} file: {filename}")
'''