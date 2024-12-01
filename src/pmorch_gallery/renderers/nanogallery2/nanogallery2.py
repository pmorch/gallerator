import argparse
import json
from pathlib import Path

from pmorch_gallery import data_types, renderer
from pmorch_gallery.renderers import renderer_util

description = """
These are the arguments for the nanogallery2 renderer.
Beware of its license.
"""


height_help = """
The height of the thumbnails.
"""

def json_dumps_media_items(media_items, relative_url):
    items = []
    for i in media_items:
        item = {
            "title": i.title,
            "src": relative_url(i.image.path),
            "srct": relative_url(i.thumbnail.path),
        }
        if i.video is not None:
            item['customData'] = {"video": relative_url(i.video)}
        items.append(item)
    return json.dumps(items, indent=4)


class Nanongallery2(renderer.Renderer):
    def __init__(self):
        self.jenv = renderer_util.jinja2_env(
            Path(__file__).parent / 'templates')

    def add_argparse_args(self, parser: argparse.ArgumentParser):
        group = parser.add_argument_group(
            'nanogallery2', description=description)
        group.add_argument('--height', default=300, help=height_help)

    def render(self, template_vars: data_types.TemplateVars):
        template = self.jenv.get_template("page.html")
        render_vars = template_vars.__dict__
        render_vars["media_items_json"] = json_dumps_media_items(
            template_vars.media_items,
            template_vars.relative_url,
        )
        render_vars['thumbnail_height'] = self.args.height
        return template.render(render_vars)

    def copy_static(self, gallery_path: Path):
        renderer_util.copy_static(
            Path(__file__).parent / 'static', gallery_path)


def renderer() -> renderer.Renderer:
    return Nanongallery2()
