import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich import print


from . import constants, media_items, data_types, nanogallery2


def directory_path_url(paths):
    if len(paths) == 0:
        return 'index.html'
    else:
        # Escape any ":" chars in directory names
        return ("_".join([re.sub(r"_", "__", p) for p in paths])) + ".html"


def create_template_vars(gallery_name, directory, parent):
    subdirectories = []
    for dir in sorted(directory.subdirectories):
        subdirectories.append(directory.subdirectories[dir])

    breadcrumbs = [
        data_types.Breadcrumb(
            name=gallery_name,
            url=directory_path_url([])
        )
    ]
    path_so_far = []
    for p in directory.path:
        path_so_far.append(p)
        breadcrumbs.append(data_types.Breadcrumb(
            name=p,
            url=directory_path_url(path_so_far),
        ))

    template_vars = data_types.TemplateVars(
        gallery_name=gallery_name,
        parent=parent,
        breadcrumbs=breadcrumbs,
        media_items=directory.items,
        thumbnail_height=constants.thumbnail_height,
        subdirectories=directory.subdirectories
    )

    return template_vars


def write_gallery_directory(renderer, gallery_name, gallery_path,
                            directory: data_types.Directory,
                            parent: data_types.Directory | None):
    fname = str(gallery_path / directory.url)
    print(f'Creating {fname}')
    template_vars = create_template_vars(gallery_name, directory, parent)
    html = renderer.render(template_vars)
    with open(fname, 'w') as file:
        file.write(html)
    # recursive!
    for subdir in directory.subdirectories:
        write_gallery_directory(renderer, gallery_name, gallery_path,
                                directory.subdirectories[subdir],
                                directory)


def write_gallery(
        gallery_name,
        src_path,
        gallery_path,
        recursive,
        template_dir):

    root = media_items.create_directory_media(
        src_path, gallery_path, directory_path_url, recursive)
    renderer = nanogallery2.renderer()
    
    write_gallery_directory(renderer, gallery_name, gallery_path, root, None)

    static = Path(__file__).parent / 'static'
    print("Copying static files")
    shutil.copytree(static, gallery_path / 'static', dirs_exist_ok=True)


if __name__ == "__main__":
    sample = Path(__file__).parent.parent.parent / "sample"
    gallery_path = sample.parent / 'gallery'
    write_gallery(sample, gallery_path, True)
