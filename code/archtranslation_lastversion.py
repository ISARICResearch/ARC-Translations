# ...existing code...
import time

import pandas as pd
from deep_translator import (GoogleTranslator, PonsTranslator, ChatGptTranslator)
import sys
import os
##archtranslation_v2.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang, arc_translated_file, arch_dir_path_prev)
def translate_arch(file_path, columns_df, arch_dir_path_des, lang, prev_translation_path=None, arch_dir_path_prev=None):
    """
    Translate specified columns in a CSV file but reuse previous translations when variables are unchanged or renamed.

    Args:
      file_path (str): Path to the CSV file to translate.
      columns_df (list): Names of columns to translate.
      arch_dir_path_des (str): Destination base directory for outputs.
      lang (tuple): ("Language", "code") e.g. ("Spanish","es").
      prev_translation_path (str|None): CSV path of previous-version translated ARCH (optional).
      arch_dir_path_prev (str|None): Path to previous version translation directory (used to copy unchanged form and section translations)

    """
    filename = os.path.basename(file_path)
    arch_dir_path_des_file = os.path.join(arch_dir_path_des, lang[0]) + os.sep + filename
    total_vars = 0
    total_vars_found_prev = 0
    if os.path.exists(arch_dir_path_des_file):
        print("ARCH File already created: "+filename)
        return (0, 0) #skip translation for this file
    
    df = pd.read_csv(file_path, sep=',')
    # Prepare output df: for ARCH.csv behavior was to overwrite the original columns with translations.
    cols_to_keep = ['Form', 'Section', 'Variable'] + [col for col in columns_df if col not in ['Form', 'Section', 'Variable']]
    df_final = df[cols_to_keep].copy()
    # prepare destination folder for this language
    try:
        os.makedirs(arch_dir_path_des, exist_ok=True)
        arch_dir_path_des_dir = os.path.join(arch_dir_path_des, lang[0]) + os.sep
        os.makedirs(arch_dir_path_des_dir, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {arch_dir_path_des_dir}: {e}")

    # Load previous translations if provided and build lookup maps
    prev_df = None
    prev_map = {}
    map_var_form_section = {}
    prev_form = {}
    prev_section= {}
    if arch_dir_path_prev and os.path.exists(arch_dir_path_prev):
        #directory exists
        prev_english_file=arch_dir_path_prev+'English/ARCH.csv'
        if prev_english_file and os.path.exists(prev_english_file):
            prev_english_df = pd.read_csv(prev_english_file, sep=',', dtype=str).fillna('')
            for idx, r in prev_english_df.iterrows():
                var = str(r.get('Variable', '')).strip()
                if var:
                    form = str(r.get('Form', '')).strip()
                    section = str(r.get('Section', '')).strip()
                    map_var_form_section[var] = {
                        'Form': form,
                        'Section': section
                    }
                    if form is not None and form != '':
                        prev_form[form] = None
                    if section is not None and section != '':
                        prev_section[section] = None
        else:
            print("No previous English file found at "+str(prev_english_file)+".")
        
        if prev_translation_path and os.path.exists(prev_translation_path):
            prev_df = pd.read_csv(prev_translation_path, sep=',', dtype=str).fillna('')
            # build quick lookup map by Variable
            if 'Variable' in prev_df.columns:
                #prev_map = {r['Variable']: r for _, r in prev_df.iterrows()}
                for idx, r in prev_df.iterrows():
                    prev_map[r['Variable']] = r
                    form=map_var_form_section.get(r['Variable'], {}).get('Form', '')
                    section=map_var_form_section.get(r['Variable'], {}).get('Section', '')
                    if form is not None and form != '':
                        prev_form[form] = r['Form']
                    
                    if section is not None and section != '':
                        prev_section[section] = r['Section']
        else:
            print("No previous translation file found at "+str(prev_translation_path)+". Will use empty previous translations (translate all).")
    else:
        print("No previous translation directory found at "+str(arch_dir_path_prev)+".")

    #print(f"prev form: {prev_form}")
    #print(f"prev section: {prev_section}")   
    
    # Helper: translation function with safe fallback
    def do_translate(text):
        s = str(text)
        if pd.isna(text) or text is None:
            return ''
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
    for idx, row in df_final.iterrows():
        #ux=input("Quiere continuar con la siguiente?")##solo para pruebas
        var = str(row.get('Variable', '')).strip()
        #print("Variable actual: "+var)
        if not var:
            continue

        if prev_map.get(var) is not None:
            #print("Variable found on previous translation: "+var)
            prev_row = prev_map[var]
            total_vars_found_prev += 1
        else:
            prev_row = None
        # Otherwise, translate the required columns for this row
        #print("Variable a traducir: "+var+" porque 1) es nueva o sufrió cambios de contenido o 2) no hay traducción previa: ")
        for col in columns_df:
            original_text = row.get(col, '')
            if col == 'Form' and prev_form.get(original_text) is not None:
                translated = prev_form.get(original_text)
            elif col == 'Section' and prev_section.get(original_text) is not None:
                translated = prev_section.get(original_text)
            # If variable unchanged and prev translation available, copy it  
            elif prev_row is not None and col in prev_row and prev_row.get(col) is not None:
                translated = prev_row.get(col)
            else:            
                translated = do_translate(original_text)

            df_final.at[idx, col] = translated
        filled = int(100 * idx / total_vars)
        bar = '#' * filled + '.' * (100 - filled)
        sys.stdout.write(f"\rProgress: [{bar}] {idx*100/total_vars:.0f}%")
        sys.stdout.flush()
        time.sleep(0.5)

    df_final.to_csv(os.path.join(arch_dir_path_des_dir, filename), index=False)
    print("****ARCH " + lang[0] + " Finished******")
    print(f"Total vars found in previous translations vs total translated variables: {total_vars_found_prev}/{total_vars}")
    print(f"ARCH Translation complete. Output saved to {arch_dir_path_des_dir}/{filename}")
    print("**********")
    return (total_vars_found_prev, total_vars)