The code assumes that you have the public-inbox archives and the Git repository at
`0.git`, `1.git`, and `git/` in the current directory.

```
git clone --mirror https://lore.kernel.org/git/0 0.git
git clone --mirror https://lore.kernel.org/git/1 1.git
git clone https://github.com/git/git
```

Basically this is a tiny data pipeline where the steps are:

1. start with 0.git, 1.git, the Git repo, etc. I made symlinks in my current directory to point to them.
2. Run all the `sync` scripts to get the data into SQLite with some opinions about what's useful in terms of analysis.
   The sync scripts are not smart now and can't do an incremental sync.
3. In the Jupyter notebook (the `.ipynb` file) there's a final step to combine everything in the SQLite db into one big table in memory
3. Draw the graphs in Jupyter 

### how to run everything 

I ran the sync scripts like this:

```
uv run sync_amlog.py
uv run sync_list_emails.py
uv run sync_merged_git_commits.py
```

I started Jupyter notebook like this:

```
uv run jupyter notebook
```
