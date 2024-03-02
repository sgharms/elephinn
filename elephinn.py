import sys
import pprint
from subprocess import check_output
from mastodon import Mastodon
from bs4 import BeautifulSoup
from math import inf

VALID_SUBCOMMANDS=["register", "fetch_follows", "rss_feeds_for_follows",
                   "find_local_toot", "open_local_toot", "fetch_mentions",
                   "help"]
MY_MASTODON_APP_NAME="elephinn"
MY_MASTODON_NODE_NAME="techhub.social"
MY_MASTODON_CREDENTIALS_FILE=".elephinn_credentials.secret"
MY_LOGIN_SECRETS_FILE=".login.secret"

def process_subcommand(cmd):
    if "register" == cmd:
        register()
    elif "fetch_follows" == cmd:
        fetch_follows()
    elif "rss_feeds_for_follows" == cmd:
        rss_feeds_for_follows()
    elif "find_local_toot" == cmd:
        find_local_toot()
    elif "open_local_toot" == cmd:
        open_local_toot()
    elif "fetch_mentions" == cmd:
        fetch_mentions()
    elif "help" == cmd:
        help()
    else:
        raise RuntimeError(f"Bug! Could not find behavior for {cmd}")

def help():
    cmds = "\n".join(sorted(VALID_SUBCOMMANDS))

    print("""
Welcome to elephinn.py help

Valid commands are:

""" + cmds + "\n\n")

def register():
    """
    Creates a local credentials file based on the credentials provided by ./.login.secret
    """
    print(f"Saving credentials for caching in {MY_MASTODON_CREDENTIALS_FILE}")
    Mastodon.create_app(
        MY_MASTODON_APP_NAME,
        api_base_url = MY_MASTODON_NODE_NAME,
        to_file = MY_MASTODON_CREDENTIALS_FILE
    )

def _login(authenticated_func):
    """
    All internal methods need a wrapper of login around their execution. This
    is that wrapper. You should not call it directly
    """
    def _decorated_login():
        with(open(MY_LOGIN_SECRETS_FILE)) as f:
            [login, password] = map(lambda t: t.rstrip(), f.readlines())
            usercred_file = f".{MY_MASTODON_APP_NAME}_usercred.secret"
            mastodon = Mastodon(client_id = MY_MASTODON_CREDENTIALS_FILE)
            mastodon.log_in(login, password, to_file = usercred_file)
        return authenticated_func(mastodon)
    return _decorated_login

def _follows_list(session):
    """
    Helper method
    """
    id = session.me()["id"]
    return session.account_following(id)

@_login
def fetch_mentions(session):
    """
    ./elephinn.py fetch_mentions 20

    Get mentions in sets of 15 until we cross 20 (so this will get 30 total).

    Leaving off the final arg will do fetches of n=15 through your entire
    @-mention history. This may be a jerky thing to do. Don't be a jerk.
    
    """
    excluded_types = ["follow", "follow_request", "favourite", "reblog", "update", "poll"]
    def extract_relevant(s):
        return {
            "id": s["id"],
            "url": s["status"]["url"],
            "date": s["status"]["created_at"],
            "content": BeautifulSoup(s["status"]["content"], 'html.parser').text,
            "acct": s["account"]["acct"]
        }

    max_id: int = None
    threshold_counter: int = 0
    threshold: int = int(sys.argv[2]) if len(sys.argv) >= 3 else inf
    while (True):
        mentions = session.notifications(exclude_types=excluded_types, max_id=max_id)
        if (len(mentions) == 0 ):
            break
        results = [ extract_relevant(struc) for struc in mentions]
        max_id = int(mentions[-1]["id"])
        pprint.pprint(results)
        threshold_counter += len(mentions)
        if threshold_counter >= threshold:
            break

@_login
def fetch_follows(session):
    follows = _follows_list(session)
    for follow in follows:
        print(follow["username"], follow["url"])

@_login
def rss_feeds_for_follows(session):
    follows = sorted(_follows_list(session), key = lambda a: a["url"])
    for follow in follows:
        print(follow["url"] + ".rss")

@_login
def find_local_toot(session):
    """
    If you're looking at statuses in an RSS reader and then want to reply, the
    URL you have is *probably* not the url at your home node. As such, search
    for the toot based on its canonical URI at your home node. The return value
    is the URL you can reply to.
    """
    if (len(sys.argv) < 3):
        raise RuntimeError("A toot url should be passed in")
    q = sys.argv[2]
    result = session.search(q, result_type="statuses")["statuses"][0]
    localized_id = result["id"]
    localized_acct = result['account']['acct']
    retarget = f"https://{MY_MASTODON_NODE_NAME}/@{localized_acct}/{localized_id}"
    print(retarget)
    return retarget

def open_local_toot():
    """
    This is a slight extension to find_local_toot, but here we actually shell
    out to execute some program that processes the URL calculated by
    find_local_toot. On OSX (my development platform), that's `open`.
    """
    url = find_local_toot()
    check_output(["open", url])

if __name__ == "__main__":
    if (len(sys.argv) <= 1 ):
        raise RuntimeError(f"No subcommand provided. Check for typos. Eligible options: {', '.join(VALID_SUBCOMMANDS)}")

    subcommand = sys.argv[1]
    if not subcommand.lower() in VALID_SUBCOMMANDS:
        raise RuntimeError(f"No recognized subcommand provided. Check for typos. Eligible options: {', '.join(VALID_SUBCOMMANDS)}")

    process_subcommand(subcommand)
