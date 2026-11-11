from pygit2 import Repository
import pygit2
import sqlite3

"""
Take `notes/amlog` and put it in a sql table to make it easier to cross reference

One thing here is that sometimes there are multiple message IDs and I don't know
what it means. I think this happens 64 times. Maybe that should be dealt with
more explicitly in this file.
"""

def create_db(cur):
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS amlog
(
commit_id TEXT PRIMARY KEY,
message_id TEXT NOT NULL
)
""")


def process(repo, con, cur):
    commit = repo.revparse_single('notes/amlog')
    # pygit doesn't seem to have libgit2's function for iterating over a tree
    # but a github comment suggested this hack where we diff from the empty
    # tree instead
    diff = commit.tree.diff_to_tree()
    i = 0
    for p in diff:
        file = p.delta.old_file
        filename = file.path
        contents = repo[file.id].data
        message_id = contents.strip(b'Message-Id: ').strip().decode('utf-8')
        commit_id = filename.replace('/', '')
        i += 1
        data = [commit_id, message_id]
        cur.execute('INSERT OR REPLACE INTO amlog VALUES (?, ?)', data)
        if i % 1000 == 0:
            con.commit()
            print(f"processed {i} entries")

def main():
    con = sqlite3.connect('emails.db')
    cur = con.cursor()
    create_db(cur)
    process(Repository('git'), con, cur)
    

if __name__ == '__main__':
    main()
