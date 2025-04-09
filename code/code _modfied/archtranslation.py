import pandas as pd
import openai
import sys
import os

# Configura tu API key

def traducir_con_chatgpt(texto, idioma_destino):
    """
    Usa la API de OpenAI para traducir texto al idioma especificado.
    """
    if pd.isnull(texto) or len(texto) > 5000:
        return texto
    
    prompt = f"Translate the following English text to {idioma_destino}:\n\n{texto}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[ERROR] Fallo al traducir texto: {texto[:30]}... - {e}")
        return texto

def translate_arch(file_path, columns_df, arch_dir_path_des, lang):
    """
    Traduce columnas específicas de un archivo CSV usando la API de OpenAI.

    Args:
        file_path (str): Ruta del archivo CSV.
        columns_df (list): Lista de columnas a traducir.
        arch_dir_path_des (str): Ruta al directorio donde guardar el resultado.
        lang (tuple): Idioma destino en formato ("French", "fr").
    """
    filename = os.path.basename(file_path)
    df = pd.read_csv(file_path, sep=',')

    if filename == 'paper_like_details.csv':
        df_final = df
    elif filename == 'ARCH.csv':
        df_final = df[['Variable']]
        df_final = df[df_final.columns.union(columns_df, False)]

    for column_name in columns_df:
        column_name1 = column_name + "_translation" if filename == 'paper_like_details.csv' else column_name
        column_name2 = column_name

        #print(f"Translating column: {column_name2} → {column_name1} to {lang[0]}...")
        df_final[column_name1] = df_final[column_name2].apply(lambda x: traducir_con_chatgpt(x, lang[0]))

    # Agrega columnas vacías
    df_final['Language Speaker Reviewed'] = None
    df_final['Clinical Language Speaker Reviewed'] = None

    # Crea estructura de carpetas
    try:
        os.makedirs(arch_dir_path_des, exist_ok=True)
        arch_dir_path_des_dir = os.path.join(arch_dir_path_des, lang[0])
        os.makedirs(arch_dir_path_des_dir, exist_ok=True)
    except OSError as e:
        sys.exit(f"No se pudo crear el directorio {arch_dir_path_des_dir}: {e}")

    # Guarda el archivo traducido
    arch_file_path_des = os.path.join(arch_dir_path_des_dir, filename)
    df_final.to_csv(arch_file_path_des, index=False)
    print(f"✅ Traducción completa. Archivo guardado en: {arch_file_path_des}")
    print("**********")
