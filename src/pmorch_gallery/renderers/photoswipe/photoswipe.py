from pathlib import Path

from pmorch_gallery import data_types
from pmorch_gallery.renderers import renderer_util


class Photoswipe(data_types.Renderer):
    def __init__(self):
        self.jenv = renderer_util.jinja2_env(
            Path(__file__).parent / 'templates')

    def render(self, template_vars: data_types.TemplateVars):
        template = self.jenv.get_template("page.html")
        vars = template_vars.__dict__.copy()
        vars['data_types'] = data_types
        return template.render(vars)

    def copy_static(self, gallery_path: Path):
        renderer_util.copy_static(
            Path(__file__).parent / 'static', gallery_path)


def renderer() -> data_types.Renderer:
    return Photoswipe()
