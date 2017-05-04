# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from medialog.bikebooking.testing import MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that medialog.bikebooking is properly installed."""

    layer = MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if medialog.bikebooking is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'medialog.bikebooking'))

    def test_browserlayer(self):
        """Test that IMedialogBikebookingLayer is registered."""
        from medialog.bikebooking.interfaces import (
            IMedialogBikebookingLayer)
        from plone.browserlayer import utils
        self.assertIn(IMedialogBikebookingLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['medialog.bikebooking'])

    def test_product_uninstalled(self):
        """Test if medialog.bikebooking is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'medialog.bikebooking'))

    def test_browserlayer_removed(self):
        """Test that IMedialogBikebookingLayer is removed."""
        from medialog.bikebooking.interfaces import IMedialogBikebookingLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMedialogBikebookingLayer, utils.registered_layers())
