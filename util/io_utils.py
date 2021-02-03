import pandas as pd

def read_dataset_csv(dataset_files):
    dataframes = []
    for file in dataset_files:
        flows = pd.read_csv(file)
        dataframes.append(flows)
    return pd.concat(dataframes)
