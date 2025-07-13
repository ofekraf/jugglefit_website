from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pylib.classes.prop import Prop
from pylib.classes.trick import Trick
from pylib.configuration.bot_consts import JUGGLEFIT_BOT_CREDS, TRICK_SUGGESTIONS_SPREADSHEET_ID
from pylib.utils.general import quote_string


def append_trick_suggestion(*, prop: Prop, trick: Trick) -> None:
    """Appends a trick suggestion to the Google Sheet.
    
    Args:
        prop: The prop type for the trick
        trick: The trick to add
    """
    try:
        tags_csv = quote_string('|'.join(tag.value for tag in trick.tags) if trick.tags is not None else '')
        csv_row = [
            quote_string(trick.name),
            str(trick.props_count),
            str(trick.difficulty),
            quote_string(trick.comment if trick.comment else ''),
            tags_csv
        ]
        csv_row_str = ','.join(csv_row)
        values = [csv_row + [csv_row_str]]

        # Use the Google Sheets API v4 endpoint
        append_row_to_sheet(
            spreadsheet_id=TRICK_SUGGESTIONS_SPREADSHEET_ID,
            range_name=prop.name,
            values_to_append=values
        )
        
    except Exception as e:
        raise 
    

def append_row_to_sheet(*, spreadsheet_id, range_name, values_to_append):
    """
    Appends a new row of data to a Google Sheet using Service Account authentication.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        range_name (str): The A1 notation of the range to append values to.
        values_to_append (list): A list of lists, where each inner list is a row.
                                  For adding a single row, it will be [[value1, value2, ...]].
    """
    try:
        service = build('sheets', 'v4', credentials=JUGGLEFIT_BOT_CREDS)

        value_input_option = 'RAW' # Or 'USER_ENTERED'
        insert_data_option = 'INSERT_ROWS'

        body = {
            'values': values_to_append
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=body
        ).execute()
    except HttpError as err:
        raise
    except Exception as e:
        raise