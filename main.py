import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3]})
# test retry
df.to_csv("./data/20230911.csv")