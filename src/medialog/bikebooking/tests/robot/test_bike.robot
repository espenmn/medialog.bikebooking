# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s medialog.bikebooking -t test_bike.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src medialog.bikebooking.testing.MEDIALOG_BIKEBOOKING_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/plonetraining/testing/tests/robot/test_bike.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Bike
  Given a logged-in site administrator
    and an add bike form
   When I type 'My Bike' into the title field
    and I submit the form
   Then a bike with the title 'My Bike' has been created

Scenario: As a site administrator I can view a Bike
  Given a logged-in site administrator
    and a bike 'My Bike'
   When I go to the bike view
   Then I can see the bike title 'My Bike'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add bike form
  Go To  ${PLONE_URL}/++add++Bike

a bike 'My Bike'
  Create content  type=Bike  id=my-bike  title=My Bike


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.title  ${title}

I submit the form
  Click Button  Save

I go to the bike view
  Go To  ${PLONE_URL}/my-bike
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a bike with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the bike title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
