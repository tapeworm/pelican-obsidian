
import pytest
from pathlib import Path
from pelican.generators import ArticlesGenerator
from pelican.tests.support import get_settings
from pelican.plugins.obsidian import ObsidianMarkdownReader, populate_files_and_articles
import os

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

    # Create dot-env.md file
    (fixtures_dir / "dot-env.md").write_text("---\ntitle: dot-env\n---\nDOTENV_NOTE_VAR=note_value\n", encoding="utf-8")

    # Create a jinja2 file
    jinja_content = """---
title: Jinja Test
tags: jinja
jinja2: true
---
Environment: {{ ENV_VAR }}
Note: {{ DOTENV_NOTE_VAR }}
OS: {{ OS_VAR }}
"""
    (fixtures_dir / "jinja_test.md").write_text(jinja_content, encoding="utf-8")

    # Create a non-jinja file
    non_jinja_content = """---
title: Non Jinja Test
tags: nojinja
---
Environment: {{ ENV_VAR }}
"""
    (fixtures_dir / "non_jinja_test.md").write_text(non_jinja_content, encoding="utf-8")

    # Set OS environment variable
    os.environ["OS_VAR"] = "os_value"

    # Change CWD to fixtures_dir so load_dotenv finds .env
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

def test_jinja2_rendering(obsidian_jinja):
    omr, fixtures_dir = obsidian_jinja
    source_path = fixtures_dir / "jinja_test.md"

    content, metadata = omr.read(str(source_path))

    assert "Environment: env_value" in content
    assert "Note: note_value" in content
    assert "OS: os_value" in content
    assert metadata["title"] == "Jinja Test"

def test_no_jinja2_rendering(obsidian_jinja):
    omr, fixtures_dir = obsidian_jinja
    source_path = fixtures_dir / "non_jinja_test.md"

    content, metadata = omr.read(str(source_path))

    # Should not be rendered
    assert "Environment: {{ ENV_VAR }}" in content
