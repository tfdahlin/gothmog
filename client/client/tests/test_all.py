#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: client/tests/test_all.py

# Native python imports
from unittest import TestCase

# PIP library imports

# Local file imports
from client import Client

class TestClient(TestCase):
    def setUp(self):
        """Set up performed before tests in this class are run."""
        self.client_instance = Client('http://127.0.0.1', 13889)
        pass

    def tearDown(self):
        """Tear down performed after tests in this class are run."""
        pass

    def test_main(self):
        pass
