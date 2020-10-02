import json
import logging
import base64
import time

from github import Github, GithubException
from tornado.web import HTTPError

from .base import APIBaseHandler, github_authenticated

logger = logging.getLogger(__name__)

class GHHandler(APIBaseHandler):

    @github_authenticated
    def get(self, repo_name=None):
        """
        Check repo existence
        or get all public repos
        {
            "name": repo name
        }
        """
        user = json.loads(self.get_secure_cookie("user"))
        g = Github(user['access_token'])
        # authenticated user
        auth_user = g.get_user()

        if not repo_name:
            print("NO REPO NAME")
            list = []
            if auth_user.login:
                try:
                    repos = auth_user.get_repos()
                except GithubException:
                    self.finish({
                        'success': True,
                        'exists': False,
                        'msg': list
                    })
                except Exception as exc:  # unexpected
                    raise HTTPError(500, reason=str(exc))
                else:

                    for repo in repos:
                        list.append(repo.name)
                    self.finish({
                        'success': True,
                        'exists': True,
                        'msg': list
                    })
            else:
                raise HTTPError(400, reason=f"Unable to authenticate user")
        else:
            print('REPO NAME', repo_name)
            if auth_user.login:
                print(auth_user)
                try:
                    repo = auth_user.get_repo(repo_name)
                except GithubException.UnknownObjectException:
                    self.finish({
                        'success': True,
                        'exists': False,
                        'msg': f"{repo_name} does not exist"
                    })
                except Exception as exc:  # unexpected
                    raise HTTPError(500, reason=str(exc))
                else:
                    if repo.full_name:
                        contents = repo.get_contents("")
                        files = []
                        for content_file in contents:
                            files.append(content_file.path)
                        self.finish({
                            'success': True,
                            'exists': True,
                            'msg': files
                        })
                    else:
                        self.finish({
                            'success': True,
                            'exists': False,
                            'msg': f"{repo_name} does not exist"
                        })
            else:
                raise HTTPError(400, reason=f"Unable to authenticate user")


    @github_authenticated
    def delete(self):
        """
        Delete repo
        {
            "name": repo name
        }
        """
        user = json.loads(self.get_secure_cookie("user"))
        g = Github(user['access_token'])
        # authenticated user
        auth_user = g.get_user()
        repo_name = self.args.name
        if not repo_name:
            raise HTTPError(400, reason=f"Repo name not provided")
        try:
            repo = auth_user.get_repo(full_name=repo_name)
            repo.delete()
        except GithubException as e:
            raise HTTPError(400, reason=e)
        except Exception as exc:  # unexpected
            raise HTTPError(500, reason=str(exc))
        if not repo:
            logging.info(msg="Deleted repo "+repo_name)
            self.finish({
                'success': True,
                'msg': f"{repo_name} was deleted"
            })

    @github_authenticated
    def post(self):
        """
        Create new repo with file
        or add file to existing repo
        {
            "name": repo name
            "file": name of jsonld schema
            "data": file content- needs to be encoded
        }
        """
        if self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)
        repo_name = self.args.get('name', None)
        file_name = self.args.get('file', None)
        msg = self.args.get('comment', "added by Data Discovery Engine")
        existing = self.args.get('existing', False)
        # data must be encoded
        data = self.args.get('data', None)
        if data:
            content_encoded = json.dumps(data, indent=2).encode('utf-8')
        else:
            raise HTTPError(400, reason=f"File content not provided")
        if not repo_name:
            raise HTTPError(400, reason=f"Repo name not provided")

        logging.info(msg="Repo name "+repo_name)
        user = json.loads(self.get_secure_cookie("user"))
        # print('Token', user['access_token'])
        # signin with token
        g = Github(user['access_token'])
        # authenticated user
        auth_user = g.get_user()
        if auth_user.login:

            if existing:
                try:
                    repo = auth_user.get_repo(repo_name)
                except GithubException.UnknownObjectException:
                    self.finish({
                        'success': False,
                        'exists': True,
                        'msg': f"Repo {repo_name} already exists"
                    })
                except Exception as exc:  # unexpected
                    raise HTTPError(500, reason=str(exc))
            else:
                try:
                    print('auth_user',auth_user)
                    repo = auth_user.create_repo(repo_name)
                    # print("REPO CREATED ",repo.full_name)
                except GithubException as e:
                    raise HTTPError(400, reason=e)
                except Exception as exc:  # unexpected
                    raise HTTPError(500, reason=str(exc))

        else:
            raise HTTPError(400, reason=f"Unable to authenticate user")

        if repo:
            path = file_name
            file = repo.create_file(path, msg, content_encoded)
            # returns
            # { ‘content’: ContentFile:, ‘commit’: Commit}
            if file:
                self.finish({
                    'success': True,
                    'msg': repo.full_name
                })
        else:
            self.finish({
                'success': False,
                'msg': f"{repo_name} does not exist"
            })

    @github_authenticated
    def put(self):
        """
        Update file in repo
        {
            "name": repo name
            "file": name or path to file
            "data": file content- needs to be encoded
            'existing': existing repo,
            'comment': commit comment,
            'existing_file': update existing file?
        }
        """
        if self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)
        repo_name = self.args.get('name', None)
        file_name = self.args.get('file', None)
        msg = self.args.get('comment', "updated via Data Discovery Engine")
        existing = self.args.get('existing', True)
        existing_file = self.args.get('existing_file', True)

        # data must be encoded
        data = self.args.get('data', None)
        if data:
            content_encoded = json.dumps(data, indent=2).encode('utf-8')
        else:
            raise HTTPError(400, reason=f"File content not provided")
        if not repo_name:
            raise HTTPError(400, reason=f"Repo name not provided")

        logging.info(msg="Updating file on repo.name: "+repo_name)
        user = json.loads(self.get_secure_cookie("user"))
        g = Github(user['access_token'])
        # authenticated user
        auth_user = g.get_user()
        if auth_user.login:
            try:
                repo = auth_user.get_repo(repo_name)
            except GithubException as e:
                raise HTTPError(400, reason=e)
            except Exception as exc:  # unexpected
                raise HTTPError(500, reason=str(exc))
        else:
            raise HTTPError(400, reason=f"Unable to authenticate user")
        if repo and existing_file:
            file_path = file_name
            try:
                file = repo.get_contents(file_path)
            except GithubException as e:
                raise HTTPError(400, reason=e)
            except Exception as exc:  # unexpected
                raise HTTPError(500, reason=str(exc))
            if file:
                file_updated = repo.update_file(file_path, msg, content_encoded, file.sha)
                if file_updated:
                    logging.info(msg="File updated name "+file_name)
                    self.finish({
                        'success': True,
                        'msg': repo.full_name
                    })
                else:
                    self.finish({
                        'success': False,
                        'msg': repo.full_name
                    })
        else:
            self.finish({
                'success': False,
                'msg': f"{repo_name} repo or file must exist."
            })
