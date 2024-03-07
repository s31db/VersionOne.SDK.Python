# VersionOne Python SDK #
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

_Fork officially distributed via PyPi (pip) as: __v1pysdk___<br>
_An older version of this package, which follows flows with this version numbering, was distributed as 'v1pysdk-unoffical'_

The VersionOne Python SDK is an open-source and community supported client for the VersionOne API.

As an open-sourced and community supported project, the VersionOne Python SDK is not formally supported by VersionOne.

That said, there are a number of options for getting your questions addressed:

* [StackOverflow](http://stackoverflow.com/questions/tagged/versionone): For asking questions of the VersionOne Development Community.
* [GitHub Issues](https://github.com/s31db/VersionOne.SDK.Python/issues): For submitting issues that others may try to address.

In general, StackOverflow is your best option for getting support for the VersionOne Python SDK.

The source code for the VersionOne Python SDK is free and open-source, and we encourage you to improve it by [submitting pull requests](https://help.github.com/articles/using-pull-requests)!

## Overview

### Instantiating a connection

To interact, you must first create an instance of the `V1Meta` object.  This requires you to specify how to connect to the server.

There are two options, specifying the full URL to your instance directly, or specifying individual details.

```python
from v1pysdk import V1Meta

with V1Meta(
  instance_url = 'http://localhost/VersionOne',
  # any instance, scheme, or address values will be ignored
  username = 'admin',
  password = 'admin'
  ) as v1:
```

Alternatively

```python
from v1pysdk import V1Meta

with V1Meta(
  address = 'localhost',
  instance = 'VersionOne',
  scheme = 'http', #optional, defaults to https
  username = 'admin',
  password = 'admin'
  ) as v1:
```

To authenticate, two methods are provided, username and password as demonstrated above, or Access Tokens.
Tokens are created by logging in to VersionOne via the web interface, going to the user's profile, going to Applications, and creating a new application.  This will provide an Access Token that looks something like `1.2cFHe7NkoO1kOV/x8WLpw1NasJg=`.  KEEP THIS SECRET since it's the secret API access key for your specific user on your instance.

To use an access token, you use it as your password and set the flag indicating it's really an Access Token.  This will no longer require a username to be present.

```python
from v1pysdk import V1Meta

with V1Meta(
  address = 'localhost',
  instance = 'VersionOne',
  password = '1.2cFHe7NkoO1kOV/x8WLpw1NasJg=',
  use_password_as_token=True,
  ) as v1:
```

### Dynamic reflection of all V1 asset types:

  Just instantiate a V1Meta.  All asset types defined on the server are available
  as attributes on the instance.  The metadata is only loaded once, so you must
  create a new instance of V1Meta to pick up metadata changes.  Each asset class
  comes with properties for all asset attributes and operations.

```python
from v1pysdk import V1Meta

with V1Meta(
  instance_url = 'http://localhost/VersionOne',
  username = 'admin',
  password = 'admin'
  ) as v1:

  user = v1.Member(20) # internal numeric ID

  print user.CreateDate, user.Name
```

### Simple access to individual assets:

  Asset instances are created on demand and cached so that instances with the same OID are always
  the same object.  You can retrieve an instance by passing an asset ID to an asset class:

```python
      s = v1.Story(1005)
```

  Or by providing an OID Token:

```python
      s = v1.asset_from_oid('Story:1005')

      print s is v1.Story(1005)   # True
```

### Lazyily loaded values and relations:

  NOTE: Making requests synchronously for attribute access on each object is costly.  We recommend
  using the query syntax to select, filter, aggregate, and retrieve values from related assets 
  in a single HTTP transaction.

  Asset instances are created empty, or with query results if available. The server is
  accessed for attributes that aren't currently fetched.  A basic set of attributes is fetched
  upon the first unfound attribute. 

```python
      epic = v1.Epic(324355)

      # No data fetched yet.
      print epic  #=>  Epic(324355)

      # Access an attribute.
      print epic.Name  #=> "Team Features"

      # Now some basic data has been fetched
      print epic       #=> Epic(324355).with_data({'AssetType': 'Epic',
                           'Description': "Make features easier for new team members", 'AssetState': '64',
                           'SecurityScope_Name': 'Projects', 'Number': 'E-01958', 'Super_Number': 'E-01902',
                           'Scope_Name': 'Projects', 'Super_Name': 'New Feature Development',
                           'Scope': [Scope(314406)], 'SecurityScope': [Scope(314406)],
                           'Super': [Epic(312659)], 'Order': '-24', 'Name': 'Team Features'})
```

      # And further non-basic data is available, but will cause a request.

```python
      print epic.CreateDate   #=>  '2012-05-14T23:45:14.124'
```

  The relationship network can be traversed at will, and assets will be fetched as needed.

```python
    # Freely traverse the relationship graph
    print epic.Super.Scope.Name  #=> 'Products'
```

  Since the metadata is modeled as data, you can find the list of "Basic" attributes:

```python
    basic_attr_names = list( v1.AttributeDefinition
                               .where(IsBasic = "true")
                               .select('Name')
                               .Name
                           )
```

### Operations:

  Operations on assets can be initiated by calling the appropriate method on an asset instance:

```python
      for story in epic.Subs:
        story.QuickSignup() 
```

  The asset instance data will be invalidated upon success, and thus re-fetched on the next
  attribute access.


### Iterating through all assets of a type

  The asset class is iterable to obtain all assets of that type. This is equivalent to the
  "query", "select" or "where" methods when given no arguments.

```python
      # WARNING: Lots of HTTP requests this way.
      members = list(v1.Member)                               # HTTP request to get the list of members.
      print "Members: " + ', '.join(m.Name for m in members)  # HTTP request per member to fetch the Name

      # A much better way, requiring a single HTTP access via the query mechanism.
      members = v1.Member.select('Name')
      print "Members: " + ', '.join(m.Name for m in members)  # HTTP request to return list of members with Name attribute.

      # There is also a shortcut for pulling an attribute off all the results
      members = v1.Member.select('Name')
      print "Members: " + ', '.join(members.Name)

      # Alternative to best way with more explicit indication of what's being done
      members = v1.Member.select('Name')
      members.queryAll()   # forces performing HTTP query to fetch all members' basic details
      print "Members: " + ', '.join(m.Name for m in members)
```

### Queries

#### Query Objects

  the `select()`, `where()`, and `sort()` methods on asset instances return a query object
  upon which you can call more `.where()`'s, `.select()`'s, and `.sort()`'s.  Iterating through
  the query object will run the query.

  the `.first()`, `.queryAll()`, and `.reQueryAll()` methods on a query object will run the query immediately
  and return the appropriate result.

  the `find()` can be used to perform a server-side whole-word match on a field, though it's server intensive,
  can only match one field, and should be used sparing.

  the `page()` can be used to limit results for the purposes of performing server-side paging.

  the `reQueryAll()` can be used like the `queryAll()`, but will clear all previously cached data and re-run
  the HTTP query if any query options have been changed, allowing for easily repeating a query where only
  response limits such as `page()` have changed.

#### Simple query syntax:

  Use `.where(Attr="value", ...)` to introduce "Equals" comparisons, and
  `.select("Attr", ...)` to append to the select list.
  
  Non-"Equal" comparisons are not supported (Use the advanced query syntax instead).

```python
      for s in v1.Story.where(Name='Add feature X to main product"):
          print s.Name, s.CreateDate, ', '.join([owner.Name for owner in s.Owners])

      # Select only some attributes to reduce traffic

      for s in v1.Story.select('Name', 'Owners').where(Estimate='10'):
          print s.Name, [o.Name for o in s.Owners]
```

#### Advanced query, taking the standard V1 query syntax.

  The `filter()` operator will take arbitrary V1 filter terms.

```python
      for s in (v1.Story
                  .filter("Estimate>'5';TotalDone.@Count<'10'")
                  .select('Name')):
          print s.Name
```

#### Limiting results from the server via paging

  It can be easier on the client to have the server perform paging by limiting the number of
  results returned matching a query.  Paging requires a limit on the number of items returned, and
  an index of the first item in the list to return.

  The API allows the index to be left off, which assumes a default start index of 0.

```python
    pageNum = 0
    pageSize = 3
    pageStart = 0
    while True:
        results = ( v1.Story
                     .select('Name')
                     .filter(str(myFilter))
                     .sort('-Name')
                     .page(size=pageSize, start=pageStart) 
                  ) # Requires a new query each time
        if not len(results):
            break;
        print("Page items = " + str(len(results)))
        pageNum += 1
        pageStart += pageSize
        print("Page " + str(pageNum) + " : " + ',   '.join(results.Name))
```

  Alternatively the `reQueryAll()` can be used to force re-querying of the content based on updated 
  query settings to make paging easier to implement.

```python
    pageNum = 0
    pageSize = 3
    pageStart = 0
    results = ( v1.Story
                .select('Name')
                .filter(str(myFilter))
                .sort('-Name')
               )

    while True:
        results = results.page(size=pageSize, start=pageStart).reQueryAll()
        if not len(results):
            break;
        pageNum += 1
        pageStart += pageSize
        print("Page " + str(pageNum) + " : " + ',   '.join(results.Name))
```

#### Sorting

  Sorting can be included in the query by specifying the order of the columns to sort on, and whether
  those columns should be sorted ascending or descending.  The default sort order is ascending.

  sort() operates like select(), where field names are listed in quotes and may be listed as separate arguments
  to a single sort call, separate sort calls, or a mixture of both.
  Sorting descending requires the field name to be prefaced with a dash, '-'.  
  Fields may only be listed in the sort order once, with repeats being ignored.

  To sort in reverse alphabetical order of names, then on Estimate time, then on Detailed Estimate time:

```python
    results = v1.Story.select('Name').filter(str(myFilter)).sort('-Name','Estimate').sort('DetailedEstimate')
    print '\n'.join(results.Name)
```
#### Matched searching

  Searching, while possible, is very server intensive and should be avoided as much as possible.  Server-side
  searching can be whole-word matched within a single field.  For this reason it should be significantly limited
  with appropriate filter/where commands.

```python
    results = v1.Story.select('Name').filter(str(myFilter)).find('Get a', field='Name')
    print ', '.join(results.Name) #=> Get a handle on filtering, Get a toolkit for ease of use
```
#### Limiting results from the server via paging

  It can be easier on the client to have the server perform paging by limiting the number of
  results returned matching a query.  Paging requires a limit on the number of items returned, and
  an index of the first item in the list to return.

  The API allows the index to be left off, which assumes a default start index of 0.

```python
    pageNum = 0
    pageSize = 3
    pageStart = 0
    while True:
        results = ( v1.Story
                     .select('Name')
                     .filter(str(myFilter))
                     .sort('-Name')
                     .page(size=pageSize, start=pageStart) 
                  ) # Requires a new query each time
        if not len(results):
            break;
        print("Page items = " + str(len(results)))
        pageNum += 1
        pageStart += pageSize
        print("Page " + str(pageNum) + " : " + ',   '.join(results.Name))
```

  Alternatively the `reQueryAll()` can be used to force re-querying of the content based on updated 
  query settings to make paging easier to implement.

```python
    pageNum = 0
    pageSize = 3
    pageStart = 0
    results = ( v1.Story
                .select('Name')
                .filter(str(myFilter))
                .sort('-Name')
               )

    while True:
        results = results.page(size=pageSize, start=pageStart).reQueryAll()
        if not len(results):
            break;
        pageNum += 1
        pageStart += pageSize
        print("Page " + str(pageNum) + " : " + ',   '.join(results.Name))
```

#### Sorting

  Sorting can be included in the query by specifying the order of the columns to sort on, and whether
  those columns should be sorted ascending or descending.  The default sort order is ascending.

  sort() operates like select(), where field names are listed in quotes and may be listed as separate arguments
  to a single sort call, separate sort calls, or a mixture of both.
  Sorting descending requires the field name to be prefaced with a dash, '-'.  
  Fields may only be listed in the sort order once, with repeats being ignored.

  To sort in reverse alphabetical order of names, then on Estimate time, then on Detailed Estimate time:

```python
    results = v1.Story.select('Name').filter(str(myFilter)).sort('-Name','Estimate').sort('DetailedEstimate')
    print '\n'.join(results.Name)
```
#### Matched searching

  Searching, while possible, is very server intensive and should be avoided as much as possible.  Server-side
  searching can be whole-word matched within a single field.  For this reason it should be significantly limited
  with appropriate filter/where commands.

```python
    results = v1.Story.select('Name').filter(str(myFilter)).find('Get a', field='Name')
    print ', '.join(results.Name) #=> Get a handle on filtering, Get a toolkit for ease of use
```

#### Advanced selection, taking the standard V1 selection syntax.

  The `select()` operator will allow arbitrary V1 "select" terms, and will add
  them to the "data" mapping of the result with a key identical to the term used.

```python
    select_term = "Workitems:PrimaryWorkitem[Status='Done'].Estimate.@Sum"
    total_done = ( v1.Timebox
                     .where(Name="Iteration 25")
                     .select(select_term)
                 )
    for result in total_done:
      print "Total 'Done' story points: ", result.data[select_term]
```

#### Advanced Filtering and Selection

  get a list of all the stories dedicated people are working on

```python
      writer = csv.writer(outfile)
      results = (
        v1.Story
          .select('Name', 'CreateDate', 'Estimate', 'Owners.Name')
          .filter("Owners.OwnedWorkitems.@Count='1'")
          )
      for result in results:
          writer.writerow((result['Name'], ', '.join(result['Owners.Name'])))
```

### Simple creation syntax:

  GOTCHA: All "required" attributes must be set, or the server will reject the data.

```python
      from v1pysdk import V1Meta
      v1 = V1Meta(username='admin', password='admin')
      new_story = v1.Story.create(
        Name = 'New Story',
        Scope = v1.Scope.where(Name='2012 Projects').first()
        )
      # creation happens immediately. No need to commit.
      print new_story.CreateDate
      new_story.QuickSignup()
      print 'Owners: ' + ', '.join(o.Name for o in story.Owners)
```

### Simple update syntax.

  Nothing is written until `V1Meta.commit()` is called, and then all dirty assets are written out.

```python
      story = v1.Story.where(Name='Super Cool Feature do over').first()
      story.Name = 'Super Cool Feature Redux'
      story.Owners = v1.Member.where(Name='Joe Koberg')      
      errors = v1.commit()  # flushes all pending updates to the server
      if not errors:
          print("Successfully committed!")
      else:
          for e in errors:
              raise e 
```

  The V1Meta object also serves as a context manager which will commit dirty object on exit.

```python
      with V1Meta() as v1:
        story = v1.Story.where(Name='New Features').first()
        story.Owners = v1.Member.where(Name='Joe Koberg')
        
      print "Story committed implicitly."
```

### Attachment Contents

  Attachment file bodies can be fetched or set with the special "file_data" attribute on Attachment instances. 

  See the v1pysdk/tests/test_attachment.py file for a full example.

### As Of / Historical Queries

  Queries can return data "as of" a specific point in the past.  The `.asof()` query term can
  take a list (or multiple positional parameters) of timestamps or strings in ISO date format.
  The query is run for each timestamp in the list.  A single iterable is returned that will
  iterate all of the collected results.  The results will all contain a data item `'AsOf'` with
  the "As of" date of that item.  
  Note that the "As of" date is not the date of the previous change to the item, but rather is exactly the 
  same date passed into the query.  
  Also note that timestamps such as "2012-01-01" are taken to be at the midnight starting that day, which
  naturally excludes any activity happening during that day.  You may want to specify a timestamp
  with a specific hour, or of the following day.
  The timezone used when performing these comparisons is the timezone configured for the user specified
  in the V1Meta object, and the time comparison is performed based on the time as determined by the 
  server.

```python
      with V1Meta() as v1:
        results = (v1.Story
                     .select("Owners")
                     .where(Name="Fix HTML5 Bug")
                     .asof("2012-10-10", "2012-10-11")
                  )
        for result in results:
            print result.data['AsOf'], [o.Name for o in result.Owners]
```

### Polling (TODO)

  A simple callback api will be available to hook asset changes

```python
      from v1meta import V1Meta
      from v1poll import V1Poller

      MAILBODY = """
      From: VersionOne Notification <notifier@versionone.mycorp.com>
      To: John Smith <cto@mycorp.com>

      Please take note of the high risk story '{0}' recently created in VersionOne.

      Link: {1}


      Thanks,

      Your VersionOne Software
      """.lstrip()

      def notify_CTO_of_high_risk_stories(story):
        if story.Risk > 10:
            import smtplib, time
            server = smtplib.SMTP('smtp.mycorp.com')
            server.sendmail(MAILBODY.format(story.Name, story.url))
            server.quit()
            story.CustomNotificationLog = (story.CustomNotificationLog +
                "\n Notified CTO on {0}".format(time.asctime()))

      with V1Meta() as v1:
        with V1Poller(v1) as poller:
          poller.run_on_new('Story', notify_CTO_of_high_risk_stories)

      print "Notification complete and log updated."

```

## Performance notes

  An HTTP request is made to the server the first time each asset class is referenced.

  Assets do not make a request until a data item is needed from them. Further attribute access
  is cached if a previous request returned that attribute. Otherwise a new request is made.

  The fastest way to collect and use a set of assets is to query with the attributes
  you expect to use included in the select list.  The entire result set will be returned
  in a single HTTP transaction if you manually call one of the methods that triggers a full query.
  These methods include `__iter__()` (e.g. .join() uses this), `__len__()`, `queryAll()`, and `reQueryAll()`.

  Writing to assets does not require reading them; setting attributes and calling the commit
  function does not invoke the "read" pipeline.  Writing assets requires one HTTP POST per dirty
  asset instance.

  When an asset is committed or an operation is called, the asset data is invalidated and will
  be read again on the next attribute access.  Grouping your updates then calling queryAll() on a fresh
  query is a good way to enhance performance.

  GOTCHA: `reQueryAll()` tracks the dirty state of the query object separately from the way asset data
    is invalidated following an update.  Unless the terms of the query have been changed, the `reQueryAll`
    won't update the cached data and a new query will be generated for each invalidated data item accessed.
    To avoid this, adding and then restoring a query term on the query object can be used to cause the
    re-query to actually occur.

  `reQueryAll()` can be very useful when implementing paging, changing the sorting, etc, but it should
  be used with care.  It clears all cached data, so any fields that were not included in the original query
  and have since been retrieved are also cleared.  Accessing those fields will prompt the same individual
  query as before.  To avoid this problem, either include the extra field(s) in your initial query, or
  create a new query object for the updated query terms.

## TODO

  - [ ] Make things Moment-aware

  - [ ] Convert types between client and server (right now everything is a string)

  - [ ] Add debug logging

  - [ ] Beef up test coverage

  - [ ] Asset creation templates and creation "in context of" other asset

  - [ ] Correctly handle multi-valued attributes including removal of values.

## Installation

run `pip install .`, or just copy the v1pysdk folder into your PYTHONPATH.

## Testing

Run 
```
bash
$ python setup.py test
```

from within your virtual environment. If all tests ran correctly, it will say:

```
----------------------------------------------------------------------
Ran <X> tests in <Y> s

OK

```
