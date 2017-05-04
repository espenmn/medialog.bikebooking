# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from medialog.bikebooking.testing import MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING  # noqa
from medialog.bikebooking.interfaces import IBike

import unittest2 as unittest


class BikeIntegrationTest(unittest.TestCase):

    layer = MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Bike')
        schema = fti.lookupSchema()
        self.assertEqual(IBike, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Bike')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Bike')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IBike.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('Bike', 'Bike')
        self.assertTrue(
            IBike.providedBy(self.portal['Bike'])
        )
