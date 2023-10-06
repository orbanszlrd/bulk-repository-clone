#!/usr/bin/env python3

from git import Repo, GitCommandError
import requests
import sys

def get_username():
    return "orbanszlrd" if len(sys.argv) > 1 else input("Please provide GitHub username: ")

def get_token():
    return sys.argv[1] if len(sys.argv) > 1 else input("Please provide GitHub token: ")

def fetch_data(url, headers): 
    response = requests.get(url, headers=headers)
    return response.json()


def process_projects(owner, projects):
    print(f"{owner}: {len(projects)} projects")
    if len(projects) > 0:
        print_projects(projects)
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
    username = get_username()
    api_url = "https://api.github.com/"
    query_params = "?sort=name&per_page=100"
    user_url = f"{api_url}users/{username}"
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + get_token(), "X-GitHub-Api-Version": "2022-11-28"}
    user = fetch_data(user_url, headers)

    if "message" in user:
        sys.exit(user["message"])

    repos_url = f"{api_url}user/repos{query_params}&affiliation=owner"
    projects = fetch_data(repos_url, headers)

    process_projects(username, projects)

    if "organizations_url" in user:
        organizations = fetch_data(user["organizations_url"], headers)

        for organization in organizations:
            if "repos_url" in organization:
                owner = organization["login"]
                repos_url = organization["repos_url"] + query_params
                projects = fetch_data(repos_url, headers)
                process_projects(owner, projects)

    sys.exit("Success.")
