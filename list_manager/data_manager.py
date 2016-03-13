"""
"""
class NoListFoundError(Exception):
    pass

class NoItemFoundError(Exception):
    pass


import MySQLdb as msql
from datetime import datetime as dt
def deactive_user(user_id, access_token, db):
    now = dt.now()
    deleted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print deleted_time
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update users set deleted_time = %s where id = %s and deleted_time is null""", (deleted_time, user_id))
    cur.execute("""update access_tokens set deleted_time = %s where user_id = %s and deleted_time is NULL """, (deleted_time, user_id))
    db.commit()

def list_of_list(user_id, db):
    print user_id
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select l.id , l.name, l.status from lists l where l.user_id = %s and deleted_time is null""", (user_id,))
    if cur.rowcount == 0:
        raise NoListFoundError
    else:
        rows = list(cur.fetchall())
        print rows
        lists_with_items = items_of_list(rows,db)
        print lists_with_items
        return lists_with_items

def items_of_list(rows, db):
    for x in rows:
        id = x['id']
        cur = db.cursor(msql.cursors.DictCursor)
        cur.execute("""select i.id, i.name, i.status, i.quantity from items i where i.list_id = %s and deleted_time is null""" , (id,))
        items = list(cur.fetchall())
        x["items"] = items
    return rows

def fetch_list(list_id, user_id, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select l.id , l.name, l.status from lists l where l.id = %s and user_id = %s and deleted_time is null""", (list_id, user_id) )
    if cur.rowcount == 0:
        raise NoListFoundError
    else:
        return items_of_list(list(cur.fetchall()), db)

def create_new_list(list_name, user_id, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""insert into lists (user_id, name, status) values (%s, %s, 'incomplete')""" ,(user_id, list_name))
    db.commit()
    id = cur.lastrowid
    cur.execute("""select l.id, l.name, l.status from lists l where l.user_id = %s and l.id = %s and deleted_time is null""", (user_id, id))
    return cur.fetchall()

def change_list_name(list_id, new_name, user_id, db):
    validate_list(list_id, user_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update lists set name = %s where id = %s and user_id = %s and deleted_time is null""", (new_name, list_id, user_id))
    db.commit()
    cur.execute("""select l.id, l.name, l.status from lists l where l.id = %s and user_id = %s and deleted_time ia null""", (list_id, user_id))
    return cur.fetchone()

def logout_user(access_token, db):
    cur = db.cursor(msql.cursors.DictCursor)
    now = dt.now()#.strftime("%Y-%m-%d %H:%M:%S")
    print now
    cur.execute("""update access_tokens set deleted_time = %s where access_token = %s and deleted_time is null""" , (now ,access_token))
    db.commit()

def delete_list(list_id, user_id, db):
    now = dt.now()
    cur = db.cursor(msql.cursors.DictCursor)
    validate_list(list_id, user_id, db)
    cur.execute("""update lists set deleted_time = %s where id = %s and user_id = %s and deleted_time is null""" , (now, list_id, user_id))
    db.commit()

def validate_list(list_id, user_id, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select id from lists where id = %s and user_id = %s and deleted_time is null""", (list_id, user_id))
    if cur.rowcount == 0:
        raise NoListFoundError

def add_item_to_list(list_id, user_id, name, status, quantity, db):
    validate_list(list_id, user_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""insert into items (list_id, name, status, quantity) values (%s, %s, %s, %s)""" ,(list_id, name, status, quantity))
    db.commit()
    id = cur.lastrowid
    cur.execute("""select id, name, status from lists where id = %s and deleted_time is null""", (list_id,))
    list_info = cur.fetchone()
    print list_info
    cur.execute("""select id, name, status, quantity from items where list_id = %s and id = %s and deleted_time is null""", (list_id, id))
    list_info['items'] = list(cur.fetchall())
    print list_info
    return list_info

def validate_item(list_id, item_id, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select id from items where list_id = %s and id = %s and deleted_time is null""", (list_id, item_id))
    if cur.rowcount == 0:
        raise NoItemFoundError

#only changes item name(quantity missed)
def change_item_name(user_id, list_id, item_id, name, db):
    validate_list(list_id, user_id, db)
    validate_item(list_id, item_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update items set name = %s where list_id = %s and id = %s and deleted_time is null""", (name, list_id, item_id))
    db.commit()
    cur.execute("""select id, name, status from lists where id = %s and deleted_time is null""", (list_id,))
    list_info = cur.fetchone()
    print list_info
    cur.execute("""select id, name, status, quantity from items where list_id = %s and id = %s and deleted_time is null""", (list_id, item_id))
    list_info['items'] = list(cur.fetchall())
    print list_info
    return list_info

#only changes item status(quantity missed)
def change_item_status(user_id, list_id, item_id, status, db):
    validate_list(list_id, user_id, db)
    validate_item(list_id, item_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update items set status = %s where list_id = %s and id = %s and deleted_time is null""", (status, list_id, item_id))
    db.commit()
    cur.execute("""select id, name, status from lists where id = %s and deleted_time is null""", (list_id,))
    list_info = cur.fetchone()
    print list_info
    cur.execute("""select id, name, status, quantity from items where list_id = %s and id = %s and deleted_time is null""", (list_id, item_id))
    list_info['items'] = list(cur.fetchall())
    print list_info
    return list_info

def delete_item(user_id, list_id, item_id, db):
    validate_list(list_id, user_id, db)
    validate_item(list_id, item_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    now = dt.now()
    cur.execute("""update items set deleted_time = %s where id = %s and list_id = %s and deleted_time is null""" , (now, item_id, list_id))
    db.commit()

def update_item(user_id, list_id, item_id, name, status, quantity, db):
    validate_list(list_id, user_id, db)
    validate_item(list_id, item_id, db)
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update items set name = %s, quantity = %s, status = %s  where id = %s and deleted_time is null""", (name, quantity, status, item_id))
    db.commit()
    cur.execute("""select id, name, status from lists where id = %s and deleted_time is null""", (list_id,))
    list_info = cur.fetchone()
    print list_info
    cur.execute("""select id, name, status, quantity from items where list_id = %s and id = %s and deleted_time is null""", (list_id, item_id))
    list_info['items'] = list(cur.fetchall())
    print list_info
    return list_info
