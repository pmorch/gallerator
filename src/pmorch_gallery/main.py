import argparse
from pathlib import Path

from . import constants, gallery

gallery_name_help = '''
The name of the gallery. Defaults the base name of the 'source_dir'.
'''

source_dir_help = f'''
The directory containing the source images and videos over which we want to
create a gallery.

Any sub-directory named {constants.generated_dir_basename} in this directory
will be ignored.
'''

gallery_dir_help = '''
The directory in which to store the generated gallery. Defaults to the same as
the 'source_dir' containing the images.

Note that this directory should be "close" to the `source_dir` since relative
paths are used when referencing source images from the gallery or you'll get
many '../' elements in the image paths.
'''

recursive_help = '''
Whether to search for image and video files recursively.
'''

renderer_help = '''
Which renderer to use to actually produce the output galleries. At the moment,
there are two built-in ones: "PhotoSwipe" and "nanogallery2". Advanced: Other
values will be loaded as a module that is expected to have a renderer() method
that returns an instance of pmorch_gallery.data_types.Renderer. That way you can
render the gallery exactly like you want.
'''

def parse_args():
    parser = argparse.ArgumentParser(
        prog='pmorch-gallery',
        description='Create static thumbnail galleries',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('source_dir', help=source_dir_help)
    parser.add_argument('--name-of-gallery', help=gallery_name_help, default=None)
    parser.add_argument('--gallery-dir', '-g',
                        help=gallery_dir_help, default=None)
    parser.add_argument('--recursive', '-r', help=recursive_help,
                        default=False, action='store_true')
    parser.add_argument('--renderer', default='PhotoSwipe', help=renderer_help)
    args = parser.parse_args()
    return args


def cli_main():
    args = parse_args()
    if args.name_of_gallery is None:
        gallery_name = Path(args.source_dir).stem
    else:
        gallery_name = args.name_of_gallery
    if args.gallery_dir is None:
        gallery_dir = args.source_dir
    else:
        gallery_dir = args.gallery_dir
    gallery.write_gallery(
        gallery_name,
        Path(args.source_dir).resolve(),
        Path(gallery_dir).resolve(),
        args.recursive,
        args.renderer)
