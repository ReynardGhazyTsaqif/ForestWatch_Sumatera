import zipfile, pandas as pd
from pathlib import Path

# Ambil SATU ZIP provinsi sebagai sampel
zip_path = list(Path(r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Dataset\Dataset Provinsi").glob("*.zip"))[0]
print(f"ZIP: {zip_path.name}\n")

with zipfile.ZipFile(zip_path) as z:
    print("Isi ZIP:", z.namelist())
    
    for nama in z.namelist():
        if nama.endswith(".csv"):
            with z.open(nama) as f:
                df = pd.read_csv(f)
                print(f"\n--- {nama} ---")
                print(df.head(3))
                print("Kolom:", list(df.columns))