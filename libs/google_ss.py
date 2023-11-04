import os
import calendar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from aiogram import types

from config_reader import myvars, DEBUG
from libs.dictanotry_lib import to_ru_month, to_ru_month2, column_by_id, to_ru_dayofweek


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_weekday_name_by_id(weekday):
    if weekday == 0:
        return "Понедельник"
    if weekday == 1:
        return "Вторник"
    if weekday == 2:
        return "Среда"
    if weekday == 3:
        return "Четверг"
    if weekday == 4:
        return "Пятница"
    if weekday == 5:
        return "Суббота"
    if weekday == 6:
        return "Воскресенье"


# def to_ru_month(month_name):
#     if month_name == 'January':
#         return 'Январь'
#     if month_name == 'February':
#         return 'Февраль'
#     if month_name == 'March':
#         return 'Март'
#     if month_name == 'April':
#         return 'Апрель'
#     if month_name == 'May':
#         return 'Май'
#     if month_name == 'June':
#         return 'Июнь'
#     if month_name == 'July':
#         return 'Июль'
#     if month_name == 'August':
#         return 'Август'
#     if month_name == 'September':
#         return 'Сентябрь'
#     if month_name == 'October':
#         return 'Октябрь'
#     if month_name == 'November':
#         return 'Ноябрь'
#     if month_name == 'December':
#         return 'Декабрь'
#
#
# def to_ru_month2(month_name):
#     if month_name == 'January':
#         return 'Января'
#     if month_name == 'February':
#         return 'Февраля'
#     if month_name == 'March':
#         return 'Марта'
#     if month_name == 'April':
#         return 'Апреля'
#     if month_name == 'May':
#         return 'Мая'
#     if month_name == 'June':
#         return 'Июня'
#     if month_name == 'July':
#         return 'Июля'
#     if month_name == 'August':
#         return 'Августа'
#     if month_name == 'September':
#         return 'Сентября'
#     if month_name == 'October':
#         return 'Октября'
#     if month_name == 'November':
#         return 'Ноября'
#     if month_name == 'December':
#         return 'Декабря'


def get_calendar_list(year: int, month: int):
    # now = dt.now()
    # curmonth = now.month
    # curyear = now.year
    # curday = now.day

    month_calendar = calendar.monthcalendar(year, month)
    week_count = 0
    calendar_as_list = []

    for week in month_calendar:

        day_list = []
        numbers_list = []
        # month_list = []
        t_10 = ["10.00-11.00"]
        t_11 = ["11.00-12.00"]
        t_12 = ["12.00-13.00"]
        t_13 = ["13.00-14.00"]
        t_14 = ["14.00-15.00"]
        t_15 = ["15.00-16.00"]
        t_16 = ["16.00-17.00"]
        blank_1 = [""]
        blank_2 = [""]
        day_list.append("")
        numbers_list.append("")
        # month_list.append("")
        weekday = 0
        for day in week:
            day_list.append(to_ru_dayofweek[weekday])
            weekday += 1
            if day == 0:
                numbers_list.append("")
                # month_list.append("")
                continue
            # month_list.append(to_ru_month(calendar.month_name[month]))
            numbers_list.append(f'{day} {to_ru_month2[calendar.month_name[month]]} {year}г.')
        # calendar_as_list.append(month_list)
        calendar_as_list.append(numbers_list)
        calendar_as_list.append(day_list)
        calendar_as_list.append(t_10)
        calendar_as_list.append(t_11)
        calendar_as_list.append(t_12)
        calendar_as_list.append(t_13)
        calendar_as_list.append(t_14)
        calendar_as_list.append(t_15)
        calendar_as_list.append(t_16)
        calendar_as_list.append(blank_1)
        calendar_as_list.append(blank_2)
        week_count += 1

    return calendar_as_list


