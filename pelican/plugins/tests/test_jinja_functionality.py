
import pytest
from pathlib import Path
from pelican.generators import ArticlesGenerator
from pelican.tests.support import get_settings
# Import module to patch it
import pelican.plugins.obsidian.obsidian as obsidian_module
from pelican.plugins.obsidian import ObsidianMarkdownReader, populate_files_and_articles
import os
import logging

@pytest.fixture
def obsidian_jinja(tmp_path):
    settings = get_settings()
    settings["DEFAULT_CATEGORY"] = "Default"
    settings["DEFAULT_DATE"] = (1970, 1, 1)
    settings["READERS"] = {"asc": None}
    settings["CACHE_CONTENT"] = False

    # Setup test directory structure
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()

    settings['PATH'] = str(fixtures_dir)

    # Create .env file
    (fixtures_dir / ".env").write_text("ENV_VAR=env_value\n", encoding="utf-8")

    # Create dot-env.md file (default name)
    (fixtures_dir / "dot-env.md").write_text("---\ntitle: dot-env\n---\nDOTENV_NOTE_VAR=note_value\n", encoding="utf-8")

    # Create custom-env.md file
    (fixtures_dir / "custom-env.md").write_text("---\ntitle: custom-env\n---\nCUSTOM_NOTE_VAR=custom_value\n", encoding="utf-8")

    # Create a jinja2 file
    jinja_content = """---
title: Jinja Test
tags: jinja
jinja2: true
my_meta: meta_value
---
Environment: {{ ENV_VAR }}
Note: {{ DOTENV_NOTE_VAR }}
OS: {{ OS_VAR }}
Metadata: {{ my_meta }}
"""
    (fixtures_dir / "jinja_test.md").write_text(jinja_content, encoding="utf-8")

    # Create a file for custom env test
    custom_env_content = """---
title: Custom Env Test
jinja2: true
---
Custom: {{ CUSTOM_NOTE_VAR }}
"""
    (fixtures_dir / "custom_env_test.md").write_text(custom_env_content, encoding="utf-8")

    # Create a file for custom filter test
    filter_content = """---
title: Filter Test
jinja2: true
---
Filtered: {{ 'hello' | my_upper }}
"""
    (fixtures_dir / "filter_test.md").write_text(filter_content, encoding="utf-8")

    # Create a file for error handling
    error_content = """---
title: Error Test
jinja2: true
---
Bad: {{ undefined_variable / 0 }}
"""
    (fixtures_dir / "error_test.md").write_text(error_content, encoding="utf-8")

    # Set OS environment variable
    os.environ["OS_VAR"] = "os_value"

    # Ensure JINJA2_INSTALLED is True for these tests
    obsidian_module.JINJA2_INSTALLED = True

    # Change CWD to fixtures_dir for load_dotenv default behavior (though we use usecwd=True)
    old_cwd = os.getcwd()
    os.chdir(fixtures_dir)

    omr = ObsidianMarkdownReader(settings=settings)

    generator = ArticlesGenerator(
        context=settings,
        settings=settings,
        path=str(fixtures_dir),
        theme=settings["THEME"],
        output_path=None,
    )
    populate_files_and_articles(generator)

    yield omr, fixtures_dir

    # Teardown
    os.chdir(old_cwd)
    del os.environ["OS_VAR"]


def test_jinja2_rendering_with_metadata(obsidian_jinja):
    omr, fixtures_dir = obsidian_jinja
    source_path = fixtures_dir / "jinja_test.md"

    content, metadata = omr.read(str(source_path))

    assert "Environment: env_value" in content
    assert "Note: note_value" in content
    assert "OS: os_value" in content
    assert "Metadata: meta_value" in content
    assert metadata["title"] == "Jinja Test"

def test_custom_dot_env_name(obsidian_jinja):
    omr, fixtures_dir = obsidian_jinja

    # Update settings
    omr.settings['OBSIDIAN_DOT_ENV_NOTE'] = 'custom-env'

    source_path = fixtures_dir / "custom_env_test.md"

    content, metadata = omr.read(str(source_path))

    assert "Custom: custom_value" in content

def test_custom_jinja_filters(obsidian_jinja):
    omr, fixtures_dir = obsidian_jinja

    # Define and register filter
    def my_upper(value):
        return value.upper() + " WORLD"

    omr.settings['OBSIDIAN_JINJA_FILTERS'] = {'my_upper': my_upper}

    source_path = fixtures_dir / "filter_test.md"

    content, metadata = omr.read(str(source_path))

    assert "Filtered: HELLO WORLD" in content

def test_jinja2_error_handling(obsidian_jinja, caplog):
    omr, fixtures_dir = obsidian_jinja
    source_path = fixtures_dir / "error_test.md"

    # Capture logs
    with caplog.at_level(logging.ERROR):
        content, metadata = omr.read(str(source_path))

    # Should return original content (with jinja tags unrendered)
    assert "Bad: {{ undefined_variable / 0 }}" in content
    # Should have logged error
    assert "Error rendering Jinja2 template" in caplog.text

def test_missing_jinja2_warning(obsidian_jinja, caplog):
    omr, fixtures_dir = obsidian_jinja
    source_path = fixtures_dir / "jinja_test.md"

    # Mock JINJA2_INSTALLED = False
    original_val = obsidian_module.JINJA2_INSTALLED
    obsidian_module.JINJA2_INSTALLED = False

    try:
        with caplog.at_level(logging.WARNING):
            content, metadata = omr.read(str(source_path))

        # Should return original content
        assert "Environment: {{ ENV_VAR }}" in content
        # Should warn
        assert "Jinja2 is not installed but requested" in caplog.text
        assert "pip install pelican-obsidian[jinja2]" in caplog.text

    finally:
        obsidian_module.JINJA2_INSTALLED = original_val
