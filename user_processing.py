import logging
from password_utils import generate_random_password

def process_user_data(row):
  """
  Processes a row of data from the Excel file to generate user data.

  Args:
      row (pandas.Series): A row from the pandas DataFrame.

  Returns:
      dict: Dictionary containing user data.
  """
  try:
      # Extract relevant data from the row
      user_data = {
          "accountEnabled": True,
          "displayName": f"{row['First Name']} {row['Last Name']}",
          "mailNickname": row['Last Name'].lower(),
          'givenName': row['First Name'],
          "surname": row['Last Name'],
          "userPrincipalName": row['Official Mail ID'],
          "jobTitle": row['Team'],
          "passwordProfile": {
              "forceChangePasswordNextSignIn": True,
              "password": generate_random_password()
          },
          'usageLocation': 'IN',  # Update with the appropriate value
          # ... (Add other user data fields as needed)
      }
      logging.info(f"Processed user data for: {row['Official Mail ID']}")
      return user_data
  except Exception as e:
      logging.error(f"Error processing user data for row: {row.to_string()}")
      logging.error(f"Error: {e}")
      return None
