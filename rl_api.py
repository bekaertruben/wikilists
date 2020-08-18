"""
This module wraps https://www.mediawiki.org/wiki/Extension:ReadingLists#API
The wikimedia reading list API is internal and thus may change without notice, making this code useless.
That being said, at the time of writing it has not changed since 2017.
"""

import requests

session = requests.Session()
csrf_token = None # a csrf token is required to do basically anything

base_url =  "https://en.wikipedia.org/"
api_url = "https://en.wikipedia.org/w/api.php"
default_args = {'format':"json", 'utf8':1}


class ApiException(Exception):
    """Exception raised when the api returns an error"""
    code = None
    info = None
    request_args = None


class LoginException(Exception):
    """Exception raised when logging in to the wiki api fails"""


def wikiget(**kwargs):
    """GET request from the wiki api"""
    args = {**default_args, **kwargs}
    response = session.get(url=api_url, params=args).json()
    if 'error' in response:
        e = ApiException("Getting from the api returned the following error [{}: {}]".format(response['error']['code'], response['error']['info']))
        e.code = response['error']['code']
        e.info = response['error']['info']
        e.request_args = args
        raise e
    if 'warnings' in response:
        print("Getting from the api returned with the following warnings: {}".format(response['warnings']))
    return response


def wikipost(**kwargs):
    """POST request to the wiki api"""
    args = {**default_args, **kwargs}
    response = session.post(url=api_url, data=args).json()
    if "error" in response:
        e = ApiException("Posting to the api returned the following error [{}: {}]".format(response['error']['code'], response['error']['info']))
        e.code = response['error']['code']
        e.info = response['error']['info']
        e.request_args = args
        raise e
    if 'warnings' in response:
        print("Posting to the api returned with the following warnings: {}".format(response['warnings']))
    return response


def get_token(type):
    """gets an api token of the specified type"""
    if not type in ("createaccount", "csrf", "deleteglobalaccount", "login", "patrol", "rollback", "setglobalaccountstatus", "userrights", "watch"):
        raise ValueError("unknown token type")
    return wikiget(action="query", meta="tokens", type=type)['query']['tokens']['{}token'.format(type)]


def botlogin(username, password):
    """log the session in to a bot account"""
    login_token = get_token('login')
    response = wikipost(action="login", lgname=username, lgpassword=password, lgtoken=login_token)
    if response['login']['result'] == 'Success':
        print("-----")
        print("Logged in as user [{} (id: {})]".format(response['login']['lgusername'], response['login']['lguserid']))
        print("-----")
    else:
        raise LoginException("Login using BotPassword Failed")
    
    global csrf_token
    csrf_token = login_token = get_token('csrf')


def clientlogin(username, password):
    """log the session in to your client account"""
    login_token = get_token('login')
    response = wikipost(action="clientlogin", username=username, password=password, loginreturnurl=base_url, logintoken=login_token)
    if response['clientlogin']['status'] == 'PASS':
        print("-----")
        print("Logged in as user {}".format(response['clientlogin']['username']))
        print("/!\\ This is a User account and as such it is very important that you don't leak your login credentials!")
        print("-----")
    else:
        raise LoginException("Client login Failed")
    
    global csrf_token
    csrf_token = login_token = get_token('csrf')


def readinglists(**kwargs):
    """lists reading list on the account"""
    data = {**kwargs, 'action':"query", 'meta':"readinglists"}
    return wikiget(**data)['query']['readinglists']


def readinglistentries(list_ids, **kwargs):
    """lists entries in reading list"""
    data = {**kwargs, 'action':"query", 'list':"readinglistentries", 'rlelists':list_ids}
    return wikiget(**data)['query']['readinglistentries']


def create(name, **kwargs):
    """creates a new reading list"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"create", 'name':name}
    return wikipost(**data)['create']


def create_entry(list_id, title, project="https://en.wikipedia.org", **kwargs):
    """creates a new reading list"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"createentry", 'list':list_id, 'title':title, 'project':project}
    return wikipost(**data)['createentry']


def delete(list_id, **kwargs):
    """deletes a reading list"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"delete", 'list':list_id}
    return wikipost(**data)['delete']


def delete_entry(entry_id, **kwargs):
    """removes a reading list entry"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"deleteentry", 'entry':entry_id}
    return wikipost(**data)['deleteentry']


def setup(**kwargs):
    """creates a new reading list"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"setup"}
    return wikipost(**data)['setup']


def teardown(**kwargs):
    """creates a new reading list"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"teardown"}
    return wikipost(**data)['teardown']


def update(list_id, **kwargs):
    """updates reading list name/description"""
    data = {**kwargs, 'token':csrf_token, 'action':"readinglists", 'command':"update", 'list':list_id}
    return wikipost(**data)['update']
