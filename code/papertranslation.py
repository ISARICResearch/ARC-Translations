import time
import pandas as pd
from deep_translator import (GoogleTranslator, PonsTranslator, ChatGptTranslator)
import sys
import os
##archtranslation_v2.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang, arc_translated_file, arch_dir_path_prev)
def translate_paper(file_path, columns_df, arch_dir_path_des, lang, prev_translation_path=None, arch_dir_path_prev=None):
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
        print("File already created: "+filename)
        return (0, 0) #skip translation for this file
    
    df = pd.read_csv(file_path, sep=',')
    # Prepare output df: for ARCH.csv behavior was to overwrite the original columns with translations.
    df_final = df.copy()
    # prepare destination folder for this language
    try:
        os.makedirs(arch_dir_path_des, exist_ok=True)
        arch_dir_path_des_dir = os.path.join(arch_dir_path_des, lang[0]) + os.sep
        os.makedirs(arch_dir_path_des_dir, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {arch_dir_path_des_dir}: {e}")

    # Load previous translations if provided
    ###pending
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
        #print("Variable a traducir: "+var+" porque 1) es nueva o sufrió cambios de contenido o 2) no hay traducción previa: ")
        for col in columns_df:
            original_text = row.get(col, '')
            translated = do_translate(original_text)
            df_final.at[idx, col + "_translation"] = translated
        filled = int(10 * idx / total_vars)
        bar = '#' * filled + '.' * (10 - filled)
        sys.stdout.write(f"\rProgress: [{bar}] {idx*100/total_vars:.0f}%")
        sys.stdout.flush()

    df_final.to_csv(os.path.join(arch_dir_path_des_dir, filename), index=False)
    print("****Paper like " + lang[0] + "Finished******")
    print(f"Total vars found in previous translations vs total translated variables: {total_vars_found_prev}/{total_vars}")
    print(f"Paper like file Translation complete. Output saved to {arch_dir_path_des_dir}/{filename}")
    print("**********")
    return (total_vars_found_prev, total_vars)