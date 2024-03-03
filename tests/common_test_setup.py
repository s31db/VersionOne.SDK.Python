from testtools import TestCase
from testtools.assertions import assert_that
from testtools.content import text_content
from testtools.matchers import Equals, GreaterThan
from math import fabs

import v1pysdk
from .common_test_server import PublicTestServerConnection


class TestV1CommonSetup(TestCase):
    def _create_story(self, v1):
        """Creates a very simple story and returns the object"""
        v1StoryName = self.getUniqueString()
        self.addDetail("name", text_content(v1StoryName))

        defaultEstimate = fabs(self.getUniqueInteger())
        self.addDetail("detailedestimate", text_content(str(defaultEstimate)))

        reference = "http://test.com"
        self.addDetail("reference", text_content(reference))

        scope = v1.Scope.select("Name").page(size=1)
        defaultScope = None
        if len(scope) > 0:
            defaultScope = scope.first()
            self.addDetail("scope", text_content(defaultScope.Name))
        else:
            self.addDetail("scope", text_content("None"))

        epic = v1.Epic.select("Name").page(size=1)
        defaultSuper = None
        if len(epic) > 0:
            defaultSuper = epic.first()
            self.addDetail("super", text_content(defaultSuper.Name))
        else:
            self.addDetail("super", text_content("None"))

        # build a filter string that exactly matches what we've set above
        baseFilterStr = (
            "Reference='"
            + reference
            + "'&DetailEstimate='"
            + str(defaultEstimate)
            + "'&"
        )
        if defaultScope:
            baseFilterStr += "Scope.Name='" + defaultScope.Name + "'&"
        if defaultSuper:
            baseFilterStr += "Super.Name='" + defaultSuper.Name + "'&"
        baseFilterStr += "Name='" + v1StoryName + "'"

        newStory = None
        try:
            newStory = v1.Story.create(
                Name=v1StoryName,
                Scope=defaultScope,
                Super=defaultSuper,
                DetailEstimate=defaultEstimate,
                Reference=reference,
            )
        except Exception as e:
            assert_that(
                False, Equals(True), message="Error creating new story: " + str(e)
            )

        # Perform a readback using the constructed filter to make sure the item's on the server
        self.addDetail("readback-filter", text_content(baseFilterStr))

        createdItems = v1.Story.select("Name").filter(baseFilterStr)
        for (
            t
        ) in (
            createdItems
        ):  # run query, but don't throw an exception if nothing is returned
            pass

        assert_that(
            len(createdItems), GreaterThan(0), message="Created item can't be queried"
        )

        return newStory