async def get_or_create_credentials(scopes, callback: types.CallbackQuery):
    credentials = None
    # if os.path.exists("../cred/token.json"):
    if os.path.exists("cred/token.json"):
        credentials = Credentials.from_authorized_user_file("cred/token.json", scopes)
        # credentials = Credentials.from_authorized_user_file("../cred/token.json", scopes)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_secrets_file("../cred/credentials.json", scopes)
            flow = InstalledAppFlow.from_client_secrets_file("cred/credentials.json", scopes)
            # auth_url, _ = flow.authorization_url(prompt='consent')
            await callback.message.bot.send_message(chat_id=236829971, text=f'CREDENTIALS GOOGLE MEDBOT. URL FOR APPROVE AND REFRESH TOKEN')
            credentials = flow.run_local_server(port=0)
        # with open("../cred/token.json", "w") as token:
        with open("cred/token.json", "w") as token:
            token.write(credentials.to_json())
    return credentials


def create_sheet(service, title, spreadsheet_id):
    body = {
        "requests": {
            "addSheet": {
                "properties": {
                    "title": title
                }
            }
        }
    }

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def get_sheet_id(service, sheet_name, spreadsheet_id):
    sheets = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in sheets['sheets']:
        if sheet['properties']['title'] == sheet_name:
            sheet_id = sheet['properties']['sheetId']
            return sheet_id
    return None


def update_sheet(service, sheet_name, spreadsheet_id):
    sheet_id = get_sheet_id(service, sheet_name, spreadsheet_id)

    body = {
        'requests': [
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'index': 0
                    },
                    'fields': 'index',
                }
            }
        ]
    }
    print(f'sheet_id: {sheet_id}')
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def create_list(service, year, month, rrange, spreadsheet_id):
    # mylist = [["октябрь2023", "111", "222"], ["ноябрь2023"], ["ноябрь2023", 111, 222, 333]]
    mylist = get_calendar_list(year, month)
    # mylist.append("ноябрь2023")
    # print(mylist)
    resource = {
        "majorDimension": "ROWS",
        "values": mylist
    }
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=rrange,
        body=resource,
        valueInputOption="USER_ENTERED"
    ).execute()


def sheet_is_exist(service, sheet_name, spreadsheet_id):
    sheet_id = get_sheet_id(service, sheet_name, spreadsheet_id)
    if sheet_id is not None:
        return True
    else:
        return False


