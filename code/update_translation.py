import os
import pandas as pd
import numpy as np

# Rutas
root_old = 'https://raw.githubusercontent.com/ISARICResearch/ARC/main'
root_trans = r'C:/Users/sduquevallejo/Documents/GitHub/ARC-Translations/ARCH1.1.0'
save_root = r'C:\Users\sduquevallejo\Documents\GitHub\ARC-Translations\ARCH1.1.2'

# Idiomas
lang = ['Spanish', 'French', 'Portuguese']

# Columnas de contenido
CONTENT_COLS = ['Form', 'Section', 'Question', 'Answer Options', 'Definition', 'Completion Guideline']

# Base ARC
df_base = pd.read_csv(root_old + '/ARC.csv')
required_cols = ['Variable'] + CONTENT_COLS
missing_in_base = [c for c in required_cols if c not in df_base.columns]
if missing_in_base:
    raise ValueError(f"Faltan columnas en ARC base: {missing_in_base}")

df_base = df_base[required_cols].copy()
os.makedirs(save_root, exist_ok=True)

for i in lang:
    # Traducción
    path_trans = f"{root_trans}/{i}/ARCH.csv"
    df_trans = pd.read_csv(path_trans)
    if 'Variable' not in df_trans.columns:
        raise ValueError(f"'{path_trans}' no contiene columna 'Variable'.")

    # Nos quedamos con Variable + columnas de contenido (si faltan, no pasa nada)
    trans_cols_present = ['Variable'] + [c for c in CONTENT_COLS if c in df_trans.columns]
    df_trans_min = df_trans[trans_cols_present].copy()

    # Merge con indicador para saber si la Variable existía en la traducción
    dfm = pd.merge(
        df_base.add_suffix('_base'),
        df_trans_min.add_suffix('_trans'),
        left_on='Variable_base',
        right_on='Variable_trans',
        how='left',
        indicator=True
    )

    # Flag de filas sin traducción (variable no está en df_trans)
    no_trans = (dfm['_merge'] == 'left_only')

    # Construir columnas finales:
    # - Si no hay traducción para esa Variable => usar *_base
    # - Si hay traducción => usar *_trans (aunque venga vacío)
    out = pd.DataFrame()
    out['Variable'] = dfm['Variable_base']
    for col in CONTENT_COLS:
        col_base = f"{col}_base"
        col_trans = f"{col}_trans"
        if col_trans not in dfm.columns:
            # si esa columna no existe en el archivo de traducción, créala vacía
            dfm[col_trans] = pd.NA
        out[col] = np.where(no_trans, dfm[col_base], dfm[col_trans])

    # needs_manual = 1 solo cuando la Variable no existía en df_trans
    out[f'{i}_needs_manual'] = no_trans.astype(int)

    # Guardar
    folder_path = os.path.join(save_root, i)
    os.makedirs(folder_path, exist_ok=True)
    save_path = os.path.join(folder_path, 'ARCH.csv')
    out.to_csv(save_path, index=False, encoding='utf-8-sig')

    print(f"Archivo mergeado y guardado en: {save_path}")
