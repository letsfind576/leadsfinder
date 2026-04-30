import pandas as pd
import numpy as np

# Load and clean the data
df = pd.read_csv('dashboard/public/data.csv')
print(f'Before cleaning: {len(df)} rows')

# Clean embedded newlines from all string columns
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.replace('\n', ' ', regex=False).str.replace('\r', ' ', regex=False).str.strip()

# Also clean any double spaces
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()

print(f'After cleaning: {len(df)} rows')

# Verify no more embedded newlines
for col in df.select_dtypes(include='object').columns:
    count = df[col].str.contains('\n', na=False).sum()
    if count > 0:
        print(f'WARNING: {col} still has {count} rows with newlines')

# Save back to data.csv
df.to_csv('dashboard/public/data.csv', index=False, encoding='utf-8', lineterminator='\n')
print('Saved cleaned data.csv')
print(f'Valid rows: {len(df[df["Company Name"].notna() & (df["Company Name"].str.strip() != "")])}')
