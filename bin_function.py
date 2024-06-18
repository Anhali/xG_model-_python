import pandas as pd
import numpy as np

def coords_to_bins(df, x_col, y_col, bins=(10, 10)):
    # Calculate bin edges
    x_edges = np.linspace(0, 100, bins[0] + 1)
    y_edges = np.linspace(0, 100, bins[1] + 1)
    
    # Convert coordinates to bins using pd.cut
    bin_x = pd.cut(df[x_col], x_edges, right=False, labels=np.arange(0, bins[0]))
    bin_y = pd.cut(df[y_col], y_edges, right=False, labels=np.arange(0, bins[1]))
    
    # Handle the edge case where x or y equals 100
    bin_x = bin_x.fillna(bins[0] - 1).astype(int)
    bin_y = bin_y.fillna(bins[1] - 1).astype(int)
    
    # Calculate the bin number
    bin_number = bin_x * bins[1] + bin_y

    
    return bin_number


data = {
    'x': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    'y': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
}
df = pd.DataFrame(data)

# Ajouter une colonne de bins au DataFrame
df['bin'] = coords_to_bins(df, 'x', 'y', bins=(10, 10))

print(df)







