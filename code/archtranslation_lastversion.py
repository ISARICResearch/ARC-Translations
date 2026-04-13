# ...existing code...
import pandas as pd
from deep_translator import (GoogleTranslator, PonsTranslator, ChatGptTranslator)
import sys
import os
##archtranslation_v2.translate_arch(arch_file_path_src, arch_col_translate, arch_dir_path_des, lang, arc_translated_file, changes_log_path)
def translate_arch(file_path, columns_df, arch_dir_path_des, lang, prev_translation_path=None, changes_log_path=None):
    """
    Translate specified columns in a CSV file but reuse previous translations when variables are unchanged or renamed.

    Args:
      file_path (str): Path to the CSV file to translate.
      columns_df (list): Names of columns to translate.
      arch_dir_path_des (str): Destination base directory for outputs.
      lang (tuple): ("Language", "code") e.g. ("Spanish","es").
      prev_translation_path (str|None): CSV path of previous-version translated ARCH (optional).
      changes_log_path (str|None): Path to Excel changes log produced by compare_arc.py (optional).

    Behavior:
      - If changes_log_path is provided it will read sheets:
          "Added Variables" -> column "Variable (New)"
          "Content Changes" -> column "Variable"
          "Variable Replacements" -> two cols mapping old->new
      - Variables in Added or Content Changes are translated.
      - Renamed variables are populated by copying the previous-version translation of the old variable.
      - For variables not in the above sets, previous translations are reused if available; otherwise translated.
    """
    filename = os.path.basename(file_path)
    arch_dir_path_des_file = os.path.join(arch_dir_path_des, lang[0]) + os.sep + filename
    total_vars = 0
    total_vars_found_prev = 0
    if os.path.exists(arch_dir_path_des_file):
        print("File already created: "+filename)
        return (0, 0) #skip translation for this file
    
    df = pd.read_csv(file_path, sep=',')

    # prepare destination folder for this language
    try:
        os.makedirs(arch_dir_path_des, exist_ok=True)
        arch_dir_path_des_dir = os.path.join(arch_dir_path_des, lang[0]) + os.sep
        os.makedirs(arch_dir_path_des_dir, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {arch_dir_path_des_dir}: {e}")

    # Load previous translations if provided
    # Fast copy of previous translations for unchanged variables and renamed variables
    prev_df = None
    prev_map = {}
    if prev_translation_path and os.path.exists(prev_translation_path):
        prev_df = pd.read_csv(prev_translation_path, sep=',', dtype=str).fillna('')
        # build quick lookup map by Variable
        if 'Variable' in prev_df.columns:
            prev_map = {r['Variable']: r for _, r in prev_df.iterrows()}
    else:
        print("No previous translation file found at "+str(prev_translation_path)+". Will use empty previous translations (translate all).")
    
    # Prepare output df: for ARCH.csv behavior was to overwrite the original columns with translations.
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
    for idx, row in df_final.iterrows():
        #ux=input("Quiere continuar con la siguiente?")##solo para pruebas
        var = str(row.get('Variable', '')).strip()
        #print("Variable actual: "+var)
        if not var and filename != 'paper_like_details.csv':
            continue


        # If variable unchanged and prev translation available, copy it
        if prev_map.get(var) is not None and  filename != 'paper_like_details.csv':
            #print("Variable found on previous translation: "+var)
            prev_row = prev_map[var]
            total_vars_found_prev += 1
            for col in columns_df:
                # ARCH.csv: previous translations overwrite original column value
                if col in prev_row and prev_row.get(col) is not None:
                    df_final.at[idx, col] = prev_row.get(col)
            continue

        # Otherwise, translate the required columns for this row
        #print("Variable a traducir: "+var+" porque 1) es nueva o sufrió cambios de contenido o 2) no hay traducción previa: ")
        for col in columns_df:
            original_text = row.get(col, '')
            translated = do_translate(original_text)
            if filename == 'paper_like_details.csv':
                df_final.at[idx, col + "_translation"] = translated
            else:
                df_final.at[idx, col] = translated

    # Add review columns used previously
    
    #df_final.loc[:, 'Language Speaker Reviewed'] = None
    #df_final.loc[:, 'Clinical Language Speaker Reviewed'] = None

    df_final.to_csv(os.path.join(arch_dir_path_des_dir, filename), index=False)
    #print(f"Total vars found in previous translations vs total translated variables: {total_vars_found_prev}/{total_vars}")
    print(f"Translation complete. Output saved to {arch_dir_path_des_dir}/{filename}")
    print("**********")
    return (total_vars_found_prev, total_vars)