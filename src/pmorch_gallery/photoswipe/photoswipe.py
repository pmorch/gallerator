import json
import shutil
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)

from pmorch_gallery import data_types


def jinja2_env():
    loader = FileSystemLoader(Path(__file__).parent / 'templates')
    return Environment(
        loader=loader,
        autoescape=select_autoescape()
    )



class Photoswipe(data_types.Renderer):
    def __init__(self):
        self.jenv = jinja2_env()

    def render(self, template_vars: data_types.TemplateVars):
        template = self.jenv.get_template("page.html")
        vars = template_vars.__dict__.copy()
        vars['data_types'] = data_types
        data_types.MediaType.VIDEO
        return template.render(vars)

    def copy_static(self, gallery_path: Path):
        static_src = Path(__file__).parent / 'static'
        for src in static_src.glob('*'):
            shutil.copy(src, gallery_path / 'static')

def renderer() -> data_types.Renderer:
    return Photoswipe()
