# Gallerator

The gallery generator.

Demos: https://pmorch.github.io/demo-gallerator/

Homepage: https://github.com/pmorch/gallerator

## Features

* Static gallery generation that can be used anywhere, also using `file://` urls
  without a web server.
* Create thumbnails for images and thumbnails and contact sheets for videos.
* Generates galleries in a few formats
  * Justified
  * Grid (two variants)
  * See [demos](https://pmorch.github.io/demo-gallerator/)
* With or without thumbnail captions
* For a single directory or recursively for an entire tree
  * Includes navigation into sub-directories
* *ALL* filenames are relative, so you can move image and gallery files around
  and they still work, as long as they don't move relative to each other.
* Completely separate metadata generation and output rendering with a documented
  API between them
    * Two examples provided:
      * Renderer using [PhotoSwipe](https://github.com/dimsemenov/PhotoSwipe) -
        the default and most full-featured.
      * Renderer using [nanogallery2](https://nanogallery2.nanostudio.org/) - I
        forgot to check nanogallery2's GPLv3 license when I wrote code for it.
        😜 Less features.

## Installation and basic usage

```
# Need python 3.12:
$ python3 --version
Python 3.12.x (or higher)

# Perhaps use a virtualenv
$ python3 -m venv venv
$ source ./venv/bin/activate

# Need ffmpeg - debian example
$ sudo apt install ffmpeg

# Install gallerator
$ pip3 install gallerator

# See command line flags
$ gallerator --help 

# Generator your first gallery
$ gallerator -g /path/to/gallery /path/to/images

# Profit - open the new gallery in your web browser
$ xdg-open file:///path/to/images
```
## License

MIT

## Usage

<!-- replace-section:usage -->
```
usage: gallerator [-h] [--name-of-gallery NAME_OF_GALLERY]
                  [--gallery-dir GALLERY_DIR] [--recursive]
                  [--pagination PAGINATION] [--renderer RENDERER]
                  [--justified] [--auto-grid] [--grid GRID] [--width WIDTH]
                  [--height HEIGHT] [--no-filename-captions]
                  source_dir

Create static thumbnail galleries

positional arguments:
  source_dir            The directory containing the source images and videos
                        over which we want to create a gallery.

options:
  -h, --help            show this help message and exit
  --name-of-gallery NAME_OF_GALLERY
                        The name of the gallery. Defaults the base name of the
                        'source_dir'. (default: None)
  --gallery-dir GALLERY_DIR, -g GALLERY_DIR
                        The directory in which to store the generated gallery.
                        Defaults to the same as the 'source_dir' containing
                        the images. Note that this directory should be "close"
                        to the `source_dir` since relative paths are used when
                        referencing source images from the gallery or you'll
                        get many '../' elements in the image paths. (default:
                        None)
  --recursive, -r       Whether to search for image and video files
                        recursively. (default: False)
  --pagination PAGINATION, -p PAGINATION
                        The maximum number of images per page. 0 means
                        unlimited. (default: 0)
  --renderer RENDERER   Which renderer to use to actually produce the output
                        galleries. At the moment, there are two built-in ones:
                        "PhotoSwipe" and "nanogallery2". Advanced: Other
                        values will be loaded as a module that is expected to
                        have a renderer() method that returns an instance of
                        gallerator.data_types.Renderer. That way you can
                        render the gallery exactly like you want. (default:
                        PhotoSwipe)

Photoswipe:
  These are the arguments for Photoswipe, the default renderer. Different
  renderers have different options, so try "--renderer name-of-renderer
  --help" to see options for other renderers.

  --justified           Use a justified layout (the default), where all images
                        have the same height, but the width depends on the
                        image. This is the most dense but different pages may
                        not have the same height if used with pagination, so
                        perhaps one other layouts are better with pagination.
                        (default: False)
  --auto-grid           Use a grid layout but fit as many columns as will fit
                        depending on screen width. (default: False)
  --grid GRID           By default, Photoswipe uses a justified layout, but
                        this will create a grid layout. Try e.g. "--grid 4x5",
                        for 4 columns by 5 rows, but supply your own "XxY"
                        value to set your own grid layout. This will override
                        any --pagination value. Beware that this is not
                        responsive, so it will either be too wide on mobile or
                        too narrow for large desktop users, or both. (default:
                        None)
  --width WIDTH         The width of the thumbnails. Only used by --auto-grid
                        and --grid (default: 300)
  --height HEIGHT       The height of the thumbnails. (default: 300)
  --no-filename-captions
                        Don't add the filenames of the images as a caption in
                        the thumbnail gallery. This makes it look cleaner
                        (especially for --grid and --auto-grid), but less
                        information for the user. When the full image is shown
                        in a lightbox, the file name is always shown,
                        regardless of this setting. (default: False)
```
<!-- /replace-section:usage -->


## Customizations - about renderers

Generating output is and must be flexible. Users can write their own "renderer"
to generate `.html` file output. Two renderers come out of the box:

1. One using Photoswipe
2. One using nanogallery2

They basically just have to implement an instance of
`gallerator.renderer.Renderer` and return it as described under `gallerator
--help` for the `--renderer` flag. Look in the `renderer` folder for the two
examples if you want your own look and feel.

Both of the built-in ones use bootstrap, but they don't have to. You can use
whatever you like.

## Implementation details

### About the choice of slide-show-in-a-light-box library

At first I implemented this with
[nanogallery2](https://nanogallery2.nanostudio.org/) which has a simple API and
is quick to get started with. But the
[license](https://github.com/nanostudio-org/nanogallery2?tab=readme-ov-file#license--gplv3)
GPLv3! I didn't notice that when I picked it.

When [looking
for](https://github.com/search?q=gallery&type=repositories&s=stars&o=desc)
popular open-source, non-GPL3 libraries for this, there seem to be two
contenders:

* [swiper](https://github.com/nolimits4web/swiper) 40k stars
* [PhotoSwipe](https://github.com/dimsemenov/PhotoSwipe) 24.3k stars

Others don't even come close (nanogallery2 has 762 stars).

I've tried to get swiper to [run in a
lightbox](https://github.com/nolimits4web/swiper/discussions/4336#discussioncomment-11377361)
bit it looks like that is going to be a lot of work, so I picked PhotoSwipe. But
it is possible to writeother renderers

### About the naming of generated images

Currently, generated thumbnails are named:
`$gallery/generated-files/thumb-$sha1sum.jpg` where `$sha1sum` is the SHA1 sum
of the original source file.

This was done so that if you rename or move source images around, the thumbnails
still work. This may not be for everyone, and some may like something like
`$gallery/generated-files/path/to/file-thumb.jpg` instead. Not yet possible.

### Possible Enhancements

* Avoid FOUC (flash of unstyled content) at startup
  * When starting up, there is a flash of "small black boxes" while the images
    load, especially for the default "justified" layout.
* Parallelize thumbnail generation, e.g. using `Pool.map()`.
  * Note that `vcsi` for generating video screenshots and contact sheets already
    has a `--fast` parameter that parallelizes under the hood so don't
    parallelize that. But we don't (yet) even use `--fast`.
* More customizations
  * Page URL strategies: The naming of output `.html` files is currently
    hardcoded, but totally doen't have to. Look for
    `url_strategy.UnderscorePageUrlStrategy` in `gallery.py` and enable it
    instead, and you can see files are named differently. This just would need
    to be exposed in the CLI which it isn't (yet?). Patches welcome.
  * Allow flexible naming of thumbnails with or without SHA1 sums.
* It would be great if generating screenshots and contact sheets for videos
  could be faster. Start with trying `vcsi --fast` 😜.
* A little more care and love could be given to generation of thumbnails.
  * Right now we simply use `PIL.Image.thumbnail(x,y)` - is that enough?
  * We always scale thumbnails to have 350*350 total pixels, but we probably
    should scale thumbnails to the width, height and/or layout that will
    actually be used.
  * We always link to the source image, however large that may be. Perhaps we
    should also provide (optional?) scaling of the source images, so we don't
    serve multi-megabyte images when you click on the thumbnail. See e.g.
    [Efficient Image Resizing With ImageMagick— Smashing
    Magazine](https://www.smashingmagazine.com/2015/06/efficient-image-resizing-with-imagemagick/)
  * Perhaps use [jpegoptim](https://github.com/tjko/jpegoptim) if available?

### Note on usage with NixOS

When using NixOS I've seen errors with libaries. `fix-python` is the solution
for that. So instead of the above for installation, do:

```
$ nix shell nixpkgs#{python312,libGL,ffmpeg,gcc} github:GuillaumeDesforges/fix-python
$ python -m venv venv --copies
$ source ./venv/bin/activate
$ fix-python --venv venv
$ pip3 install gallerator
# I don't remember exactly when I was required to run fix-python
$ fix-python --venv venv
$ gallerator -g /path/to/gallery /path/to/images
```

But if you're using NixOS, that is perhpas enough of a hint to get you started
(patches welcome).
