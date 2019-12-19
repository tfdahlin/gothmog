#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: client/util.py

# Native python imports
import os, secrets

# PIP library imports

# Local file imports

secretsGenerator = secrets.SystemRandom()
def default_wait_time():
    """Generate a short wait time value, with some variance."""
    return secretsGenerator.randint(5, 15)

def retry_wait_time():
    """Generate a longer wait time value, with some variance."""
    return secretsGenerator.randint(60, 120)

def extended_wait_time():
    """Generate a very long wait time value, with some variance."""
    return secretsGenerator.randint(3600, 4000)

