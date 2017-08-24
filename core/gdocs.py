import gspread
from oauth2client.service_account import ServiceAccountCredentials

from settings import GDOCS_CREDENTIALS_PATH
from settings import GDOCS_TABLE_NAME


class GDocs:

    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.client = None

    def connect(self):
        # use creds to create a client to interact with the Google Drive API
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            GDOCS_CREDENTIALS_PATH, self.scope)
        self.client = gspread.authorize(creds)

    def _get_sheet(self):
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        return self.client.open(GDOCS_TABLE_NAME).sheet1

    def jobs_keywords(self):
        keywords = {}
        sheet = self._get_sheet()
        for kws in sheet.get_all_records():
            for keyword, value in kws.items():
                keywords.setdefault(keyword, [])
                keywords[keyword].append(value)

        return keywords
