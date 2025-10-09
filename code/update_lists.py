import os
import pandas as pd

# === CONFIGURACIÓN ===
BASE_DIR = r"C:\Users\sduquevallejo\Documents\GitHub\ARC-Translations\ARCH1.1.3"
ENG_ROOT = os.path.join(BASE_DIR, "English", "Lists")
LANGS = ["Spanish", "French", "Portugues"]
ENCODING = "utf-8"
DRY_RUN = False  # Pon True para probar sin sobrescribir

REVIEW_COLS = [
    "Language Speaker Reviewed",
    "Clinical Language Speaker Reviewed",
]

# === UTILIDADES ===
def read_csv_utf8(path):
    df = pd.read_csv(path, dtype=str, encoding=ENCODING)
    return df.fillna("")  # nunca NaN

def ensure_parent_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

# === PROCESO PRINCIPAL ===
for lang in LANGS:
    lang_root = os.path.join(BASE_DIR, lang, "Lists")
    todo_rows = []

    for root, _, files in os.walk(ENG_ROOT):
        for fname in files:
            if not fname.lower().endswith(".csv"):
                continue

            eng_csv = os.path.join(root, fname)
            rel = os.path.relpath(eng_csv, ENG_ROOT)
            lang_csv = os.path.join(lang_root, rel)

            # --- Cargar English ---
            try:
                df_eng = read_csv_utf8(eng_csv)
            except Exception as e:
                print(f"[{lang}] ERROR leyendo ENG {rel}: {e}")
                continue

            if "Value" not in df_eng.columns:
                print(f"[{lang}] WARNING: {rel} no tiene columna 'Value' en English. Se omite.")
                continue
            if df_eng.shape[1] < 2:
                print(f"[{lang}] WARNING: {rel} tiene menos de 2 columnas; se omite.")
                continue

            df_eng = df_eng.apply(lambda s: s.astype(str).str.strip()).fillna("")

            eng_first_col = df_eng.columns[0]
            value_col = "Value"

            # columnas de ENG que hay que reemplazar
            eng_replace_cols = [c for c in df_eng.columns if c.startswith("preset_") or c.startswith("Selected")]

            # --- Cargar idioma ---
            if os.path.exists(lang_csv):
                try:
                    df_lang = read_csv_utf8(lang_csv)
                    df_lang = df_lang.apply(lambda s: s.astype(str).str.strip()).fillna("")
                except Exception as e:
                    print(f"[{lang}] ERROR leyendo {rel}: {e}")
                    continue
            else:
                df_lang = pd.DataFrame(columns=[eng_first_col, value_col])

            lang_first_col = df_lang.columns[0] if len(df_lang.columns) > 0 else eng_first_col
            if value_col not in df_lang.columns:
                df_lang[value_col] = ""

            # asegurar columnas de revisión
            for rc in REVIEW_COLS:
                if rc not in df_lang.columns:
                    df_lang[rc] = ""

            # --- Mapear por Value ---
            map_first = dict(zip(df_lang[value_col], df_lang[lang_first_col]))
            map_reviews = {rc: dict(zip(df_lang[value_col], df_lang[rc])) for rc in REVIEW_COLS}

            # --- Construir salida ---
            out = pd.DataFrame()
            # primera columna
            out[lang_first_col] = df_eng[value_col].map(map_first).fillna("")
            # columnas de reemplazo desde English
            for c in eng_replace_cols:
                out[c] = df_eng[c]
            # columnas que se conservan del idioma (todas las demás excepto las de reemplazo)
            for c in df_lang.columns:
                if c not in [lang_first_col, value_col] + REVIEW_COLS and not (c.startswith("preset_") or c.startswith("Selected")):
                    out[c] = df_lang[value_col].map(dict(zip(df_lang[value_col], df_lang[c]))).fillna("")
            # columna Value
            out[value_col] = df_eng[value_col]
            # columnas de revisión
            for rc in REVIEW_COLS:
                out[rc] = df_eng[value_col].map(map_reviews[rc]).fillna("")

            # --- Detectar nuevos Value ---
            lang_values = set(df_lang[value_col]) if value_col in df_lang.columns else set()
            eng_values = set(df_eng[value_col])
            new_values = sorted(v for v in eng_values if v not in lang_values)

            if new_values:
                for v in new_values:
                    todo_rows.append({
                        "Language": lang,
                        "RelativePath": rel.replace("\\", "/"),
                        "Value": v,
                        "Note": "Nuevo en English. Falta traducir la primera columna."
                    })

            # --- Guardar ---
            if not DRY_RUN:
                ensure_parent_dir(lang_csv)
                try:
                    out.to_csv(lang_csv, index=False, encoding=ENCODING)
                    print(f"[{lang}] Actualizado: {rel}")
                except Exception as e:
                    print(f"[{lang}] ERROR escribiendo {rel}: {e}")
            else:
                print(f"[{lang}] (DRY_RUN) Actualizaría: {rel}")

    # === Guardar reporte de pendientes ===
    report_path = os.path.join(BASE_DIR, f"translation_todo_{lang}.csv")
    todo_df = pd.DataFrame(todo_rows, columns=["Language", "RelativePath", "Value", "Note"])
    if not DRY_RUN:
        todo_df.to_csv(report_path, index=False, encoding=ENCODING)
    print(f"[{lang}] Pendientes: {len(todo_df)} | {report_path}")
