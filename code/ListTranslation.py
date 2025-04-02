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