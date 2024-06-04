from testtools.content import text_content
from testtools.matchers import (
    GreaterThan,
    LessThan,
    Contains,
)

from .common_test_server import PublicTestServerConnection
from .common_test_setup import TestV1CommonSetup


class TestV1Query(TestV1CommonSetup):
    def test_select_story_as_generic_asset(self):
        """Queries up to 5 story assets"""
        with PublicTestServerConnection.getV1Meta() as v1:
            querySucceeded = True
            size = 0
            try:
                items = v1.AssetType.select("Name").where(Name="Story").page(size=5)
                size = len(list(items))
            except:
                querySucceeded = False

            # test assumes there is at least 1 Story on the test server
            self.assertTrue(querySucceeded)
            self.assertThat(size, LessThan(6))
            self.assertThat(size, GreaterThan(0))

    def test_select_story(self):
        """Queries up to 5 stories"""
        with PublicTestServerConnection.getV1Meta() as v1:
            querySucceeded = True
            size = 0
            try:
                items = v1.Story.select("Name").page(size=5)
                size = len(list(items))
            except:
                querySucceeded = False

            # test assumes there is at least 1 Story on the test server
            self.assertTrue(querySucceeded)
            self.assertThat(size, LessThan(6))
            self.assertThat(size, GreaterThan(0))

    def test_select_epic(self):
        """Queries up to 5 Epics, called Portfolios in the GUI.
        In order to create a new Story, we must be able to query for an Epic we want to put it under,
        and pass that returned Epic object as the Super of the new Story.  This confirms the Epic query
        part always works.
        """
        with PublicTestServerConnection.getV1Meta() as v1:
            querySucceeded = True
            size = 0
            try:
                items = v1.Epic.select("Name").page(size=5)
                size = len(list(items))
            except:
                querySucceeded = False

            # test assumes there is at least 1 Portfolio Item on the test server
            self.assertTrue(querySucceeded)
            self.assertThat(size, LessThan(6))
            self.assertThat(size, GreaterThan(0))

    def test_select_scope(self):
        """Queries up to 5 Scopes, called Projects in the GUI.
        In order to create a new Story, we must be able to query for a Scope we want to put it under,
        and pass that returned Scope object as the Scope of the new Story.  This confirms the Scope query
        part always works.
        """
        with PublicTestServerConnection.getV1Meta() as v1:
            querySucceeded = True
            size = 0
            try:
                items = v1.Scope.select("Name").page(size=5)
                size = len(list(items))
            except:
                querySucceeded = False

            # test assumes there is at least 1 Project on the test server
            self.assertTrue(querySucceeded)
            self.assertThat(size, LessThan(6))
            self.assertThat(size, GreaterThan(0))

    def test_select_task(self):
        """Queries up to 5 Tasks."""
        with PublicTestServerConnection.getV1Meta() as v1:
            querySucceeded = True
            size = 0
            try:
                items = v1.Task.select("Name").page(size=5)
                size = len(list(items))
            except:
                querySucceeded = False

            # test assumes there is at least 1 Task on the test server
            self.assertTrue(querySucceeded)
            self.assertThat(size, LessThan(6))
            self.assertThat(size, GreaterThan(0))

    def test_non_default_query(self):
        """Queries an attribute that's not retrieved by default from a Story so it will requery for the specific
        attribute that was requested.
        """
        with PublicTestServerConnection.getV1Meta() as v1:
            failedFetchCreateDate = False
            failedFetchName = False
            s = v1.Story.select("Name").page(size=1)
            try:
                junk = s.CreateDate  # fetched on demand, not default
            except:
                failedFetchCreateDate = True

            self.assertFalse(failedFetchCreateDate)

            try:
                junk = s.Name  # fetched by default on initial query
            except:
                failedFetchName = True

            self.assertFalse(failedFetchName)

    def test_sum_query(self):
        """Queries for a summation of values of a numeric field (Actuals.Value) across a set of assests (Tasks)."""
        with PublicTestServerConnection.getV1Meta() as v1:
            foundActuals = False
            tasks = v1.Task.select("Name", "Actuals.Value.@Sum").page(size=30)

            for t in tasks:
                if "Actuals.Value.@Sum" in t.data:
                    foundActuals = True
                    break
            else:
                self.skipTest("Test server contains no Tasks")
            if not foundActuals:
                self.skipTest("Test server Tasks contained no Actuals.Value's")

    def test_find_query(self):
        """Creates a story, then does a find to see if it can be located by a partial name from a separate
        connection instance.
        """
        with PublicTestServerConnection.getV1Meta() as v1create:
            createdStory = self._create_story(v1create)

            # make a search term that's just one character shorter
            searchName = createdStory.Name[:-1]
            self.addDetail("search-name", text_content(searchName))

        with PublicTestServerConnection.getV1Meta() as v1find:
            findItems = list(
                v1find.Story.select("Name").find(text=searchName, field="Name")
            )
            findItem = findItems[0]
            size = len(findItems)
            firstName = findItem.Name
            # at the very least we should have found the one we based the search string on
            self.assertThat(size, GreaterThan(0))
            # results need to contain the string we searched for
            self.assertThat(firstName, Contains(searchName))
