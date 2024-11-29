import shutil
from pathlib import Path

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    select_autoescape,
)

from pmorch_gallery import data_types


def jinja2_env(renderer_templates):
    """
    Sets up a Jinja2 environment that looks for renderer-specific templates
    first and then generic ones.
    """
    loader = ChoiceLoader([
        FileSystemLoader(renderer_templates),
        FileSystemLoader(Path(__file__).parent / 'templates'),
    ])
    return Environment(
        loader=loader,
        autoescape=select_autoescape()
    )


def copy_static(renderer_static: Path, gallery_path: Path):
    """
    Copies renderer-specific static files first and then generic ones.
    """
    for src in [
        renderer_static,
        Path(__file__).parent / 'static',
    ]:
        shutil.copytree(
            src,
            gallery_path / 'static', dirs_exist_ok=True
        )
    (gallery_path / 'static' / 'README.md').unlink()

