
import pandas as pd


def get_traffic_combos(df, frac):

    df = df.sample(frac = frac)

    combos = []
    for index, row in df.iterrows():
        r = list(row[df.columns])
        if (r.count('#') > 1):
            combo = [int(ind) for ind in row.index if row[ind] == '#']
            if combo not in combos:
                combos.append(combo)

    return combos


print(get_traffic_combos(pd.read_csv('BOS210.csv', sep=';', low_memory=False), 0.2))