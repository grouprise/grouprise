# Contribute to the documentation

The grouprise documentation for administrators and developers can be found below `docs/` in the grouprise repository.

The documentation is rendered via [Sphinx](https://sphinx-doc.org/).

Most documentation files are written in markdown format (`*.md`).
A few documentation files (especially `index` files for defining hierarchies) are written as restructured text.

Simply run `make doc` in order to build the documentation.
Afterwards you can browse the generated documentation: `build/doc/html/index.html`

## Markdown format

Markdown is a convenient format for writing formatted text, but sadly our currently used parser ([recommonmark](https://recommonmark.readthedocs.io/en/latest/)) does not offer all structuring capabilities offered by Sphinx.

The following hints may help you:

* referencing a section in a different file:
    * sadly such references need to rely on automatically generated HTML anchors (e.g. `configuration/options.html#stylesheets`)
    * the path needs to be relative (i.e. add `../` in front, depending on the nesting level of the current document)
* referencing a file:
    * use something like `/administration/configuration/options`
    * in contrast to referencing a section (see above), the path can be absolute and should not include the `.html` extension

## Graphs (via graphviz)

The [graphviz extension](https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html) for Sphinx allows to use render graphs in documentation files:

```rst
.. graphviz::

    graph {
        A -- B -- C;
        A -- D -- C;
    }
```

Such graphs are (at the moment) only available in `rst` files.
