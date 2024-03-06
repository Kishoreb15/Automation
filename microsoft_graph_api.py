import logging
import requests

def get_access_token(client_id, client_secret, resource):
  """
  Obtains an access token from Microsoft Identity Platform.

  Args:
      client_id (str): Client ID for your application.
      client_secret (str): Client secret for your application.
      resource (str): Resource URI for which you request access.

  Returns:
      str: Access token on success, None on failure.
  """
  url = "https://login.microsoftonline.com/931efe0d-98f1-41f3-90f5-3aece03983a5/oauth2/token"
  payload = {
      'grant_type': 'client_credentials',
      'client_id': client_id,
      'client_secret': client_secret,
      'resource': resource
  }

  try:
      response = requests.post(url, data=payload)
      response.raise_for_status()  # Raise an exception for HTTP errors
      access_token = response.json().get('access_token')
      logging.info(f"Access token obtained successfully.")
      return access_token
  except requests.exceptions.RequestException as e:
      logging.error(f"Error occurred during request for access token: {e}")
      return None

def get_all_users(access_token):
  """
  Retrieves a list of users from Microsoft Graph.

  Args:
      access_token (str): Access token for Microsoft Graph API.

  Returns:
      list: List of user dictionaries, empty list on failure.
  """
  if access_token:
      headers = {
          'Authorization': 'Bearer ' + access_token
      }
      url = "https://graph.microsoft.com/v1.0/users"
      users = []

      while url:
          try:
              response = requests.get(url, headers=headers)
              response.raise_for_status()
              data = response.json()
              users += data.get('value', [])
              url = data.get('@odata.nextLink', None)
          except requests.exceptions.HTTPError as e:
              logging.error(f"Error occurred during request to get users: {e}")
              break

      return users
  else:
      logging.warning("Failed to obtain access token. Unable to retrieve users.")
      return []

def user_exists(new_user, all_users):
  """
  Checks if a user with the specified user principal name exists.

  Args:
      new_user (dict): Dictionary containing user data.
      all_users (list): List of user dictionaries.

  Returns:
      bool: True if the user exists, False otherwise.
  """
  return any(user.get('userPrincipalName', '') == new_user.get('userPrincipalName', '') for user in all_users)

def assign_license(access_token, user_id, license_sku_id):
  """
  Assigns a license to a user in Microsoft Graph.

  Args:
      access_token (str): Access token for Microsoft Graph API.
      user_id (str): ID of the user to assign the license to.
      license_sku_id (str): SKU ID of the license to assign.
  """
  headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
  }
  url = f"https://graph.microsoft.com/v1.0/users/{user_id}/assignLicense"

  license_assignment_payload = {
      "addLicenses": [
          {
              "skuId": license_sku_id
          }
      ],
      "removeLicenses": []
  }

  try:
      response = requests.post(url, headers=headers, json=license_assignment_payload)
      response.raise_for_status()
      logging.info(f"License assigned successfully to user: {user_id}")
  except requests.exceptions.HTTPError as e:
      logging.error(f"Error occurred during license assignment: {e}")
      logging.error(f"Response content: {response.content}")

def create_user_and_assign_license(access_token, new_user, license_sku_id):
  """
  Creates a new user and assigns a license in Microsoft Graph.

  Args:
      access_token (str): Access token for Microsoft Graph API.
      new_user (dict): Dictionary containing user data.
      license_sku_id (str): SKU ID of the license to assign.

  Returns:
      bool: True on success, False on failure.
  """
  headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
  }
  url = "https://graph.microsoft.com/v1.0/users"

  try:
      response = requests.post(url, headers=headers, json=new_user)
      response.raise_for_status()
      created_user = response.json()
      logging.info(f"User created successfully: {created_user.get('userPrincipalName')}")

      # Assign license to the newly created user
      assign_license(access_token, created_user['id'], license_sku_id)

      return True
  except requests.exceptions.HTTPError as e:
      logging.error(f"Error occurred during user creation: {e}")
      logging.error(f"Response content: {response.content}")
      return False
  

