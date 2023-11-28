import os
import pandas as pd
import numpy as np
from datetime import datetime

# Specify the path to the directory containing files
directory_po = './out/getInventory'
directory_ci = './import/CI'
directory_out= './out/getCIProject'

try:
    os.makedirs(directory_ci)
    print(f"Directory '{directory_ci}' created.")
except FileExistsError:
    # Directory already exists
    pass

try:
    os.makedirs(directory_out)
    print(f"Directory '{directory_out}' created.")
except FileExistsError:
    # Directory already exists
    pass
# result ='result.xlsx'
def main ():
    # List all files in the specified directory
    files = [file for file in os.listdir(directory_po) if os.path.isfile(os.path.join(directory_po, file))]
    files2 = [file2 for file2 in os.listdir(directory_ci) if os.path.isfile(os.path.join(directory_ci, file2))]

    customer_name = input("Enter the customer name ? ")

    # Print the list of files
    print("List of files in the directory ProjectOne:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")
    # Get user input for file choice
    user_choice_po = input("Enter the number of the file Project One you want to open: ")

    print("List of files in the directory CI:")
    for i, file2 in enumerate(files2, start=1):
        print(f"{i}. {file2}")

    # Get user input for file choice
    user_choice_ci = input("Enter the number of the file CI you want to open: ")


    # Validate user input ProjectOne
    try:
        user_choice_po = int(user_choice_po)
        if 1 <= user_choice_po <= len(files):
            selected_file = files[user_choice_po - 1]
            file_path = os.path.join(directory_po, selected_file)
            df_po = pd.read_csv(file_path)
            print(df_po)
        else:
            print("Invalid choice. Please enter a valid number.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")

    # Validate user input CI
    try:
        user_choice_ci = int(user_choice_ci)
        if 1 <= user_choice_ci <= len(files2):
            selected_file = files2[user_choice_ci - 1]
            file_path2 = os.path.join(directory_ci, selected_file)
            df_ci = pd.read_excel(file_path2)
            print(df_ci)
        else:
            print("Invalid choice. Please enter a valid number.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")

    waktu = datetime.now().strfstime("%d-%m-%y_%H_%M_%S")
    NameFile ="out/getCIProject/Result_CIPO_" + customer_name + "_" + waktu +".xlsx"

    # Data Merge
    df_result = pd.merge(df_po,df_ci, left_on='SN',right_on='Serial Number',how='left')
    df_result = df_result.replace(np.nan, 'Data Tidak ada di CI')

    print(df_result)
    df_result.to_excel(NameFile)