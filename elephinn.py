import sys
from mastodon import Mastodon

VALID_SUBCOMMANDS=["register"]
MY_MASTODON_APP_NAME="elephinn"
MY_MASTODON_NODE_NAME="techhub.social"
MY_MASTODON_CREDENTIALS_FILE=".elephinn_credentials.secret"

def process_subcommand(cmd):
    if "register" == cmd:
        register()

def register():
	print(f"Saving credentials for caching in {MY_MASTODON_CREDENTIALS_FILE}")
	Mastodon.create_app(
		MY_MASTODON_APP_NAME,
		api_base_url = MY_MASTODON_NODE_NAME,
		to_file = MY_MASTODON_CREDENTIALS_FILE
	)

if __name__ == "__main__":
    subcommand = sys.argv[1]
    if subcommand.lower() in VALID_SUBCOMMANDS:
        process_subcommand(subcommand)
    else:
        raise RuntimeError(f"No valid subcommand provided. Eligible options: {','.join(VALID_SUBCOMMANDS)}")