def formatting_sheet(service, sheet_name, spreadsheet_id):
    sheet_id = get_sheet_id(service, sheet_name, spreadsheet_id)

    body = {
        "requests": [
            {
                # Красит серым цветом время приема (первый столбец)
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 0,
                                "endColumnIndex": 1,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "NOT_BLANK",
                            },
                            "format": {
                                # "textFormat": {
                                #   "bold": True
                                # }
                                "backgroundColor": {
                                    "green": 0.85,
                                    "red": 0.85,
                                    "blue": 0.85,
                                }
                            }
                        }
                    },
                    "index": 0
                }
            },
            {
                # Красит фиолетовым цветом дату
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 11,
                                "endRowIndex": 12,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 22,
                                "endRowIndex": 23,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 33,
                                "endRowIndex": 34,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 44,
                                "endRowIndex": 45,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 55,
                                "endRowIndex": 56,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "NOT_BLANK",
                            },
                            "format": {
                                "textFormat": {
                                    "bold": True
                                },
                                "backgroundColor": {
                                    "green": 0.82,
                                    "red": 0.85,
                                    "blue": 0.91,
                                }
                            }
                        }
                    },
                    "index": 1
                }
            },
            {
                # Красит телесным цветом дни недели
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": 2,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 12,
                                "endRowIndex": 13,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 23,
                                "endRowIndex": 24,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 34,
                                "endRowIndex": 35,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 45,
                                "endRowIndex": 46,
                            },
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 56,
                                "endRowIndex": 57,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "NOT_BLANK",
                            },
                            "format": {
                                "textFormat": {
                                    "bold": True
                                },
                                "backgroundColor": {
                                    "green": 0.95,
                                    "red": 1.00,
                                    "blue": 0.80,
                                }
                            }
                        }
                    },
                    "index": 2
                }
            },
            {
                # Красит зелёным цветом ячейки не занятые записями
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 2,
                                "endRowIndex": 9,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 13,
                                "endRowIndex": 20,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 24,
                                "endRowIndex": 31,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 35,
                                "endRowIndex": 42,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 46,
                                "endRowIndex": 53,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 57,
                                "endRowIndex": 64,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "BLANK",
                            },
                            "format": {
                                # "textFormat": {
                                #   "bold": True
                                # }
                                "backgroundColor": {
                                    "red": 0.71,
                                    "green": 0.84,
                                    "blue": 0.66,
                                }
                            }
                        }
                    },
                    "index": 3
                }
            },
            {
                # Красит голубым цветом ячейки занятые записями
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 2,
                                "endRowIndex": 9,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 13,
                                "endRowIndex": 20,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 24,
                                "endRowIndex": 31,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 35,
                                "endRowIndex": 42,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 46,
                                "endRowIndex": 53,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 57,
                                "endRowIndex": 64,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [
                                    {
                                        "userEnteredValue": "closed"
                                    }
                                ]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.92,
                                    "green": 0.60,
                                    "blue": 0.60,
                                }
                            }
                        }
                    },
                    "index": 4
                }
            },
            {
                # Красит голубым цветом ячейки занятые записями
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 2,
                                "endRowIndex": 9,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 13,
                                "endRowIndex": 20,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 24,
                                "endRowIndex": 31,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 35,
                                "endRowIndex": 42,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 46,
                                "endRowIndex": 53,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 1,
                                "endColumnIndex": 6,
                                "startRowIndex": 57,
                                "endRowIndex": 64,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "NOT_BLANK",
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.62,
                                    "green": 0.77,
                                    "blue": 0.91,
                                }
                            }
                        }
                    },
                    "index": 5
                }
            },
            {
                # Красит серым цветом ячейки выходных
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 2,
                                "endRowIndex": 9,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 13,
                                "endRowIndex": 20,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 24,
                                "endRowIndex": 31,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 35,
                                "endRowIndex": 42,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 46,
                                "endRowIndex": 53,
                            },
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 6,
                                "endColumnIndex": 8,
                                "startRowIndex": 57,
                                "endRowIndex": 64,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "BLANK",
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.60,
                                    "green": 0.60,
                                    "blue": 0.60,
                                }
                            }
                        }
                    },
                    "index": 6
                }
            },
            # Выравнивает колонки по ширине
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 8
                    }
                }
            },
            # Ц
            {
                "repeatCell": {
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8,
                    },
                    "fields": "userEnteredFormat.horizontalAlignment, userEnteredFormat.verticalAlignment, userEnteredFormat.wrapStrategy"
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def get_id_by_value(service, title, spreadsheet_id, column_name):
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=spreadsheet_id, range=title).execute()

    values = result.get("values", [[]])
    i = 0
    for row in values:
        # print(row)
        j = 0
        for cell in row:
            if cell == column_name:
                # print(f'cell[{i},{j}] = {cell}')
                return i, j
            j += 1
        i += 1
    return None


def get_row_time_id(hour: str, row_id: int):
    if hour == '10':
        return row_id+3
    if hour == '11':
        return row_id+4
    if hour == '12':
        return row_id+5
    if hour == '13':
        return row_id+6
    if hour == '14':
        # res = int(row_id) + 6
        return row_id+7
    if hour == '15':
        return row_id+8
    if hour == '16':
        return row_id+9


async def google_get_vars(user_data: dict, callback: types.CallbackQuery):
    credentials = await get_or_create_credentials(SCOPES, callback)
    title = f"{to_ru_month[calendar.month_name[int(user_data['month'])]].lower()}{int(user_data['year'])}"
    service = build('sheets', 'v4', credentials=credentials)

    if DEBUG == 1:
        await create_next_month_calendar_bot(
            callback, myvars.doctors['Соболевский В.А.']['spreadsheet_id'],
            service,
            year=int(user_data['year']),
            month=int(user_data['month']),
            title=title)
    else:
        await create_next_month_calendar_bot(
            callback, user_data['spreadsheet_id'],
            service,
            year=int(user_data['year']),
            month=int(user_data['month']),
            title=title)

    sheets = service.spreadsheets()
    return service, sheets, title


