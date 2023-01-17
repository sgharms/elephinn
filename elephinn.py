import sys
from mastodon import Mastodon

VALID_SUBCOMMANDS=["register", "fetch_follows", "rss_feeds_for_follows",
                   "find_local_toot"]
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
    else:
        raise RuntimeError(f"Bug! Could not find behavior for {cmd}")

def register():
    print(f"Saving credentials for caching in {MY_MASTODON_CREDENTIALS_FILE}")
    Mastodon.create_app(
        MY_MASTODON_APP_NAME,
        api_base_url = MY_MASTODON_NODE_NAME,
        to_file = MY_MASTODON_CREDENTIALS_FILE
    )

def _login(authenticated_func):
    def _decorated_login():
        with(open(MY_LOGIN_SECRETS_FILE)) as f:
            [login, password] = map(lambda t: t.rstrip(), f.readlines())
            usercred_file = f".{MY_MASTODON_APP_NAME}_usercred.secret"
            mastodon = Mastodon(client_id = MY_MASTODON_CREDENTIALS_FILE)
            mastodon.log_in(login, password, to_file = usercred_file)
        authenticated_func(mastodon)
    return _decorated_login

def follows_list(session):
    id = session.me()["id"]
    return session.account_following(id)

@_login
def fetch_follows(session):
    follows = follows_list(session)
    for follow in follows:
        print(follow["username"], follow["url"])

@_login
def rss_feeds_for_follows(session):
    follows = sorted(follows_list(session), key = lambda a: a["url"])
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

if __name__ == "__main__":
    subcommand = sys.argv[1]
    if subcommand.lower() in VALID_SUBCOMMANDS:
        process_subcommand(subcommand)
    else:
        raise RuntimeError(f"No valid subcommand provided. Eligible options: {','.join(VALID_SUBCOMMANDS)}")
