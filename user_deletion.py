from microsoft_graph_api import get_access_token, get_user_id, delete_user
import pandas as pd

def delete_users(access_token, users_to_delete):
    for user_principal_name in users_to_delete:
        user_id = get_user_id(access_token, user_principal_name)
        if user_id:
            delete_user(access_token, user_id)
            print(f"User {user_principal_name} has been deleted.")
        else:
            print(f"User {user_principal_name} not found.")

if __name__ == "__main__":
    client_id = ""
    client_secret = ""
    resource = "https://graph.microsoft.com"

    # Get access token
    access_token = get_access_token(client_id, client_secret, resource)

    if access_token:
        # Example list of users to delete (replace with your actual userPrincipalNames)
        users_to_delete = ['testuser@clouddestinations.com']

        # Delete users
        delete_users(access_token, users_to_delete)
    else:
        print("Failed to obtain access token.")
