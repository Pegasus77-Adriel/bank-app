import sqlite3

def view_users():
    conn = sqlite3.connect('data/bank.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

if __name__ == '__main__':
    users = view_users()
    for user in users:
        print(user)