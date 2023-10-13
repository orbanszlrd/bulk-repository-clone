#!/usr/bin/env python3

from git import Repo
import argparse
import os
import requests
import sys

def main(): 
    args = get_args()

    username = args.username
    token = args.token

    while True:
        username = get_username(username)
        token = get_token(token)
        per_page = 100

        api_url = "https://api.github.com/"
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

        if token:
            headers["Authorization"] = 'Bearer ' + token

        user_url = f"{api_url}users/{username}"
        user = fetch_data(user_url, headers)

        if "message" in user:
            print("\n" + user["message"] + "\n")
            username = None
            continue

        query_params = f"?sort=name&per_page={per_page}"

        projects = []

        if token:
            page = 1

            while True:
                repos_url = f"{api_url}user/repos{query_params}&affiliation=owner&page={page}"    
                page_projects = fetch_data(repos_url, headers)
                projects.extend(page_projects)
                if len(page_projects) < per_page:
                    break
                page +=1
        else:
            number_of_repos = user["public_repos"]
            pages = get_pages(number_of_repos, per_page)

            for page in range(1, pages + 1):
                repos_url = f"{api_url}users/{username}/repos{query_params}&page={page}"
                projects.extend(fetch_data(repos_url, headers))

        if len(projects) > 0 and username.lower() != str(projects[0]["owner"]["login"]).lower():
            owner = projects[0]["owner"]["login"]
            sys.exit( f"{username} has no access to {owner}'s private repositories")

        process_projects(username, projects, args.action, args.dir)

        if "organizations_url" in user:
            organizations = fetch_data(user["organizations_url"], headers)

            for organization in organizations:
                if "repos_url" in organization:
                    projects = []
                    owner = organization["login"]
                    url = organization["repos_url"]
                    page = 1

                    while True:
                        repos_url = f"{url}{query_params}&page={page}"
                        page_projects = fetch_data(repos_url, headers)
                        projects.extend(page_projects)
                        if len(page_projects) < per_page:
                            break
                        page +=1

                    process_projects(owner, projects, args.action, args.dir)

        print(f"Finished processing {username}'s repositories")
        input("\nPress Enter to continue, Ctrl + c to exit the script!\n")

        username = None
        token = None


def get_args():
    default_dir = os.path.join("projects", "github")

    parser = argparse.ArgumentParser(description="Clone and pull GitHub repositories")
    parser.add_argument("-u", "--username")
    parser.add_argument("-t", "--token")
    parser.add_argument("-a", "--action", default="list", help='Choices : list, clone, all (default: list)')
    parser.add_argument("-d", "--dir", default=default_dir, help=f"Target directory (default: {default_dir})")
    
    return parser.parse_args()


def get_username(username):
    return username or input("Please provide GitHub username: ")


def get_token(token):
    return token or input("Please provide GitHub token (press enter for public repositories only): ")


def fetch_data(url, headers): 
    response = requests.get(url, headers=headers)
    return response.json()


def get_pages(number_of_repos, per_page):
    return number_of_repos // per_page + 1 if number_of_repos % per_page else 0


def process_projects(owner, projects, action, target_dir):
    print(f"\nowner: {owner}")
    print(f"\n{len(projects)} repositories")
    if len(projects) > 0:
        if action in ("list", "all"):
            print_projects(projects)
        
        if action in ("clone", "all"):
            clone_and_pull_projects(projects, target_dir)


def print_projects(projects):
    print()
    for project in projects :
        print(f"{project['name']}: {project['html_url']}")
    print()


def clone_and_pull_projects(projects, target_dir):
    cloned = 0
    updated = 0
    errors = 0

    env = {"GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no"}

    for project in projects :
        print("Clone", project["full_name"])

        target_repo = os.path.abspath(os.path.join(target_dir, project['full_name']))

        try:
            if os.path.isdir(target_repo):
                print(f"Project {target_repo} already exists")
                Repo(target_repo).remotes.origin.pull(env=env)
                print("Updated")
                updated += 1
            else:
                Repo.clone_from(project["ssh_url"], target_repo, env=env)
                print("Cloned to", target_repo)
                cloned += 1
        except Exception as e:
            print(e)
            errors += 1
        print()

    print(f"\n{cloned} projects cloned, {updated} projects updated, {errors} errors\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
