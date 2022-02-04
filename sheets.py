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
SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1yL7FYxyUF4K1YpE5BYfLM0D3v8XdaRTDMkvy9XgKar8'
SAMPLE_RANGE_NAME = 'A1:CS97'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name('seating-340219-e34d940a0875.json', SCOPES)
    gc = gspread.authorize(creds)
        
    try:
        with open('seating-340219-e34d940a0875.json') as json_file:
            cred_file = json.load(json_file)
            # Open a sheet from a spreadsheet in one go
            wks = gc.open_by_url(cred_file.get("edit_link")).sheet1.get_values()

            if not wks:
                print('No data found.')
                return

            cell_count = 0
            for i in wks:
                print(len(i))
                cell_count += len(i)
            
            print(cell_count)
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()