# Development

## Prepare a local development environment

Install the required dependencies:

* `git`
* `make`
* `python3`
* `nodejs`

For example in Debian:
```shell
apt install git make python3 nodejs
```

Clone the repository:
```shell
git clone https://git.hack-hro.de/grouprise/grouprise.git
```

Run the development server locally:
```shell
make app_run
```

Now you can visit the web interface of the development system in your browser: http://localhost:5000/


## Translate content

Run `make django-translate` for collecting the translatable strings and for opening a translation
editor.
Add the argument `PO_EDITOR=`, if you want to skip the editor call.

The translation files (`*.po`) are stored below `grouprise/locale`.
They can be edited manually with any suitable editor.


## Profile specific operations

Sometimes it may be useful to analyze the runtime behavior of specific parts of the code.
The management command `profile_commands` can be used for this purpose.

Example: export the profiling information of an execution of the `update_search_index` task:
```shell
printf '%s\n' \
        'from haystack.management.commands.update_index import Command as UpdateIndexCommand' \
        'UpdateIndexCommand().handle(remove=True)' \
    | grouprisectl profile_commands --output-file=/tmp/out.profile
```

The above usage of `grouprisectl` implies the execution within a *grouprise* deployment.
For local development environments, you should use `python3 manage.py` instead.

The profiling export file can now be loaded into any Python profile visualization tool, e.g.
[RunSnakeRun](http://www.vrplumber.com/programming/runsnakerun/).
