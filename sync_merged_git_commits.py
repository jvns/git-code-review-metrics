from pygit2 import Repository
import pygit2
import sqlite3

"""
Make a list of commits that have been merged into `master` which theoretically
should correspond to patch series on the mailing list and put them in a db table.
"""

def create_db(cur):
    # All commits that have been merged into `master`
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS git_commits
(
commit_id TEXT PRIMARY KEY,
commit_message TEXT NOT NULL,
merge_time INTEGER NOT NULL
)
""")

def get_commits(repo):
    last = repo.revparse_single('master')
    i = 0
    for commit in repo.walk(last.id, pygit2.enums.SortMode.TOPOLOGICAL):
        if len(commit.parents) > 1:
            merge_time = commit.commit_time
            # Not totally confident this [1:] is right
            # sometimes merge commits have 3 or 6 parents and
            # I don't totally know how to interpret that.
            # There might be a better way to do this since I'm
            # perpetually confused about what the social contract behind
            # merge commits is.
            for child in commit.parents[1:]:
                yield merge_time, child

def process(repo, con, cur):
    i = 0
    for merge_time, commit in get_commits(repo):
        data = [str(commit.id), commit.message, merge_time]
        cur.execute('INSERT OR REPLACE INTO git_commits VALUES (?, ?, ?)', data)
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
