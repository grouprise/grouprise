# Feed import for groups

Groups can choose to automatically re-publish articles from their (separate) websites.

The import of such articles relies on RSS or ATOM feeds being published on such websites.

These feed sources are periodically parsed and new items are used for creating local articles.


# Technical details

The following processing is executed every hour (via the `grouprise-tasks` service) for every group with a configured feed URL:

1. The website is retrieved (via a HTTP request).
1. Its content is parsed for typical feed URLs.
1. The URL is retrieved and handed over to the [feedparser](https://pypi.org/project/feedparser/) module.
1. Any objects, which were not previously imported, are processed now and marked as imported.

The process can be triggered manually by executing `grouprisectl import_feeds`.
