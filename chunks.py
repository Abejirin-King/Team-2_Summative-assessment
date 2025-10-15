import pandas as pd

rows = sum(1 for _ in open("cleaned_data.csv")) - 1  
print(f"Total rows: {rows}")
print(f"Estimated chunks: {rows // 5000 + 1}")
