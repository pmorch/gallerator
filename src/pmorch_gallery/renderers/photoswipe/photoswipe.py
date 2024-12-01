from pathlib import Path

import argparse
import re

from pmorch_gallery import data_types, renderer
from pmorch_gallery.renderers import renderer_util

description = """
These are the arguments for Photoswipe, the default renderer. Different
renderers have different options, so try "--renderer name-of-renderer --help" to
see options for other renderers.
"""

grid_help = """
By default, Photoswipe uses a justified layout, but this will create a grid
layout. Recommend to use "--grid 4x5", for 4 columns of 5 images, but supply your
own "XxY" value to set your own grid layout. This will override any --pagination
value.
"""


class Photoswipe(renderer.Renderer):
    def __init__(self):
        self.jenv = renderer_util.jinja2_env(
            Path(__file__).parent / 'templates')

    def add_argparse_args(self, parser: argparse.ArgumentParser):
        group = parser.add_argument_group(
            'Photoswipe', description=description)
        group.add_argument('--grid', help=grid_help)
        # group.add_argument('--bar', help='bar help')

    def _set_grid_dimensions(self, args):
        self.grid = None
        if args.grid is not None:
            matches = re.match(r'^(\d+)x(\d+)$', args.grid)
            if matches is None:
                raise ValueError(
                    "Please sepecify --grid as XxY, where X and Y are "
                    "integers, e.g. 4x5"
                )
            x = int(matches[1])
            y = int(matches[2])
            args.pagination = x * y
            self.grid = { "x": x, "y": y}

    def update_args(self, args: argparse.Namespace):
        self._set_grid_dimensions(args)
        super().update_args(args)

    def render(self, template_vars: data_types.TemplateVars):
        template = self.jenv.get_template("page.html")
        vars = template_vars.__dict__.copy()
        vars.update({
            'data_types': data_types,
            'layout': 'justified' if self.grid is None else 'grid'
        })
        return template.render(vars)

    def copy_static(self, gallery_path: Path):
        renderer_util.copy_static(
            Path(__file__).parent / 'static', gallery_path)
        template = self.jenv.get_template('page.css')
        with open(gallery_path / 'static' / 'page.css', 'w') as f:
            f.write(template.render(thumbnail_height=200, grid=self.grid))


def renderer() -> renderer.Renderer:
    return Photoswipe()
