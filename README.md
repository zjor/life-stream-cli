# life-stream-cli

# Overview

Life is a stream of events, thought noise and ideas are coming every day. The Life Stream service is intended to organize
small notes. Simply save them under the one or more tags. You can find them later easily.
If you want to forget something, simply put it down. 

## How to distribute

1. `python -m pep517.build .`
2. `twine upload dist/*`
3. `pip install life-stream-cli`

## Useful tips

- (Development) Switching between profiles `lst config --set active-profile=default`