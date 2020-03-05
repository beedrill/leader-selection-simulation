import pandas as pd
import plotly.express as px
import os
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file_name", help="csv file")
args = parser.parse_args()

df = pd.read_csv(args.file_name, index_col = 0)
plt.plot(df)
plt.show()