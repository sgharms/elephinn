# Elephinn

A collection of utilities for helping Newsraft help us navigate the pachyderm
site(s) à la Huckleberry Finn.

## Getting Started

1. Store your credentials locally in `.login-secret` in the git-cloned
   directory. Changing this location/filename is easy enough by editing the
   code. This repo is already ignoring that file with git.
2. Use the `elephinn.py register` command. Look for `Saving credentials for
   caching in `.elephinn_credentials.secret` as a signal that all went well
3. `elephinny.py fetch_follows` should now work
4. To get their RSS publication URL: `rss_feeds_for_follows`
