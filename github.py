#!/usr/bin/env python3

from git import Repo, GitCommandError
import argparse
import requests
import sys


def main(): 
    args = get_args()

    username = get_username(args.username)
    token = get_token(args.token)

    api_url = "https://api.github.com/"
    query_params = "?sort=name&per_page=100"
    user_url = f"{api_url}users/{username}"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

    if token:
        headers["Authorization"] = 'Bearer ' + token

    user = fetch_data(user_url, headers)

    if "message" in user:
        sys.exit(user["message"])

    repos_url = f"{api_url}user/repos{query_params}&affiliation=owner" if username == "orbanszlrd" and token else f"{api_url}users/{username}/repos{query_params}"

    projects = fetch_data(repos_url, headers)
    process_projects(username, projects, args.action)

    if "organizations_url" in user:
        organizations = fetch_data(user["organizations_url"], headers)

        for organization in organizations:
            if "repos_url" in organization:
                owner = organization["login"]
                repos_url = organization["repos_url"] + query_params
                projects = fetch_data(repos_url, headers)
                process_projects(owner, projects, args.action)

    sys.exit("Success.")


def get_args():
    parser = argparse.ArgumentParser(description="Clone and update GitHub repositories")
    parser.add_argument("-u", "--username")
    parser.add_argument("-t", "--token")
    parser.add_argument("-a", "--action", default="list", help='Choices : list, clone, all (default: list)')
    parser.add_argument("-m", "--menu")

#    parser.print_help()

    return parser.parse_args()


def get_username(username):
    return username or input("Please provide GitHub username: ")


def get_token(token):
    return token or input("Please provide GitHub token (press enter for public repositories): ")


def fetch_data(url, headers): 
    response = requests.get(url, headers=headers)
    return response.json()


def process_projects(owner, projects, action):
    print(f"{owner}: {len(projects)} projects")
    if len(projects) > 0:
        if action in ("list", "all"):
            print_projects(projects)

        if action in ("clone", "all"):
            clone_and_update_projects(projects)


def print_projects(projects):
    print()
    for project in projects :
        print(f"{project['name']}: {project['html_url']}")
    print()


def clone_and_update_projects(projects):
    local_path = "projects/github/"
    env = {"GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no"}

    print("\nClone or update projects\n")
    for project in projects :
        print("Clone", project["full_name"])

        try:
            Repo.clone_from(project["ssh_url"], local_path + project['full_name'], env=env)
            print("Project cloned")
        except GitCommandError:
            print("Project already exists")
            Repo(local_path + project['full_name']).remotes.origin.pull(env=env)
            print("Project updated")
        except:
            print("Unknown error")
        print()


if __name__ == '__main__':
    main()
