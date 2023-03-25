import os

from dotenv import load_dotenv


load_dotenv()

DEBUG = True

NYM_CLIENT_URI = os.getenv("NYM_CLIENT_URI", 'ws://127.0.0.1:1977')

NOSTR_RELAY_URI_PORT = os.getenv("NOSTR_RELAY_URI_PORT", 'ws://127.0.0.1:7000')