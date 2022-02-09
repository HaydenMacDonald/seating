from __future__ import print_function
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1yL7FYxyUF4K1YpE5BYfLM0D3v8XdaRTDMkvy9XgKar8"
SAMPLE_RANGE_NAME = "A1:CS97"

def sheets():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name("seating-340219-e34d940a0875.json", SCOPES)
    gc = gspread.authorize(creds)
        
    try:
        with open("seating-340219-e34d940a0875.json") as json_file:
            cred_file = json.load(json_file)
            # Open a sheet from a spreadsheet in one go
            wks = gc.open_by_url(cred_file.get("edit_link")).sheet1.get_values()

            if not wks:
                print("No data found.")
                return

            data = clean_distance_matrix(wks)

            return data
    
    except HttpError as err:
        print(err)


def clean_distance_matrix(matrix):
    # Create result dict
    result = {}
    
    # For each list in list of lists (matrix), store the name of the guest in indices list (if not empty string or None or 'NA')
    indices = [item[0] for item in matrix if item[0] != "" and item[0] != None and item[0] != 'NA']
    print(f"Processing data for {len(indices)} attendees\n")

    # Assign indices array to indices property in result dict
    result["indices"] = indices

    # Extract row data only
    rows = matrix[1:]

    # Use same logic as above to remove name indices from lists
    distances = [ [j for j in i if j != "" and j != None and j != 'NA'][1:] for i in rows]
    distances = [[float(j) for j in i] for i in distances]

    # Check that the number of attendees squared equals the number of relationship scores, else return
    sum = 0
    for i in distances:
        sum += len(i)

    if sum / len(indices) == len(indices):
        print(f"Successfully cleaned {sum} relationship scores mapped across {len(indices)} attendees\n")
    else:
        raise ValueError(f"Data not cleaned properly: {sum} relationship scores mapped across {len(indices)} attendees")
        return

    # Assign distances list of lists to distance_matrix property in result dict
    result["distance_matrix"] = distances

    # Assign meta variables, the following are defaults for TSP problem
    result['num_vehicles'] = 1
    result['depot'] = 0
    result['pickups_deliveries'] = [
        [29, 0], # Teresa to Beth
        [5, 29], # Susan to Teresa
        [6, 5], # Andrew to Susan
        [0, 1], # Beth to Hayden
        [1, 4], # Hayden to Jansen
        [4, 2], # Jansen to Mom
        [2, 3] # Mom to Brian
    ]

    return result


    
if __name__ == "__main__":
    sheets()