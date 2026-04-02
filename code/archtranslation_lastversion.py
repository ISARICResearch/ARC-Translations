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
    
    #print("Tamaño del prev_map: "+str(len(prev_map)))
    # Parse changes log if provided
    added_vars = set()
    content_changed_vars = set()
    rename_map = {}  # old -> new
    if changes_log_path and os.path.exists(changes_log_path):
        try:
            xl = pd.ExcelFile(changes_log_path)
            
            if 'Added Variables' in xl.sheet_names:
                added_df = pd.read_excel(xl, 'Added Variables', dtype=str).fillna('')
                # tolerant of different column names
                for c in ['Variable (New)', 'Variable']:
                    if c in added_df.columns:
                        added_vars.update(v for v in added_df[c].tolist() if v)
                        break
            if 'Content Changes' in xl.sheet_names:
                content_df = pd.read_excel(xl, 'Content Changes', dtype=str).fillna('')
                if 'Variable' in content_df.columns:
                    content_changed_vars.update(v for v in content_df['Variable'].tolist() if v)
            if 'Variable Replacements' in xl.sheet_names:
                repl_df = pd.read_excel(xl, 'Variable Replacements', dtype=str).fillna('')
                # try to detect the old/new column names (they include versions)
                cols = list(repl_df.columns)
                if len(cols) >= 2:
                    old_col, new_col = cols[0], cols[1]
                    for _, row in repl_df.iterrows():
                        old, new = row.get(old_col, ''), row.get(new_col, '')
                        if old and new:
                            rename_map[old] = new
        except Exception as e:
            # if reading log fails, fall back to translating everything (do not crash)
            print("Exception found trying to read changes log, Translate everything: "+str(e))
            added_vars = set()
            content_changed_vars = set()
            rename_map = {}

    vars_to_translate = set(added_vars) | set(content_changed_vars)
    #print("len of vars_to_translate: "+str(len((vars_to_translate)))) ##solo para pruebas
    
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
            # failed translator -> return original text
            return s

    
    # Build reverse rename map new->old for quick lookup of old variable given new variable
    new_to_old = {new: old for old, new in rename_map.items()}
    ##print("new_to_old: "+str(new_to_old)) ##solo para pruebas

    for idx, row in df_final.iterrows():
        #ux=input("Quiere continuar con la siguiente?")##solo para pruebas
        var = str(row.get('Variable', '')).strip()
        #print("Variable actual: "+var)
        if not var and filename != 'paper_like_details.csv':
            continue

        # For renamed variables: if previous translation exists for old var, copy all relevant columns
        if var in new_to_old:
            print("var in replacements of variables with another name: "+var)
            old_var = new_to_old[var]
            prev_row = prev_map.get(old_var)
            if prev_row is not None:
                for col in columns_df:
                    if filename == 'paper_like_details.csv':
                        df_final.at[idx, col + "_translation"] = prev_row.get(col + "_translation", prev_row.get(col, ''))
                    else:
                        # ARCH.csv behaviour: overwrite original column with translated value from prev
                        if col in prev_row and prev_row.get(col) is not None:
                            df_final.at[idx, col] = prev_row.get(col)
                continue  # done with this row

        # If variable unchanged and prev translation available, copy it
        if var not in vars_to_translate and prev_map.get(var) is not None:
            print("var que no sufrió cambios por lo que NO se traduce de nuevo: "+var)
            prev_row = prev_map[var]
            for col in columns_df:
                if filename == 'paper_like_details.csv':
                    # keep original col, add translation col from prev if exists, else leave blank
                    df_final.at[idx, col + "_translation"] = prev_row.get(col + "_translation", prev_row.get(col, ''))
                else:
                    # ARCH.csv: previous translations overwrite original column value
                    if col in prev_row and prev_row.get(col) is not None:
                        df_final.at[idx, col] = prev_row.get(col)
            continue

        # Otherwise, translate the required columns for this row
        print("Variable a traducir: "+var+" porque 1) es nueva o sufrió cambios de contenido o 2) no hay traducción previa: ")
        for col in columns_df:
            original_text = row.get(col, '')
            translated = do_translate(original_text)
            if filename == 'paper_like_details.csv':
                df_final.at[idx, col + "_translation"] = translated
            else:
                df_final.at[idx, col] = translated

    # Add review columns used previously
    df_final.loc[:, 'Language Speaker Reviewed'] = None
    df_final.loc[:, 'Clinical Language Speaker Reviewed'] = None
    arch_file_path_des = os.path.join(arch_dir_path_des_dir, filename)
    df_final.to_csv(arch_file_path_des, index=False)
    print(f"Translation complete. Output saved to {arch_file_path_des}")
    print("**********")