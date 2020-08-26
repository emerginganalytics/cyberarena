import sqlite3


def connect_xssdb():
    xssdb = sqlite3.connect('xss.db')
    xssdb.cursor().execute('CREATE TABLE IF NOT EXISTS comments '
                        '(id INTEGER PRIMARY KEY, '
                        'comment TEXT)')
    xssdb.commit()
    return xssdb


def add_comment(comment):
    xssdb = connect_xssdb()
    xssdb.cursor().execute('INSERT INTO comments (comment) '
                        'VALUES (?)', (comment,))
    xssdb.commit()


def get_comments(search_query=None):
    xssdb = connect_xssdb()
    results = []
    get_all_query = 'SELECT comment FROM comments'
    for (comment,) in xssdb.cursor().execute(get_all_query).fetchall():
        if search_query is None or search_query in comment:
            results.append(comment)
    return results
