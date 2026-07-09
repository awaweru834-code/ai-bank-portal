from slowapi import Limiter
from slowapi.util import get_remote_address

# The global bouncer that will protect all our files
limiter = Limiter(key_func=get_remote_address)