import logging

from urllib.request import (
    Request,
    HTTPBasicAuthHandler,
    HTTPCookieProcessor,
    HTTPPasswordMgrWithDefaultRealm,
    build_opener,
)
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.parse import urlunparse, urlparse

from xml.etree import ElementTree

NTLM_FOUND = False

try:
    from ntlm3.HTTPNtlmAuthHandler import HTTPNtlmAuthHandler
except ImportError:
    logging.warn("Windows integrated authentication module (ntlm) not found.")
else:
    NTLM_FOUND = True

    class CustomHTTPNtlmAuthHandler(HTTPNtlmAuthHandler):
        # The following code was a recommended change to the existing.  However unittesting proves that it
        # and the existing obscure authentication failures.  There seems to be no actual reason to be doing
        # this unless there was a particular issue with the HTTPNtlmAuthHandler in some specific version of
        # urllib2 for Python2 that no longer exists.  Using the default handler provably works correctly
        pass

    # """ A version of HTTPNtlmAuthHandler that handles errors (better).
    #    The default version doesn't use `self.parent.open` in it's
    #    error handler, and completely bypasses the normal `OpenerDirector`
    #    call chain, most importantly `HTTPErrorProcessor.http_response`,
    #    which normally raises an error for 'bad' http status codes..
    # """
    # def http_error_401(self, req, fp, code, msg, hdrs):
    #    response = HTTPNtlmAuthHandler.http_error_401(self, req, fp, code, msg, hdrs)
    #    if not (200 <= response.code < 300):
    #        if response.code == 401:
    #            raise HTTPError(req.get_full_url(), response.code, response.msg, response.info(), fp)
    #        else:
    #            response = self.parent.error(
    #                'http', req, response, response.code, response.msg,
    #                response.info())
    #    return response


class V1Error(Exception):
    pass


class V1AssetNotFoundError(V1Error):
    pass


