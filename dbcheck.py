from sqlite3 import connect


def db():
    try:

        connection = connect("rentamon.db")
        cursor = connection.cursor()
        return cursor
    except Exception as e:
        print(e, "please try again")


cursor = db()
if cursor:
    sqlite_select_query = f"""SELECT * FROM jabama """
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    print(len(records))
    # print(cursor.description)
    for x in records:
        print(x)
    # cursor.close()