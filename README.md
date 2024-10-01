# mail_chain.py

Generate many email threads for testing purposes and persist them on an IMAP server.
The script has no dependencies outside of Python's standard library.

## Preparation

1. Provision an IMAP server and enable TLS, e.g. [Stalwart](https://stalw.art/docs/install/docker/).
2. Create two users on it, e.g. `alice@stalwart.localhost` and `bob@stalwart.localhost`.

## Usage

1. Edit the settings block at the beginning of mail_chain.py before running. The settings should be
   self-explanatory.
2. Run the script and pass the desired amount of messages to generate, e.g. `mail_chain.py 100000`.
