import os

from dotenv import load_dotenv


load_dotenv()

DEBUG = True

NYM_CLIENT_ADDR = os.getenv("NYM_CLIENT_ADDR", '127.0.0.1')
NYM_CLIENT_PORT = os.getenv("NYM_CLIENT_ADDR", '1977')
NOSTR_RELAY_URI_PORT = os.getenv("NOSTR_RELAY_URI_PORT", 'ws://127.0.0.1:7000')