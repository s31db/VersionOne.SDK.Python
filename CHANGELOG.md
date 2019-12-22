# Changelog
2018-07-02 v0.6.2 - Fix a critical memoization bug, error reponse printing, some HTTP/PUT calls, authentication error handling

  A critical memoization bug caused by the decorator being used prevented the same field of more than
  one item of the same type from being updated in a single invocation of the Python intepreter; i.e. it's
  only possible to update the Title of one Story within a Python script, regardless of how many V1Meta objects
  are created.  It also prevented the V1Meta objects from being created with separate credentials.

  Bug in how HTTP 400 responses were handled caused an exception to be thrown during handling and raising of
  an exception, preventing the actual error response provided with the HTTP 400 from being printed.

  Bug in how NTLM authentication was handled prevented the HTTP 401 authentication error from being raised and
  handled so the errors would silently fail without the GET/POST command completing.

  A bug in the creation of the HTTP POST commands in Python3 caused a TypeError exception to be thrown when no 
  data payload was needed.  This prevent Operations with no arguments from being used on V1 objects.

  Unittests were added to ensure some Operations work properly.  Connection tests to ensure bad credentials
  result in an identifable failed connection were also added.  Tests specifically to ensure separation of
  credentials between different V1Meta objects within the same tests produce different results, thereby
  checking that memoization is working properly on a per-V1Meta object basis were also added.

2018-06-21 v0.6.1 - Fix a new item creation bug and added unittests for creation

2018-06-21 v0.6 - Rebased to include some historical changes that were lost between 0.4 and 0.5.

  Fixed the tests so they can be run and succeed, including adding tests that check functionality
  of connections and some basic querying.

  Critical lost differences that were recovered:
    OAuth token support
    memoization fixes

2018-06-13 v0.5.1 - PyPi upload so it's available via pip as "v1pysdk".

2018-06-12 v0.5 - Dynamic Python3 support added.

  Add page(), sort(), queryAll(), find(), max_length(), length(), and support for len() usage to 
  the query objects.

  Primary repository moved to a fork that's maintained.

2013-09-27 v0.4 - A correction has been made to the multi-valued relation setter code.  It used the
  wrong value for the XML "act" attribute, so multi-value attributes never got set correctly.  Note
  that at this time, there is no way to un-set a value from a multi-valued relation.

2013-07-09 v0.3 - To support HTTPS, A "scheme" argument has been added to the V1Meta and V1Client
  constructors.

  An instance_url keyword argument was added to V1Meta and V1Client. This argument can be
  specified instead of the address, instance_path, scheme, and port arguments.

  A performance enhancement was made to calls such as "list(v1.Story.Name)".  The requested
  attribute is added to the select list if it's not present, thus preventing an HTTP GET
  for each matched asset.

  Some poor examples were removed and logging cleaned up in places.

  Fix some issues with NTLM and urllib2. (thanks campbellr)

  Missing attributes now return a None-like object can be deferenced to any depth. (thanks bazsi)
