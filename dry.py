#!/usr/bin/env python
"""A collection of methods to keep things DRY."""

import random
import string


def randomString(length=32):
    """Generate a random string of given length.

    String is a combination of ASCII characters and digits.
    Default length is 32.
    Minimum length is 4.
    Maximum length is 64.
    """
    if length > 64:
        length = 64
    elif length < 4:
        length = 4

    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(length))
