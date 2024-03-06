# main.py
import datetime as dt
import os
import pandas as pd
import requests
import logging
from microsoft_graph_api import get_access_token, get_all_users, user_exists, assign_license, create_user_and_assign_license
from email_utils import send_email
from yopass_api import Yopass
from processing_script import process_excel_data
from user_processing import process_user_data

# Configure logging
logging.basicConfig(filename='user_onboarding.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomYopass(Yopass):
    def secret_url(self, secret_id, password):
        base_url = super().secret_url(secret_id, password)
        return base_url.replace("api.", "")

def download_file(download_url, filename):
    download_response = requests.get(download_url)
    if download_response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(download_response.content)
        #print("File downloaded successfully as:", filename)
        logging.info(f"File downloaded successfully as: {filename}")
        return filename
    else:
        #print("Failed to download the file. Status code:", download_response.status_code)
        logging.error(f"Failed to download the file. Status code: {download_response.status_code}")
        return None

          
if __name__ == "__main__":
    client_id = "5356125c-ca72-476f-8c96-8e18eaddacc5"
    client_secret = "j1B8Q~5_pI6_bQAeNB0FVRfwosnvsd4wdpzQSbC1"
    resource = "https://graph.microsoft.com"

    access_token = get_access_token(client_id, client_secret, resource)

    if access_token:
        
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        url = "https://graph.microsoft.com/v1.0/drives/b!Hae9ETHH_kqMwUrYYyznCnvRZkU7zfNOrDI7A_0AlDGPctFFZCmvTpgdEBW_dk7b/root:/CD HRD/HR Operations/On & Off Boarding/Onboarding Checklist - 2024.xlsx"
        all_users = get_all_users(access_token)
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(data)
            download_url = data.get('@microsoft.graph.downloadUrl')
            print(download_url)
            filename = "downloaded_file.xlsx"  # Adjust the filename and extension as needed
            downloaded_filename = download_file(download_url, filename)
            if downloaded_filename:
                file_path = downloaded_filename
                if all_users:
                    total_users = len(all_users)
                    print(f"Total Users: {total_users}")
                    
                    # Read user data from the SecOps_Inventory_list.xlsx file
                    updated_data_df= process_excel_data(file_path, 'Candidate details to create IT credentails', 'Expected DoJ (DD/MM/YYYY)', 'Status')
                    
                    # Get the current date and time
                    current_date = dt.datetime.now().date()
                    print(current_date)
                    # Iterate over each row in the user data
                    for index, row in updated_data_df.iterrows():  # Assuming 'updated_data_df' is the DataFrame from processed data
                        new_user = process_user_data(row)

                        license_sku_id = '3b555118-da6a-4418-894f-7df1e2096870'  # Replace with the appropriate license SKU ID

                        # Move the receiver_email assignment here
                        receiver_email = new_user['userPrincipalName']
                        
                        # Extract the "Date of Joining" value and convert it to a datetime object
                        date_of_joining = row['Date of Joining'].date() if pd.notna(row['Date of Joining']) else None

                        # Check if "Date of Joining" is equal to the current date
                        if date_of_joining and date_of_joining == current_date:
                            if user_exists(new_user, all_users):
                                logging.info(f"The user {new_user['userPrincipalName']} already exists. Sending an email.")
                                # ... (rest of the email sending logic)
                                logging.info("The new user already exists. Sending an email.")
                                email_body = f"""<html>
            <head></head>
            <body>
                <p>Hi Team,</p>
                
                <p>I trust this message finds you well.</p>

                <p>It appears that the user for whom you requested the creation of an official email ID already exists with the email address 
                {new_user['userPrincipalName']}.</p>
                
                <p>Please provide an alternative email ID for the user, and we will be happy to assist you further.</p>

                <p>Thank you for your understanding.</p>

                <p>Regards,<br/>
                CD-Security</p>
            </body>
            </html>
            """
                                send_email("User Already Exists", email_body,"kishoreb@clouddestinations.com")
                            else:
                                logging.info(f"The user {new_user['userPrincipalName']} does not exist. Creating the new user and sending an email.")
                                if create_user_and_assign_license(access_token, new_user, license_sku_id):
                                    
                                    # Generate passphrase using Yopass
                                    yopass = CustomYopass(api="https://api.yopass.se")
                                    passphrase = yopass.generate_passphrase(length=12)  # Adjust the length as needed

                                    # Store the passphrase using Yopass
                                    secret_id = yopass.store(message=new_user['passwordProfile']['password'],
                                                            password=passphrase,
                                                            expiration="1d",
                                                            one_time=False)

                                    # Get the secret URL from Yopass
                                    secret_url = yopass.secret_url(secret_id=secret_id, password=passphrase)
                                    logging.info("Sending an email for successful user creation.")
                                    login_id = new_user['userPrincipalName']
                                    # Update the email template with the generated password
                                    email_body = f"""<html>
            <head></head>
            <body>
                <p>Hi {new_user['givenName']},</p>
                
                <p>Good Day, Welcome to Cloud Destinations!</p>

                <p>Please find your Outlook login credentials below:</p>

                <p><strong>Login Id:</strong> <a href=https://www.microsoft365.com/?auth=2&login_hint={login_id}&from=AdminCenterEmail>Outlook Login ID</a></p>
                

                <p><strong>Password:</strong> <a href="{secret_url}" target="_blank">Outlook Login Password</a></p>
                

                <p>The password is provided through encrypted communication and is only accessible for one day. 
                Please ensure to copy the password before the link expires.</p>

                <p>Thank you!</p>

                <p>Regards,<br/>
                CD-Security</p>
            </body>
            </html>
            """
                                    send_email("User Created", email_body, new_user['userPrincipalName'])
                                    #send_email("User Created", email_body, "kishoreb@clouddestinations.com")
                                    # Update the "Status" column to "Created" after user creation
                                    updated_data_df.at[index, 'Status'] = 'Created'
                                    # Save the updated DataFrame to the Excel file
                                    updated_data_df.to_excel('downloaded_file.xlsx', index=False)
                                else:
                                    logging.info("Not sending an email due to an error during user creation.")
                        else:
                            logging.info(f"The user {new_user['userPrincipalName']} is not scheduled for creation today.")
                            
                    
                    # Delete the SecOps_Inventory_list.xlsx file after processing
                    os.remove('SecOps_Inventory_list.xlsx')
                    logging.info("SecOps_Inventory_list.xlsx has been deleted.")
                else:
                    logging.info("Failed to retrieve user data.")
            else:
                logging.info("Unable to proceed with processing due to download failure.")
            os.remove('downloaded_file.xlsx')
        else:
            logging.info("Failed to retrieve file information. Status code:", response.status_code)
    else:
        logging.info("Failed to obtain access token.")

