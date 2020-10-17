
import subprocess
import os
import warnings
import re
import traceback

def git_warn(name, e):
    warnings.warn("Cannot git_get_{}".format(name))
    #traceback.print_exc()

def git_get_branch(file):
    cwd = os.path.dirname(os.path.abspath(file))
    try:
        proc = subprocess.run(
            ["git", "show-branch"], capture_output=True, cwd=cwd, check=True)
        branch = proc.stdout
        branch = branch.decode('utf-8')
        branch = branch.strip()
        if branch:
            return branch
        else:
            return None
    except Exception as e:
        git_warn("branch", e)
        return None


def git_get_status(file):
    cwd = os.path.dirname(os.path.abspath(file))
    try:
        proc = subprocess.run(
            ["git", "show", "--oneline", "-s"], capture_output=True, cwd=cwd, check=True)
        status = proc.stdout
        status = status.decode('utf-8')
        status = status.strip()
        if status:
            m = re.match("^(\\w+)\\s", status)
            if m:
                commit = m.group(1).strip()
            else:
                commit = None
            return status, commit
        else:
            return None, None
    except Exception as e:
        git_warn("status", e)
        return None, None


def git_get_remote(file, name="origin"):
    cwd = os.path.dirname(os.path.abspath(file))
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", name], capture_output=True, cwd=cwd, check=True)
        remote = proc.stdout
        remote = remote.decode('utf-8')
        remote = remote.strip()
        return remote
    except Exception as e:
        git_warn("remote", e)
        return None

def git_get_tags(__file__):
    status, commit = git_get_status(__file__)
    url = git_get_remote(__file__)
    branch = git_get_branch(__file__)
    tags = {
        "GitStatus": status,
        "GitCommit": commit,
        "GitOrigin": url,
        "GitBranch": branch,
    }
    tags = {
        k: v for k, v in tags.items() if v
    }
    return tags


if __name__ == '__main__':
    from pprint import pprint
    tags = git_get_tags(__file__)
    pprint(tags)
    from aws_sagemaker_remote.tags import make_tags
    tags = make_tags(tags)
    pprint(tags)

    tags = git_get_tags(r"C:\Projects\split-audio\setup.py")
    
    print("Audio")
    pprint(tags)
