import pandas as pd
import glob
import os

def clean_csv(path):
    try:
        df = pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding='cp1252')
    except Exception as e:
        print(f'  Skip {path}: {e}')
        return False

    changed = False
    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].str.replace('\n', ' ', regex=False).str.replace('\r', ' ', regex=False)
            cleaned = cleaned.str.replace(r'  +', ' ', regex=True).str.strip()
            if not cleaned.equals(df[col]):
                changed = True
                df[col] = cleaned
    
    if changed:
        df.to_csv(path, index=False, encoding='utf-8', lineterminator='\n')
        print(f'  Cleaned: {os.path.basename(path)}')
    return changed

csv_files = glob.glob('*_directory_complete*.csv')
print(f'Checking {len(csv_files)} CSV files...')
cleaned_count = 0
for f in csv_files:
    if clean_csv(f):
        cleaned_count += 1

print(f'\nCleaned {cleaned_count} files.')
