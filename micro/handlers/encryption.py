# Necessary imports
import hmac


# Secret key for encryption
secret = 'bees'


# Function for encrypting things!
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


# Function for checking if value is encrypted
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
