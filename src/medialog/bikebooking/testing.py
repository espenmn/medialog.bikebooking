# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import medialog.bikebooking


class MedialogBikebookingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=medialog.bikebooking)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'medialog.bikebooking:default')


MEDIALOG_BIKEBOOKING_FIXTURE = MedialogBikebookingLayer()


MEDIALOG_BIKEBOOKING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MEDIALOG_BIKEBOOKING_FIXTURE,),
    name='MedialogBikebookingLayer:IntegrationTesting'
)


MEDIALOG_BIKEBOOKING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MEDIALOG_BIKEBOOKING_FIXTURE,),
    name='MedialogBikebookingLayer:FunctionalTesting'
)


MEDIALOG_BIKEBOOKING_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MEDIALOG_BIKEBOOKING_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MedialogBikebookingLayer:AcceptanceTesting'
)
