import sqlite3


def init_db(db_path):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    query1 = '''CREATE TABLE IF NOT EXISTS requests (start_time TIMESTAMP, 
                                                    user_id INTEGER, 
                                                    user_name TEXT, 
                                                    photo_path TEXT,
                                                    model_time DOUBLE,
                                                    probabilities TEXT,
                                                    result TEXT,
                                                    user_reply TEXT,
                                                    correct_flg BOOLEAN)'''
    cursor.execute(query1)

    query2 = '''CREATE TABLE IF NOT EXISTS requests_hist (start_time TIMESTAMP, 
                                                    user_id INTEGER, 
                                                    user_name TEXT, 
                                                    photo_path TEXT,
                                                    model_time DOUBLE,
                                                    probabilities TEXT,
                                                    result TEXT,
                                                    user_reply TEXT,
                                                    correct_flg BOOLEAN)'''
    cursor.execute(query2)

    con.commit()
    cursor.close()
    con.close()
    print('Init db done')


def write_result(db_path, contex_var):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    query1 = f'''INSERT INTO requests (start_time, user_id, user_name, photo_path, model_time, probabilities, result, user_reply, correct_flg) 
            VALUES ('{contex_var['start_time']}', 
                    {contex_var['user_id']},
                   '{contex_var['user_name']}',
                   '{contex_var['photo_path']}',
                   '{contex_var['model_time']}',
                   '{contex_var['probabilities']}',
                   '{contex_var['result']}',
                   '{contex_var['user_reply']}',
                    {contex_var['correct_flg']})'''
    try:
        cursor.execute(query1)
    except Exception as e:
        print(e)
    con.commit()
    cursor.close()
    con.close()
    print('Write to db done')


def get_stat(db_path):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    cursor.execute(f"SELECT count(*), count(correct_flg), ROUND((100.0 * SUM(correct_flg))/count(correct_flg), 2), ROUND(avg(model_time), 2) FROM requests")
    stat_data = cursor.fetchall()[0]

    cursor.close()
    con.close()
    print('Get stat done')
    return stat_data


def clr_stat(db_path):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    query1 = f"INSERT INTO requests_hist SELECT * FROM requests"
    cursor.execute(query1)

    query2 = f"DELETE FROM requests"
    cursor.execute(query2)

    con.commit()
    cursor.close()
    con.close()
    print('Clear stat done')

