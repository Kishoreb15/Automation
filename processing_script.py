# processing_script.py
import os
import logging
import pandas as pd
from user_processing import process_user_data

def process_excel_data(file_path, column_name_1, column_name_2, status_column_name, output_file='SecOps_Inventory_list.xlsx'):
    # Initialize lists to store extracted values
    ids = []
    first_names = []
    last_names = []
    teams = []
    personal_mail_ids = []
    official_mail_ids = []
    additional_column_values_1 = []  # New list for the first additional column

    # Counter for generating unique IDs
    id_counter = 1

    # Iterate over each sheet in the Excel file
    for sheet_name in pd.ExcelFile(file_path).sheet_names:
        logging.info(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        selected_column_1 = df[column_name_1]
        selected_column_2 = df[column_name_2]
        status_column = df[status_column_name]  # Extract the Status column

        # Iterate over each row in the selected columns
        for row_1, row_2, status in zip(selected_column_1, selected_column_2, status_column):
            if pd.notna(status) and str(status).lower() == 'create' and isinstance(row_1, str):  # Check if the Status is 'create' and the value is a string
                # Initialize variables to store extracted values
                first_name = ""
                last_name = ""
                team = ""
                personal_mail_id = ""
                official_mail_id = ""

                lines = row_1.split('\n')

                for line in lines:
                    if line.startswith("First Name:"):
                        first_name = line.split(":")[1].strip()
                    elif line.startswith("Last Name:"):
                        last_name = line.split(":")[1].strip()
                    elif line.startswith("Team:"):
                        team = line.split(":")[1].strip()
                    elif line.startswith("Personal Mail ID:"):
                        personal_mail_id = line.split(":")[1].strip()
                    elif line.startswith("Official mail ID (to be created):"):
                        official_mail_id = line.split(":")[1].strip()

                # Append extracted values to respective lists
                ids.append(id_counter)
                first_names.append(first_name)
                last_names.append(last_name)
                teams.append(team)
                personal_mail_ids.append(personal_mail_id)
                official_mail_ids.append(official_mail_id)
                additional_column_values_1.append(row_2)  # Append value from the first additional column

                id_counter += 1  # Increment ID counter
            else:
                # Skip rows where the Status is not 'create' or empty rows
                continue

    # Create a new DataFrame with extracted columns
    new_data_df = pd.DataFrame({
        'ID': ids,
        'First Name': first_names,
        'Last Name': last_names,
        'Team': teams,
        'Personal Mail ID': personal_mail_ids,
        'Official Mail ID': official_mail_ids,
        'License': "Microsoft Business Basic",
        'Date of Joining': additional_column_values_1,  # Add the first additional column to the DataFrame
    })

    # If the output file exists, load it and check for duplicates
    if os.path.exists(output_file):
        existing_data_df = pd.read_excel(output_file)

        # Concatenate existing and new data, drop duplicates
        updated_data_df = pd.concat([existing_data_df, new_data_df]).drop_duplicates(subset=['Official Mail ID'], keep='last')
    else:
        updated_data_df = new_data_df  # If the output file doesn't exist, use the new data directly
        logging.info(f"Data has been created and named as '{output_file}'")

    updated_data_df.to_excel(output_file, index=False)

    #print(f"Data has been updated and saved to '{output_file}'")

    # Return the processed DataFrame
    return updated_data_df

# process_excel_data('./downloaded_file.xlsx', 'Candidate details to create IT credentails', 'Expected DoJ (DD/MM/YYYY)', 'Status')


