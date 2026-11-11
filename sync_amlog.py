from pygit2 import Repository
import pygit2
import sqlite3

def create_db(cur):
    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS amlog
(
commit_id TEXT PRIMARY KEY,
message_id TEXT NOT NULL
)
""")


# taken from https://www.hydrogen18.com/blog/list-all-files-git-repo-pygit2.html
def walk_repo_files(repo, branch):
    tree = repo.revparse_single(branch).tree
    trees_and_paths = [(tree, [])]
    # keep going until there is no more data
    while len(trees_and_paths) != 0:
        tree, path = trees_and_paths.pop() # take the last entry
        for entry in tree:
            if entry.filemode == pygit2.GIT_FILEMODE_TREE:
                next_tree = repo.get(entry.id)
                next_path = list(path)
                next_path.append(entry.name)
                trees_and_paths.append((next_tree, next_path,))
            else:
                yield os.path.join(*path, entry.name)
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
