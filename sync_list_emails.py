from pygit2 import Repository
import pygit2
import sqlite3
import email
from email.utils import parsedate_to_datetime

"""
Put the mailing list messages from public inbox in a sqlite database to make
them easier to cross-reference to commits and the amlog
"""

def create_db(cur):
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS list_messages
(
message_id TEXT PRIMARY KEY,
subject TEXT NOT NULL,
date INTEGER NOT NULL,
from_email TEXT NOT NULL,
in_reply_to TEXT,
-- not clear we actually need email_contents might be better to delete
email_contents TEXT NOT NULL
)
""")
    cur.execute(
    """
    CREATE INDEX IF NOT EXISTS list_message_id ON list_messages (message_id)
    CREATE INDEX IF NOT EXISTS list_message_subject ON list_messages (subject)
    """)


def process(repo, con, cur):
    last = repo[repo.head.target]
    i = 0
    for commit in repo.walk(last.id, pygit2.enums.SortMode.TIME):
        tree = commit.tree
        email_object = repo.get(tree[0].id)
        try:
            email_contents = email_object.data.decode('utf-8')
        except:
            try:
                email_contents = email_object.data.decode('ISO-8859-1')
            except:
                # save it to a file so we can figure out what's wrong manually
                with open('bad.txt', 'wb') as f:
                    print(email_object.data)
                    f.write(email_object.data)
                raise
        m = email.message_from_string(email_contents)
        subject = m.get('Subject', "(no subject)") # some subjects are missing
        from_email = m.get("From")
        try:
            dt = parsedate_to_datetime(m.get('Date'))
            date = int(dt.timestamp())
        except ValueError:
            # Some dates are formatted weird. This is not a good solution but it
            # should make the errors easy to find at least.
            # There seems to be only 1 date like this in practice.
            date = 0
        message_id = m.get("Message-ID")
        reply_to = m.get("In-Reply-To", None)
        data = [message_id, subject, date, from_email, reply_to, email_contents]
        cur.execute('INSERT OR REPLACE INTO list_messages VALUES (?, ?, ?, ?, ?, ?)', data)
        i += 1
        if i % 1000 == 0:
            con.commit()
            print(f"processed {i} messages")
        con.commit()

def main():
    con = sqlite3.connect('emails.db')
    cur = con.cursor()
    create_db(cur)
    process(Repository('0.git'), con, cur)
    process(Repository('1.git'), con, cur)
    

if __name__ == '__main__':
    main()
