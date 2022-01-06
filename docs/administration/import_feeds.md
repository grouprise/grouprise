# Feed import for groups

Groups can choose to automatically re-publish articles from their (separate) websites, e.g. blogs.
This can be configured in the group settings.

The import of articles relies on [RSS or ATOM feeds](https://en.wikipedia.org/wiki/Data_feed) being published on such a website.

These feed sources are periodically parsed.
New items are used for creating local articles.


## Technical details

The following processing is executed every hour (via the `grouprise-tasks` service) for every group with a configured feed URL:

1. The website is retrieved (via a HTTP request).
1. Its content is parsed for typical feed URLs.
1. The URL is retrieved and handed over to the [feedparser](https://pypi.org/project/feedparser/) module.
1. Any objects, which were not previously imported, are processed now and marked as imported.

The process can be triggered manually:
```shell
grouprisectl import_feeds
```
