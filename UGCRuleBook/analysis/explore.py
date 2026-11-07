
import pandas as pd
from app.records import load_records

records = load_records()

df = pd.DataFrame(records)

print("Total number of records:")
print(len(df))

print("\nRecords by year:")
print(df["year"].value_counts())

print("\nRecords by complaint authority:")
print(df["where_to_complain"].value_counts())
