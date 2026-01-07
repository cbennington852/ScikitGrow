import seaborn as sns
import pandas as pd

# Get a list of all available dataset names
dataset_names = sns.get_dataset_names()

print("Available Seaborn datasets:")
for name in dataset_names:
    print(f"* {name}")

# Example of loading a specific dataset (e.g., 'tips')
def view_set(thing_set):
    if thing_set in dataset_names:
        tips_data = sns.load_dataset(thing_set)
        print("\nSuccessfully loaded 'tips' dataset:")
        print(tips_data.head())
    else:
        print("\n'tips' dataset not available.")

view_set("car_crashes")

# Sets to gather. "we need about 6 of them"
sets_to_gather = ['iris' , 'tips' , 'diamonds' , 'car_crashes' ] # plus wine and random

for curr in sets_to_gather:
    df = sns.load_dataset(curr)
    df.to_csv(f"resources/{curr}.csv")