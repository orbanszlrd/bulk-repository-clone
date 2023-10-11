# Bulk Repository Clone

List, clone or update all GitHub repositories of a user

## Script attributes

- **--username**, **-u**: GitHub username
- **--token**, **-t**: GitHub personal access token. [Generate token here](https://github.com/settings/tokens)
- **--action**, **-a**: Action to take: list / clone / all
- **--dir**, **-d**: Target directory

## Usage

`python3 brc.py --username <username> --token <token> --action <list|clone|all> --dir <dir>`

`python3 brc.py -u <username> -t <token> -a <list|clone|all> -d <dir>`

## Hints

- for running the script need to have *python3* installed
- on linux machines you can run the script just typing `./brc.py` if the file is executable. Type `chmod u+x brc.py` to achieve that
- *username* is required. If not provided as an argument, the script will prompt you to enter it
- public repositories are accessible without any token.
- default action is *list*
- default target directory is *projects/github*
  