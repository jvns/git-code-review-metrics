The code assumes that you have the public-inbox archives and the Git repository at
`0.git`, `1.git`, and `git/` in the current directory.

```
git clone --mirror https://lore.kernel.org/git/0 0.git
git clone --mirror https://lore.kernel.org/git/1 1.git
git clone https://github.com/git/git
```

I made symlinks

Run all the `sync` scripts to create a SQLite DB with the data and then you can
run the Jupyter notebook. The sync scripts are not smart now and can't do an
incremental sync.
