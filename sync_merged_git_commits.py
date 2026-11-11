from pygit2 import Repository
import pygit2
import sqlite3

def create_db(cur):
    # All commits that have been merged into `master`
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS git_commits
(
commit_id TEXT PRIMARY KEY,
commit_message TEXT NOT NULL
)
""")

def get_commits(repo):
    last = repo.revparse_single('master')
    i = 0
    for commit in repo.walk(last.id, pygit2.enums.SortMode.TOPOLOGICAL):
        if len(commit.parents) > 1:
            for commit in commit.parents[1:]:
                yield commit

def process(repo, con, cur):
    i = 0
    for commit in get_commits(repo):
        data = [str(commit.id), commit.message]
        cur.execute('INSERT OR REPLACE INTO git_commits VALUES (?, ?)', data)
        i += 1
        if i % 1000 == 0:
            con.commit()
            print(f"processed {i} commits")
        con.commit()

def main():
    con = sqlite3.connect('emails.db')
    cur = con.cursor()
    create_db(cur)
    process(Repository('git'), con, cur)
    

if __name__ == '__main__':
    main()
