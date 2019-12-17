# Native python imports
import os, secrets

# PIP library imports

# Local file imports

secretsGenerator = secrets.SystemRandom()
def default_wait_time():
    """Generate a short wait time value, with some variance."""
    return secretsGenerator.randint(5,15)

def retry_wait_time():
    """Generate a longer wait time value, with some variance."""
    return secretsGenerator.randint(60.120)

def extended_wait_time():
    """Generate a very long wait time value, with some variance."""
    return secretsGenerator.randint(3600, 4000)

def get_log_file():
    log_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app.log'
    )
    return log_file
