import shutil
from pathlib import Path

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    select_autoescape,
)

import pmorch_gallery
from pmorch_gallery import data_types


def jinja2_env():
    loader = ChoiceLoader([
        PackageLoader('pmorch_gallery'),
        FileSystemLoader(Path(__file__).parent / 'templates')
    ])
    return Environment(
        loader=loader,
        autoescape=select_autoescape()
    )


def json_dumps_media_items(media_items):
    items = []
    for i in media_items:
        item = {
            "title": i.title,
            "src": str(i.image.path),
            "srct": str(i.thumbnail.path),
        }
        if i.video is not None:
            item['customData'] = {"video": str(i.video)}
        items.append(item)
    return json.dumps(items, indent=4)


class Nanongallery2(data_types.Renderer):
    def __init__(self):
        self.render_num = 0
        self.jenv = jinja2_env()

    def render(self, template_vars: data_types.TemplateVars):
        template = self.jenv.get_template("page.html")
        render_vars = template_vars.__dict__
        render_vars["media_items_json"] = json_dumps_media_items(
            template_vars.media_items)
        return template.render(render_vars)

    def copy_static(self, gallery_path: Path):
        for src in [
            Path(pmorch_gallery.__file__).parent / 'static',
            Path(__file__).parent / 'static',
        ]:
            shutil.copytree(
                src,
                gallery_path / 'static', dirs_exist_ok=True
            )
        (gallery_path / 'static' / 'README.md').unlink()


def renderer() -> data_types.Renderer:
    return Nanongallery2()
