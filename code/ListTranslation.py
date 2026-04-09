import os
from numpy import var
import pandas as pd
from deep_translator import  (GoogleTranslator, PonsTranslator, ChatGptTranslator)
from pandas import col

def translate_lists(dir_path, list_item, output_dir_path, lang, lists_translated_dir):
    """
    Translate a specific columns in a CSV file to French.

    Args:
    dir_path (str): Path to the directory where lists are to translate (Parent directory). e.g: ARCH.1.0.1/Lists
    list_item (Str): Name of the specific list (directory) to translate
    columns_df (list): Name of the columns within the list csv file to translate. e.g ["Text", "Description", ...]
    output_dir_path (str): Path to directory where the output CSV file would be.
    lang (dictionary (lang,code)): Language (s) to be translated to in a dictionary format. e.g ("Spanish","es")
    lists_translated_dir (str): Path to the previous version of the translated lists. This is used to copy the translations of unchanged variables and renamed variables. e.g: ARC-Translations/ARCH.1.0.0/Spanish/Lists/

    """
    
    #going through directory dir_path + list_item
    dir_path_item=dir_path+"/"+list_item
    for path, folders, files in os.walk(dir_path_item):
        for filename in files:
            prev_df = None
            prev_map = {}
            lists_translated_file = lists_translated_dir+"/"+list_item+"/"+filename
            if lists_translated_file and os.path.exists(lists_translated_file):
                prev_df = pd.read_csv(lists_translated_file, sep=',', dtype=str).fillna('')
                # build quick lookup map by Value in each csv
                if 'Value' in prev_df.columns:
                    prev_map = {r['Value']: r for _, r in prev_df.iterrows()}
            else:
                print("No previous translation file found at "+str(lists_translated_file)+". Will use empty previous translations (translate all).")
            
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
            
            if os.path.exists(os.path.join(output_dir_path_l3,filename)):
                print("File already created: "+filename)
                continue #go to next file

            # Read the CSV file
            df = pd.read_csv(os.path.join(dir_path_item,filename), sep=',')
            df_final = df.copy()

            # Helper: translation function with safe fallback
            def do_translate(text):
                if pd.isna(text) or text is None:
                    return ''
                s = str(text)
                if not s or len(s) >= 5000:
                    return s
                try:
                    return GoogleTranslator(source='en', target=lang[1]).translate(text=s)
                    #return "Enviada para traducir"
                except Exception:
                    try:
                        # Second attempt: Pons Translator (if Google fails)
                        return PonsTranslator(source='en', target=lang[1]).translate(text=s)
                    except Exception:
                        # failed translator -> return original text
                        return s
            #counting variables
            total_vars = len(df)
            total_vars_found_prev = 0
            for idx, row in df_final.iterrows():
                #ux=input("Quiere continuar con la siguiente?")##solo para pruebas
                valor= str(row.get('Value', '')).strip()
                print("Lista value actual: "+valor)
                if not valor:
                    continue

                # If lists column unchanged and prev translation available, copy it
                if prev_map.get(valor) is not None:
                    print("Lista valor found on previous translation: "+valor)
                    total_vars_found_prev += 1
                    prev_row = prev_map[valor]
                    #listFile.csv: previous translations overwrite original column value
                    if prev_row.get(0) is not None:
                        df_final.at[idx, 0] = prev_row.get(0)
                    continue

                # Otherwise, translate the required columns for this row
                print("Lista value to translate: "+valor+" because previous translations are not available: ")
                original_text = row.get(0, '')
                translated = do_translate(original_text)            
                df_final.at[idx, 0] = translated
            

            #lambda x:GoogleTranslator(source='en', target=lang[1]).translate(text=x) if pd.notnull(x) else x
            #lambda x:PonsTranslator(source='en', target=lang[1]).translate(x) if pd.notnull(x) else x
            #lambda x:ChatGptTranslator(api_key=openaiKey, source='en', target=lang[1]).translate(text=x) if pd.notnull(x) else x
            #df_final.loc[:,'Language Speaker Reviewed'] = None
            #df_final.loc[:,'Clinical Language Speaker Reviewed'] = None
            # Save the updated DataFrame to a new CSV file
            df_final.to_csv(os.path.join(output_dir_path_l3,filename), index=False)
            #print(df.columns)
            print(f"Total vars found in previous translations vs total translated variables: {total_vars_found_prev}/{total_vars}")
            print(f"List Translation complete. Output saved to {output_dir_path_l3} file: {filename}")