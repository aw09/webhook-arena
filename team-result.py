import pandas as pd

def replace_newline_with_space(cell):
    if isinstance(cell, str):
        return cell.replace("\n", " ")
    return cell
def generate_caption(row):
    rank = row['Rank']
    weight_class = row['Weight Class']
    weight = weight_class.split(' ')[-2]  # Extract the weight value from the weight class string
    rank = 3 if rank == 4.0 or rank == 'DSQ' else rank

    prefix = f'JUARA {int(rank)}'

    if 'FS' in weight_class:
        return f'{prefix} KELAS {weight}KG GAYA BEBAS KADET'
    elif 'GR' in weight_class:
        return f'{prefix} KELAS {weight}KG GAYA BEBAS PEMULA'
    elif 'WW' in weight_class:
        return f'{prefix} KELAS {weight}KG GULAT PUTRI'


# Mapping from table to weight
table_to_weight = {
    "Table 1": "FS - 50 kg",
    "Table 2": "FS - 55 kg",
    "Table 3": "FS - 75 kg",
    "Table 4": "GR - 25 kg",
    "Table 5": "GR - 33 kg",
    "Table 6": "GR - 34 kg",
    "Table 7": "GR - 35 kg",
    "Table 8": "GR - 38 kg",
    "Table 9": "GR - 40 kg",
    "Table 10": "GR - 44 kg",
    "Table 11": "GR - 45 kg",
    "Table 12": "GR - 55 kg",
    "Table 13": "GR - 58 kg",
    "Table 14": "GR - 70 kg",
    "Table 15": "GR - 90 kg",
    "Table 16": "WW - 50 kg",
    "Table 17": "WW - 55 kg"
}

# Initialize an empty DataFrame to hold the combined data
combined_df = pd.DataFrame()

# Read Excel file
xl = pd.ExcelFile('/home/agung/Downloads/AllRanking.xlsx')  # Replace with the actual Excel file path

# Loop over each sheet in the Excel file
for sheet_name in xl.sheet_names:
    # Read each sheet into a DataFrame
    df = xl.parse(sheet_name).iloc[:5]
    df = df.applymap(replace_newline_with_space)

    # Add a 'Weight Class' column based on the mapping
    df['Weight Class'] = table_to_weight.get(sheet_name, 'Unknown')
    
    # Append the DataFrame to the combined DataFrame
    combined_df = pd.concat([combined_df, df])

# Close the Excel file
xl.close()

# Show the combined DataFrame
print(combined_df)
combined_df.to_csv('combined_df.csv')


# Create a new DataFrame containing only the specified columns
filtered_df = combined_df[['Rank', 'Team', 'Wrestler', 'Weight Class']]

# Group by 'Team' and store it as a new DataFrame
grouped_df_list = []

for name, group in filtered_df.groupby('Team'):
    grouped_df_list.append(group)

# Combine the grouped DataFrames into a single DataFrame
grouped_df = pd.concat(grouped_df_list).reset_index(drop=True)
grouped_df['Caption'] = grouped_df.apply(generate_caption, axis=1)
# Show the grouped DataFrame
print(grouped_df)
grouped_df.to_csv('grouped_df.csv')

unique_teams = grouped_df['Team'].unique()

# Convert it to a Python list, if needed
unique_teams_list = list(unique_teams)

print("List of Unique Teams:")
print("\n".join(unique_teams_list))


