import pandas as pd

df_header_index_col = pd.read_csv('learn_history_0_.csv', index_col=0)
print(df_header_index_col['calcAction'].values)

for i in df_header_index_col['calcAction'].values:
    print(i)