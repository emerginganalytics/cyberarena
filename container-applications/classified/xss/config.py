import sqlite3


def connect_xssdb():
    xssdb = sqlite3.connect('xss_s.db')
    xssdb.cursor().execute("""CREATE TABLE IF NOT EXISTS feedbacks (workout_ids TEXT, feedback TEXT)""")
    xssdb.commit()
    return xssdb


def add_feedback(feedback, workout_id):
    xssdb = connect_xssdb()
    xssdb.cursor().execute("""INSERT INTO feedbacks (workout_ids, feedback) VALUES (?, ?) """, (workout_id, feedback,))
    xssdb.commit()


def get_feedbacks(workout_id, search_query=None):
    xssdb = connect_xssdb()
    results = []
    for (feedback,) in \
            xssdb.cursor().execute("""SELECT feedback FROM feedbacks WHERE workout_ids=?""", (workout_id,)).fetchall():
        if search_query is None or search_query in feedback:
            results.append(feedback)
    return results
