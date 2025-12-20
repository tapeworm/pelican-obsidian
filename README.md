Obsidian: A Plugin for Pelican
============================

<!-- [![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/series/build)](https://github.com/pelican-plugins/series/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-series)](https://pypi.org/project/pelican-series/)
![License](https://img.shields.io/pypi/l/pelican-series?color=blue) -->

Obsidian is a pelican plugin that allows you to use the syntax used within Obsidian and when pelican then renders these posts it won't look weird or out of place.

Phrased differently, if you don't like that `#` is included in the name of the tag when you name it `#my-tag` and you think that internal pelican links are difficult to remember and would like to use `[[ my link ]]` as an internal link instead this plugin would be for you.

If the article doesn't exist it will return text only. That way, there is a possibility of clearly separating posts that should belong on the blog and linked as such vs posts that should only belong inside Obsidian.


Installation
------------

This plugin can be installed via:

    # not yet on pypi, but when it is you can install it with.
    pip install pelican-obsidian
    
    # meanwhile you can install using this repo.
    pip install git+git://github.com/jonathan-s/pelican-obsidian@main#egg=pelican-obsidian


Add `'obsidian'` to the `PLUGINS` list in your Pelican config:

```
PLUGINS = [
    'obsidian',
]
```

Usage
-----

In the tags section you will be able to use `#` without that being reflected in the actual name of the tag. In other words.

```
Tags: #my-tag

# reflects as
my-tag in the html output.
```

Links follow this format:

```
[[note name]]
[[note name | custom link text]]
```

Files are similar:

```
![[photo.jpg]]
![[photo.jpg | custom alt text]]
```

They explain more about the syntax in the section on [how to embed files](https://help.obsidian.md/How+to/Embed+files)


Jinja2 Templating
-----------------

You can use Jinja2 templating within your Markdown files to insert variables dynamically. This is useful for sharing configuration between your Obsidian vault and your Pelican site.

To use this feature, you must install the optional dependencies:

    pip install pelican-obsidian[jinja2]

Enable Jinja2 processing for a note by adding `jinja2: true` to its frontmatter:

```yaml
---
title: My Dynamic Note
jinja2: true
---

Hello, {{ MY_VARIABLE }}!
```

### Variable Sources & Precedence

Variables are loaded from the following sources, in order of precedence (highest to lowest):

1.  **File Metadata**: Variables defined in the note's frontmatter override everything else.
2.  **OS Environment**: System environment variables.
3.  **`.env` File**: Variables from a `.env` file in the project root (loaded via `python-dotenv`).
4.  **`dot-env` Note**: Variables defined in a specific note in your Obsidian vault (default: `dot-env`).

### Configuration

You can configure the following settings in your `pelicanconf.py`:

*   `OBSIDIAN_DOT_ENV_NOTE` (default: `'dot-env'`): The name of the note in your vault that acts as a global source of variables. This note should contain `KEY=VALUE` pairs (like a `.env` file).
*   `OBSIDIAN_JINJA_FILTERS` (default: `{}`): A dictionary of custom Jinja2 filters to register.

    ```python
    def my_upper_filter(value):
        return value.upper()

    OBSIDIAN_JINJA_FILTERS = {
        'my_upper': my_upper_filter,
    }
    ```


Future features
---------------
- Embed files or sections as described [here](https://help.obsidian.md/How+to/Format+your+notes)
- Task list?
- Support .rst?
- don't generate links for drafts


Implemented Features
----------------- 
- Apply the same linking for pages.


<!-- Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/pelican-plugins/series/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html -->

License
-------

This project is licensed under the MIT license.
