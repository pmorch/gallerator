import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    select_autoescape,
)

from . import constants, media_items


@dataclass
class TemplateVars:
    @dataclass
    class Directory:
        # None if the parent is the root
        name: str | None
        url: str
    # The root has no parent

    @dataclass
    class MediaItem:
        title: str
        src_url: str
        thumbnail_url: str
        video_url: str | None = None

    gallery_name: str
    parent: Directory | None
    breadcrumbs: list[Directory]
    media_items: list[MediaItem]
    # The result of json_dumps_media_items(self.media_items)
    media_items_json: str
    thumbnail_height: int
    dynamic_javascript: str
    subdirectories: list[Directory]


def json_dumps_media_items(media_items):
    items = []
    for i in media_items:
        item = {
            "title": i.title,
            "src": i.src_url,
            "srct": i.thumbnail_url,
        }
        if i.video_url is not None:
            item['customData'] = {"video": i.video_url}
        items.append(item)
    return json.dumps(items, indent=4)


def create_template_vars(gallery_name, directory, parent):
    media = []
    for item in directory.items:
        media_item = TemplateVars.MediaItem(
            title=item.title,
            src_url=str(item.image.path),
            thumbnail_url=str(item.thumbnail.path)
        )
        if item.video is not None:
            media_item.video_url = str(item.video)
        media.append(media_item)

    if parent is None:
        parent_var = None
    else:
        parent_var = TemplateVars.Directory(
            name=None if parent.name == '' else parent.name,
            url=parent.url()
        )

    subdirectories = []
    for dir in directory.subdirectories:
        subdir = directory.subdirectories[dir]
        subdirectories.append(TemplateVars.Directory(
            name=subdir.name,
            url=subdir.url()
        ))

    breadcrumbs = [
        TemplateVars.Directory(
            url=media_items.Directory.path_url([]),
            name=gallery_name
        )
    ]
    path_so_far = []
    for p in directory.path:
        path_so_far.append(p)
        breadcrumbs.append(TemplateVars.Directory(
            url=media_items.Directory.path_url(path_so_far),
            name=p,
        ))

    template_vars = TemplateVars(
        gallery_name=gallery_name,
        parent=parent_var,
        breadcrumbs=breadcrumbs,
        media_items=media,
        # Set below
        media_items_json=json_dumps_media_items(media),
        thumbnail_height=constants.thumbnail_height,
        dynamic_javascript=None,
        subdirectories=subdirectories
    )

    return template_vars


def get_html(jenv, gallery_name, directory, parent):
    template_vars = create_template_vars(gallery_name, directory, parent)
    template = jenv.get_template("page.html")
    return template.render(template_vars.__dict__)


def write_gallery_directory(jenv, gallery_name, gallery_path,
                            directory: media_items.Directory,
                            parent: media_items.Directory | None):
    fname = str(gallery_path / directory.url())
    print(f'Creating {fname}')
    with open(fname, 'w') as file:
        file.write(get_html(jenv, gallery_name, directory, parent))
    # recursive!
    for subdir in directory.subdirectories:
        write_gallery_directory(jenv, gallery_name, gallery_path,
                                directory.subdirectories[subdir],
                                directory)


def jinja2_env(template_dir):
    loader = loader = PackageLoader("pmorch_gallery")
    if template_dir is not None:
        custom_loader = FileSystemLoader(template_dir)
        loader = ChoiceLoader([custom_loader, loader])
    return Environment(
        loader=loader,
        autoescape=select_autoescape()
    )


def write_gallery(
        gallery_name,
        src_path,
        gallery_path,
        recursive,
        template_dir):

    jenv = jinja2_env(template_dir)
    root = media_items.create_directory_media(
        src_path, gallery_path, recursive)
    write_gallery_directory(jenv, gallery_name, gallery_path, root, None)

    static = Path(__file__).parent / 'static'
    print("Copying static files")
    shutil.copytree(static, gallery_path / 'static', dirs_exist_ok=True)


if __name__ == "__main__":
    sample = Path(__file__).parent.parent.parent / "sample"
    gallery_path = sample.parent / 'gallery'
    write_gallery(sample, gallery_path, True)
