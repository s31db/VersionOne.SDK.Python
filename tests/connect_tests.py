from testtools import TestCase
from testtools.assertions import assert_that
from testtools.matchers import Equals
from testtools.content import text_content

from urllib.error import HTTPError

from xml.etree.ElementTree import fromstring

from v1pysdk.client import V1Server
from v1pysdk import V1Meta
from .common_test_server import PublicTestServerConnection


class TestV1Connection(TestCase):
    def test_connect(self):
        username = PublicTestServerConnection.username
        password = PublicTestServerConnection.password
        address = PublicTestServerConnection.address
        instance = PublicTestServerConnection.instance
        self.addDetail("URL", text_content(address + "/" + instance))
        self.addDetail("username", text_content(username))

        server = V1Server(
            address=address, username=username, password=password, instance=instance
        )
        # The story names, but limit to only the first result so we don't get inundated with results
        code, body = server.fetch("/rest-1.v1/Data/Story?sel=Name&page=1,0")
        self.addDetail("Code", text_content(str(code)))
        self.addDetail("Body", text_content(str(body)))

        elem = fromstring(body)
        self.assertThat(elem.tag, Equals("Assets"))

    def test_meta_connect_instance_url(self):
        v1 = None
        self.addDetail("URL", text_content(PublicTestServerConnection.instance_url))
        self.addDetail("username", text_content(PublicTestServerConnection.username))
        try:
            v1 = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                username=PublicTestServerConnection.username,
                password=PublicTestServerConnection.password,
            )
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error trying to create connection: " + str(e),
            )

        try:
            items = v1.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from connection: " + str(e),
            )

    def test_meta_connect_instance_and_address(self):
        v1 = None
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))
        self.addDetail("username", text_content(PublicTestServerConnection.username))

        try:
            v1 = V1Meta(
                address=PublicTestServerConnection.address,
                instance=PublicTestServerConnection.instance,
                username=PublicTestServerConnection.username,
                password=PublicTestServerConnection.password,
            )
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error trying to create connection: " + str(e),
            )

        try:
            items = v1.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from connection: " + str(e),
            )

    def test_meta_connect_instance_url_overrides_separate(self):
        v1 = None
        address = self.getUniqueString()  # garbage
        instance = self.getUniqueString()  # garbage
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail(
            "instance-url", text_content(PublicTestServerConnection.instance_url)
        )
        self.addDetail("instance", text_content(address))
        self.addDetail("username", text_content(instance))

        try:
            v1 = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                address=address,
                instance=instance,
                username=PublicTestServerConnection.username,
                password=PublicTestServerConnection.password,
            )
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error trying to create connection: " + str(e),
            )

        try:
            items = v1.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from connection: " + str(e),
            )

    def test_meta_connect_oauth(self):
        v1 = None
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))

        try:
            v1 = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                # no username
                password=PublicTestServerConnection.token,
                use_password_as_token=True,
            )
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error trying to create connection: " + str(e),
            )

        try:
            items = v1.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from connection: " + str(e),
            )

    def test_meta_connect_oauth_ignores_username(self):
        v1 = None
        username = self.getUniqueString()  # garbage
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))
        self.addDetail("username", text_content(username))

        try:
            v1 = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                username=username,
                password=PublicTestServerConnection.token,
                use_password_as_token=True,
            )
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error trying to create connection: " + str(e),
            )

        try:
            items = v1.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from connection: " + str(e),
            )

    def test_connect_fails_when_invalid(self):
        v1bad = None
        username = self.getUniqueString()  # garbage
        password = self.getUniqueString()  # garbage
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))
        self.addDetail("bad-username", text_content(username))
        self.addDetail("bad-password", text_content(password))

        try:
            v1bad = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                username=username,
                password=password,
                use_password_as_token=False,
            )
            # we have to try to use it to get it to connect and fail
            items = v1bad.Story.select("Name").page(size=1)
            items.first()  # run the query
        except HTTPError as e:
            assert_that(
                e.code,
                Equals(401),
                message="Connection failed for reasons other than authorization",
            )
        else:
            assert_that(
                False, Equals(True), message="Connection succeeded with bad credentials"
            )

    def test_reconnect_succeeds_after_invalid(self):
        v1bad = None
        username = self.getUniqueString()  # garbage
        password = self.getUniqueString()  # garbage
        self.addDetail("bad-username", text_content(username))
        self.addDetail("bad-password", text_content(password))

        try:
            v1bad = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                username=username,
                password=password,
                use_password_as_token=False,
            )
            items = v1bad.Story.select("Name").page(size=1)
            items.first()  # run the query
        except HTTPError as e:
            assert_that(
                e.code,
                Equals(401),
                message="Connection failed for reasons other than authorization",
            )
        else:
            assert_that(
                False,
                Equals(True),
                message="First connection succeeded with bad credentials, cannot continue test",
            )

        v1good = None
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))

        # Connect correctly first
        try:
            v1good = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                password=PublicTestServerConnection.token,
                use_password_as_token=True,
            )
            items = v1good.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from good connection: " + str(e),
            )

    def test_reconnect_fails_when_invalid(self):
        v1good = None
        self.addDetail("address", text_content(PublicTestServerConnection.address))
        self.addDetail("instance", text_content(PublicTestServerConnection.instance))

        # Connect correctly first
        try:
            v1good = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                password=PublicTestServerConnection.token,
                use_password_as_token=True,
            )
            items = v1good.Story.select("Name").page(size=1)
            items.first()  # run the query
        except Exception as e:
            assert_that(
                False,
                Equals(True),
                message="Error running query from good connection, cannot perform test: "
                + str(e),
            )

        v1bad = None
        username = self.getUniqueString()  # garbage
        password = self.getUniqueString()  # garbage
        self.addDetail("bad-username", text_content(username))
        self.addDetail("bad-password", text_content(password))

        try:
            v1bad = V1Meta(
                instance_url=PublicTestServerConnection.instance_url,
                username=username,
                password=password,
                use_password_as_token=False,
            )
            items = v1bad.Story.select("Name").page(size=1)
            items.first()  # run the query
        except HTTPError as e:
            assert_that(
                e.code,
                Equals(401),
                message="Connection failed for reasons other than authorization",
            )
        else:
            assert_that(
                False,
                Equals(True),
                message="Second connection succeeded with bad credentials",
            )
