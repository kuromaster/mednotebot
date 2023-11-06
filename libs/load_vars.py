from libs.db_lib import pg_select_one_column as pg_soc, pg_select
from config_reader import myvars


async def update_appointments():
    query = "SELECT appt_date, tid, doctor_id, is_approved, is_closed, notify_date " \
            "FROM tb_appointments as ap " \
            "LEFT JOIN tb_customers as cu " \
            "ON ap.cid = cu.id " \
            "WHERE appt_date > CURRENT_TIMESTAMP"
    rows = pg_select(query)

    myvars.appointments = {}
    for row in rows:
        myvars.appointments[row[0]] = {'tid': row[1], 'doctor_id': row[2], 'is_approved': row[3], 'is_closed': row[4],
                                       'notify_date': row[5]}


def update_superuser():
    query = "SELECT tid FROM tb_customers WHERE is_superuser=1"
    myvars.superuser = pg_soc(query)
    return myvars.superuser


def update_administrator():
    query = "SELECT tid FROM tb_customers WHERE is_administrator=1"
    myvars.administrator = pg_soc(query)


def update_doctor():
    query = "SELECT lastname, name, surname, tid, spreadsheet_id FROM tb_customers WHERE is_doctor=1"
    rows = pg_select(query)
    myvars.doctors = {}
    for row in rows:
        myvars.doctors[f'{row[0]} {row[1][0]}.{row[2][0]}.'] = {'id': row[3], 'spreadsheet_id': f'{row[4]}'}


def update_registred():
    query = "SELECT tid FROM tb_customers"
    myvars.registred_users = pg_soc(query)


async def loadvars():
    update_superuser()
    update_registred()
    update_doctor()
    update_administrator()
    await update_appointments()
