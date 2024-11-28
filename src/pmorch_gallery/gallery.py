import re
from pathlib import Path

from . import constants, data_types, dynimport, media_items
from .nanogallery2 import nanogallery2
from .photoswipe import photoswipe


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


def get_renderer(renderer_arg):
    match renderer_arg:
        case "PhotoSwipe":
            return photoswipe.renderer()
        case "nanogallery2":
            return nanogallery2.renderer()
        case _:
            path = Path(renderer_arg)
            if not path.exists():
                raise FileNotFoundError(path)
            module = dynimport.import_random_module_from_path(renderer_arg)
            if not hasattr(module, 'renderer'):
                raise ValueError(
                    f'Renderer {renderer_arg} does not have a renderer method')
            renderer = module.renderer()
            if not isinstance(renderer, data_types.Renderer):
                raise ValueError(
                    f'Renderer {renderer_arg}.render() does not return a Renderer instance')
            return renderer


def write_gallery(
        gallery_name,
        src_path,
        gallery_path,
        recursive,
        renderer_arg):

    root = media_items.create_directory_media(
        src_path, gallery_path, directory_path_url, recursive)

    renderer = get_renderer(renderer_arg)

    write_gallery_directory(renderer, gallery_name, gallery_path, root, None)

    print(f"Copying static files to {gallery_path}")
    renderer.copy_static(gallery_path)