async def update_cell(spreadsheet_id, hour, month, year, day, value, service, sheets, title):

    # print(f'month: {month}')
    # print(f'month_en: {calendar.month_name[month]}')
    # print(f'month_ru: {to_ru_month[calendar.month_name[month]].lower()}')

    # print(f'title: {title}')
    # print(f'spreadsheet_id: {spreadsheet_id}')

    try:
        # spreadsheet_id = SPREADSHEET_ID

        column_name = f'{day} {to_ru_month2[calendar.month_name[month]]} {year}г.'
        row_id, column_id = get_id_by_value(service, title, spreadsheet_id, column_name)
        # print(f'row_id: {row_id} column_id: {column_id}')
        row_id = get_row_time_id(str(hour), row_id)
        # print(f'row_id: {row_id} column_id: {column_id}')

        body = {'values': [[value]]}
        rrange = f'{title}!{column_by_id[column_id]}{row_id}'
        # rrange = f'{column_by_id[column_id]}{row_id}'
        # print(rrange)

        res = sheets.values().get(spreadsheetId=spreadsheet_id, range=rrange).execute()
        if "values" in res:
            if value == 'closed' or "opened" in value or "appt_cancel" in value:
                if "opened" in value:
                    value = value[6:]
                elif "appt_cancel" in value:
                    value = value[11:]
                # print("Try")
                body = {'values': [[value]]}
                result = sheets.values().update(spreadsheetId=spreadsheet_id, range=rrange,
                                                valueInputOption='USER_ENTERED', body=body).execute()
                # print(f'result update: {result}')
                return result
            # print(f'res: {res["values"][0][0]}')
            # print('Error: время занято')
            return 'data_exist'
        else:
            if "opened" in value:
                value = value[6:]
                body = {'values': [[value]]}
            result = sheets.values().update(spreadsheetId=spreadsheet_id, range=rrange, valueInputOption='USER_ENTERED', body=body).execute()
            print(f'result update: {result}')
            return result

    except HttpError as error:
        print(error)


async def create_next_month_calendar_bot(callback, spreadsheet_id, service, year, month, title):
    try:

        rrange = title + "!A:H"

        if not sheet_is_exist(service, title, spreadsheet_id):
            create_sheet(service, title, spreadsheet_id)
            update_sheet(service, title, spreadsheet_id)
            create_list(service, year, month, rrange, spreadsheet_id)
            formatting_sheet(service, title, spreadsheet_id)
        # else:
        #     print("Sheet is exist.")
            # update_cell(service, title, spreadsheet_id, 15, month, year, 26, 'Привет лунатикам')
        # print(sheet_is_exist(service, 'ноябрь2023'))

    except HttpError as error:
        print(error)


# async def create_next_month_calendar(callback, spreadsheet_id):
#     credentials = await get_or_create_credentials(SCOPES, callback)
#
#     try:
#         service = build('sheets', 'v4', credentials=credentials)
#         # get_by_range(service)
#         month = 12
#         year = 2023
#         title = f'{to_ru_month[calendar.month_name[month]].lower()}{year}'
#         rrange = title + "!A:H"
#
#         if not sheet_is_exist(service, title, spreadsheet_id):
#             create_sheet(service, title, spreadsheet_id)
#             update_sheet(service, title, spreadsheet_id)
#             create_list(service, year, month, rrange, spreadsheet_id)
#             formatting_sheet(service, title, spreadsheet_id)
#         else:
#             print("Sheet is exist.")
#             # update_cell(service, title, spreadsheet_id, 15, month, year, 26, 'Привет лунатикам')
#         # print(sheet_is_exist(service, 'ноябрь2023'))
#
#     except HttpError as error:
#         print(error)


async def google_main(callback, spreadsheet_id):
    credentials = await get_or_create_credentials(SCOPES, callback)

    try:
        spreadsheet_id = spreadsheet_id
        service = build('sheets', 'v4', credentials=credentials)
        # get_by_range(service)
        month = 12
        year = 2023
        title = f'{to_ru_month[calendar.month_name[month]].lower()}{year}'
        rrange = title + "!A:H"

        if not sheet_is_exist(service, title, spreadsheet_id):
            create_sheet(service, title, spreadsheet_id)
            update_sheet(service, title, spreadsheet_id)
            create_list(service, year, month, rrange, spreadsheet_id)
            formatting_sheet(service, title, spreadsheet_id)
        else:
            print("Sheet is exist.")
            await update_cell(spreadsheet_id, 15, month, year, 26, 'Привет лунатикам', callback)
        # print(sheet_is_exist(service, 'ноябрь2023'))

    except HttpError as error:
        print(f'MyError: {error}')


# if __name__ == "__main__":
#     google_main()
