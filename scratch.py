import pandas as pd
df = pd.read_csv('/Users/apple/Desktop/metro dav/backend/data/edges.csv')
if 'fare' in df.columns:
    df.drop(columns=['fare'], inplace=True)
df.to_csv('/Users/apple/Desktop/metro dav/backend/data/edges.csv', index=False)
print("Restored edges.csv")