class V1Server(object):
    """Accesses a V1 HTTP server as a client of the XML API protocol"""

    def __init__(
        self,
        address="localhost",
        instance="VersionOne.Web",
        username="",
        password="",
        scheme="https",
        instance_url=None,
        logparent=None,
        loglevel=logging.ERROR,
        use_password_as_token=False,
        use_oauth_path=False,
    ):
        """
        scheme and object's instance_url attributes.
        If *token* is not None a HTTP header will be added to each request.
        :param address: target hostname
        :param instance: instance
        :param username: credentials (username)
        :param password: credentials (password) or (authentication token)
        :param scheme: HTTP scheme
        :param instance_url: instance URL
        :param logparent: logger prefix
        :param loglevel: logging level
        :param use_password_as_token: Use password as token
        :param use_oauth_path: Use OAuth path
        """
        modulelogname = "v1pysdk.client"
        logname = "%s.%s" % (logparent, modulelogname) if logparent else None
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(loglevel)
        if instance_url:
            self.instance_url = instance_url
            parsed = urlparse(instance_url)
            self.address = parsed.netloc
            self.instance = parsed.path.strip("/")
            self.scheme = parsed.scheme
        else:
            self.address = address
            self.instance = instance.strip("/")
            self.scheme = scheme
            self.instance_url = self.build_url("")
        self.AUTH_HANDLERS = [HTTPBasicAuthHandler]
        if NTLM_FOUND:
            self.AUTH_HANDLERS.append(CustomHTTPNtlmAuthHandler)
        self.username = username
        self.password = password
        self.use_password_as_token = use_password_as_token
        self._install_opener()
        # On-premise installations will not allow token based auth on usual path
        if use_oauth_path is True:
            self.rest_api_path = "rest-1.oauth.v1"
        else:
            self.rest_api_path = "rest-1.v1"

    def _install_opener(self):
        base_url = self.build_url("")
        password_manager = HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
            realm=None, uri=base_url, user=self.username, passwd=self.password
        )
        handlers = [
            HandlerClass(password_manager) for HandlerClass in self.AUTH_HANDLERS
        ]
        self.opener = build_opener(*handlers)
        if self.use_password_as_token:
            self.opener.addheaders.append(("Authorization", "Bearer " + self.password))
        self.opener.add_handler(HTTPCookieProcessor())

    def http_get(self, url):
        request = Request(url)
        request.add_header("Content-Type", "text/xml;charset=UTF-8")
        response = self.opener.open(request)
        return response

    def http_post(self, url, data=""):
        encoded_data = data
        # encode to byte data as is needed if  it's a string
        if isinstance(data, str):
            encoded_data = data.encode("utf-8")
        request = Request(url, encoded_data)
        request.add_header("Content-Type", "text/xml;charset=UTF-8")
        response = self.opener.open(request)
        return response

    def build_url(self, path, query="", fragment="", params=""):
        """So we dont have to interpolate urls ad-hoc"""
        path = self.instance + "/" + path.strip("/")
        if isinstance(query, dict):
            query = urlencode(query)
        url = urlunparse((self.scheme, self.address, path, params, query, fragment))
        self.logger.debug("Build URL: %s", url)
        return url

    def _debug_headers(self, headers):
        self.logger.debug("Headers:")
        for hdr in str(headers).split("\n"):
            self.logger.debug("  %s" % hdr)

    def _debug_body(self, body, headers):
        try:
            ctype = headers["content-type"]
        except AttributeError:
            ctype = None
        if ctype is not None and ctype[:5] == "text/":
            self.logger.debug("Body:")
            for line in str(body).split("\n"):
                self.logger.debug("  %s" % line)
        else:
            self.logger.debug(
                "Body: non-textual content (Content-Type: %s). Not logged." % ctype
            )

    def fetch(self, path, query="", postdata=None):
        """Perform an HTTP GET or POST depending on whether postdata is present"""
        url = self.build_url(path, query=query)
        self.logger.debug("URL: %s" % url)
        try:
            if postdata is not None:
                if isinstance(postdata, dict):
                    postdata = urlencode(postdata)
                    self.logger.debug("postdata: %s" % postdata)
                response = self.http_post(url, postdata)
            else:
                response = self.http_get(url)
            body = response.read()
            self._debug_headers(response.headers)
            self._debug_body(body, response.headers)
            return None, body
        except HTTPError as e:
            if e.code == 401:
                raise
            body = e.fp.read()
            self._debug_headers(e.headers)
            self._debug_body(body, e.headers)
            return e, body

    def handle_non_xml_response(self, body, exception, msg, postdata):
        if exception.code >= 500:
            # 5XX error codes mean we won't have an XML response to parse
            self.logger.error("{0} during {1}".format(exception, msg))
            if postdata is not None:
                self.logger.error(postdata)
            raise exception

    def get_xml(self, path, query="", postdata=None):
        verb = "HTTP POST to " if postdata else "HTTP GET from "
        msg = verb + path
        self.logger.info(msg)
        # print(path, query)
        exception, body = self.fetch(path, query=query, postdata=postdata)
        if exception:
            self.handle_non_xml_response(body, exception, msg, postdata)

        self.logger.warning("{0} during {1}".format(exception, msg))
        if postdata is not None:
            self.logger.warning(postdata)

        document = ElementTree.fromstring(body)
        if exception:
            exception.xmldoc = document
            if exception.code == 404:
                raise V1AssetNotFoundError(exception)
            elif exception.code == 400:
                raise V1Error("\n" + str(body))
            else:
                raise V1Error(exception)
        return document

    def get_asset_xml(self, asset_type_name, oid, moment="none"):
        """
        Returns an array of asset xmls. possible moment values are:
        'every' or 'none' or the specific moment
        """
        if moment == "none" or moment is None:
            path = "/{0}/Data/{1}/{2}".format(self.rest_api_path, asset_type_name, oid)
            # return self.get_xml(path) # old style, not history-aware
            return self.get_xml(path)

        elif moment == "every":
            path = "/{0}/Hist/{1}/{2}".format(self.rest_api_path, asset_type_name, oid)
            return self.get_xml(path)

        elif isinstance(moment, int):
            path = "/{0}/Data/{1}/{2}/{3}".format(
                self.rest_api_path, asset_type_name, oid, moment
            )
            return self.get_xml(path)

        else:
            raise V1Error("Invalid moment passed for asset.")

    def get_query_xml(self, api, asset_type_name, where=None, sel=None):
        path = "/{0}/{1}/{2}".format(self.rest_api_path, api, asset_type_name)
        query = {}
        if where is not None:
            query["Where"] = where
        if sel is not None:
            query["sel"] = sel
        return self.get_xml(path, query=query)

    def get_meta_xml(self, asset_type_name):
        path = "/meta.v1/{0}".format(asset_type_name)
        return self.get_xml(path)

    def execute_operation(self, asset_type_name, oid, opname):
        path = "/{0}/Data/{1}/{2}".format(self.rest_api_path, asset_type_name, oid)
        query = {"op": opname}
        return self.get_xml(path, query=query, postdata={})

    def get_attr(self, asset_type_name, oid, attrname, moment=None):
        if moment:
            path = "/{0}/Data/{1}/{2}/{4}/{3}".format(
                self.rest_api_path, asset_type_name, oid, attrname, moment
            )
        else:
            path = "/{0}/Data/{1}/{2}/{3}".format(
                self.rest_api_path, asset_type_name, oid, attrname
            )
        return self.get_xml(path)

    def create_asset(self, asset_type_name, xmldata, context_oid=""):
        body = ElementTree.tostring(xmldata, encoding="utf-8")
        query = {}
        if context_oid:
            query = {"ctx": context_oid}
        path = "/{0}/Data/{1}".format(self.rest_api_path, asset_type_name)
        return self.get_xml(path, query=query, postdata=body)

    def update_asset(self, asset_type_name, oid, update_doc):
        newdata = ElementTree.tostring(update_doc, encoding="utf-8")
        path = "/{0}/Data/{1}/{2}".format(self.rest_api_path, asset_type_name, oid)
        return self.get_xml(path, postdata=newdata)

    def get_attachment_blob(self, attachment_id, blobdata=None):
        path = "/attachment.v1/{0}".format(attachment_id)
        exception, body = self.fetch(path, postdata=blobdata)
        if exception:
            raise exception
        return body

    set_attachment_blob = get_attachment_blob

    def get(self, url):
        try:
            request = Request(url)
            request.add_header("Content-Type", "text/xml;charset=UTF-8")
            response = self.opener.open(request)
            body = response.read()
            return None, body
        except HTTPError as e:
            if e.code == 401:
                raise
            body = e.fp.read()
            return e, body
