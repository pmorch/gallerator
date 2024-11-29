import re
from pathlib import Path

from . import constants, data_types, dynimport, media_items, url_strategy


def create_template_vars(gallery_name, directory, parent, page_url_strategy: url_strategy.PageUrlStrategy):
    subdirectories = []
    for dir in sorted(directory.subdirectories):
        subdirectories.append(directory.subdirectories[dir])

    breadcrumbs = [
        data_types.Breadcrumb(
            name=gallery_name,
            path=[]
        )
    ]
    path_so_far = []
    for p in directory.path:
        path_so_far.append(p)
        breadcrumbs.append(data_types.Breadcrumb(
            name=p,
            path=path_so_far.copy(),
        ))

    def path_to_url(path: list[Path], page_num: int = 0):
        return page_url_strategy.page_url(path, page_num)

    template_vars = data_types.TemplateVars(
        gallery_name=gallery_name,
        parent=parent,
        breadcrumbs=breadcrumbs,
        media_items=directory.items,
        thumbnail_height=constants.thumbnail_height,
        subdirectories=subdirectories,
        path_to_url=path_to_url
    )

    return template_vars


def write_gallery_directory(renderer,
                            gallery_name: str,
                            gallery_path: Path,
                            directory: data_types.Directory,
                            parent: data_types.Directory | None,
                            page_url_strategy: url_strategy.PageUrlStrategy,
                            pagination: int | None):
    fname: Path = gallery_path / page_url_strategy.page_url(directory.path)
    fname.parent.mkdir(exist_ok=True)
    print(f'Creating {fname}')
    template_vars = create_template_vars(
        gallery_name, directory, parent, page_url_strategy)
    html = renderer.render(template_vars)
    with open(fname, 'w') as file:
        file.write(html)
    # recursive!
    for subdir in directory.subdirectories:
        write_gallery_directory(renderer,
                                gallery_name,
                                gallery_path,
                                directory.subdirectories[subdir],
                                directory,
                                page_url_strategy,
                                pagination)


def get_renderer(renderer_arg):
    def get_renderer(path):
        module = dynimport.import_random_module_from_path(path)
        if not hasattr(module, 'renderer'):
            raise ValueError(
                f'Renderer {path} does not have a renderer method')
        renderer = module.renderer()
        if not isinstance(renderer, data_types.Renderer):
            raise ValueError(
                f'Renderer {path}.render() does not return a Renderer instance')
        return renderer

    match renderer_arg:
        case "PhotoSwipe":
            return get_renderer(
                Path(__file__).parent / "renderers" /
                "photoswipe" / "photoswipe.py")
        case "nanogallery2":
            return get_renderer(
                Path(__file__).parent / "renderers" /
                "nanogallery2" / "nanogallery2.py")
        case _:
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
        renderer_arg,
        pagination):

    root = media_items.create_directory_media(
        src_path, gallery_path, recursive)

    renderer = get_renderer(renderer_arg)

    page_url_strategy = url_strategy.UnderscorePageUrlStrategy()

    write_gallery_directory(
        renderer,
        gallery_name,
        gallery_path,
        root,
        None,
        page_url_strategy,
        pagination
    )

    print(f"Copying static files to {gallery_path}")
    renderer.copy_static(gallery_path)
