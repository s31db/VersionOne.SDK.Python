from testtools import TestCase
from testtools.assertions import assert_that
from testtools.content import text_content
from testtools.matchers import Equals

import v1pysdk
from .common_test_server import PublicTestServerConnection
from .common_test_setup import TestV1CommonSetup


class TestV1Operations(TestV1CommonSetup):
    def test_quick_close_and_reopen(self):
        """Creates a story, quick closes it, then reopens it, then quick closes again"""
        with PublicTestServerConnection.getV1Meta() as v1:
            newStory = None
            try:
                newStory = self._create_story(v1)
            except Exception as e:
                assert_that(
                    False,
                    Equals(True),
                    message="Unable to setup by creating initial test story: " + str(e),
                )

            assert_that(
                newStory.IsClosed,
                Equals("false"),
                message="New story created already closed, cannot test",
            )

            try:
                newStory.QuickClose()
            except Exception as e:
                assert_that(
                    False,
                    Equals(True),
                    message="Error while quick closing story: " + str(e),
                )

            try:
                v1.commit()
            except Exception as e:
                assert_that(
                    False,
                    Equals(True),
                    message="Error while syncing commits after close: " + str(e),
                )

            assert_that(
                newStory.IsClosed,
                Equals("true"),
                message="Story didn't close when QuickClose() was called",
            )

            try:
                newStory.Reactivate()
            except Exception as e:
                assert_that(
                    False,
                    Equals(True),
                    message="Error while reactivating story: " + str(e),
                )

            try:
                v1.commit()
            except Exception as e:
                assert_that(
                    False,
                    Equals(True),
                    message="Error while syncing commits after reactivation: " + str(e),
                )

            assert_that(
                newStory.IsClosed,
                Equals("false"),
                message="Story didn't re-open when Reactivate() was called",
            )

            # "cleanup" by closing the story
            newStory.QuickClose()
            v1.commit()
