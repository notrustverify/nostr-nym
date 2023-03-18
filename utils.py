import os

from dotenv import load_dotenv


load_dotenv()

DEBUG=True

NYM_CLIENT_ADDR = os.getenv("NYM_CLIENT_ADDR", '127.0.0.1')
NOSTR_RELAY_ADDR = os.getenv("NOSTR_RELAY_ADDR", 'localhost')
NOSTR_RELAY_PORT = os.getenv("NOSTR_RELAY_PORT", '7000')