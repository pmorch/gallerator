# pmorch-gallery

## TODO

* Pagination: Currently if a folder has 1000 .jpg files, so will the (slow) gallery.
* Handle if the gallery contains the images
* Delete previously generated, now-obsolete `.html` and thumbnails.
* `dir/sub_dir/file.html` instead of `dir_sub__dir_file.html`
* Documentation.

**NOTE**: This version uses the GPLv3 versioned nanogallery2. I should've used
another MIT versioned gallery :-( This is the highest TODO-list item.

## Usage

Example

```bash
$ pmorch-gallery --gallery ./gallery  ./sample --recursive
```

## Requirements

Create a gallery that serves images and videos. (Are gifs images or videos?)

It should work recursively in a directory structure, reflecting the directories.

We want to serve these use cases:

1. Generate static gallery web pages
   1. Serve these over a simple webserver such as `nginx` or `python3 -m
      http.server`
   2. Open such files on the local file system as `file://` urls.
2. Serve dynamic web pages (so no .html files are stored on-disk)

Incorporate thumbnail generation for images and contact-sheet generation for
movies.

Theme-able?

## Design

### Intro

After a look around,
[nanogallery2](https://github.com/nanostudio-org/nanogallery2) seems like a good
base for the actual gallery part. It does what I want well enough and the API
looks good, albeit jQuery based.

Also, this shouldn't be a huge effort. 😜 I'd like to stay away from the
snowball effect of React, Vue, etc, which includes `vite` and the entire
javascript toolchain. This shouldn't need a lot of interactivity, so we
shouldn't need that. But perhaps we'll end up there.

The requirement of serving static web pages over file:// urls (not requiring a
web server at all), adds a serious limitation: We cannot use `XMLHttpRequest`s.
So no Ajax, or at least a no-Ajax fallback.

I also have been wanting to kick the tires of [htmx](https://htmx.org/)

And so it takes shape.

### Thumbnail generation

There are `PIL.Image.open().thumbnail()` seems to do a decent job of creating
the tumbnails, so I'll do that for now.

Perhaps parallelize it, using `Pool.map()`. What happens when `Pool.map()` forks
off sub-processes and the parent process is a web server with a web server port
open? Lets hope `Pool` is smart enough to do the right thing.

#### Elegant thumbnaiil opportunity: `SHA1` indirection

Lets use a digest like `SHA1` as indirection for thumbnails, so that if we have
`/path/to/imageX.jpg`, we don't just store `/thumbnails/path/to/imageX.jpg`
somwhere. That works until somebody moves it to `/otherpath/to/imageX.jpg`. Then
we have to regenerate the thumbnail again. If we instead store
`/thumbnails/thumb-deadbeef.jpg` where `deadbeef` is the `SHA1` digest of the
original image, then if somebody moves the image, it we can use the same
thumbnail again, and updating the gallery is fast the images get moved around.

If we start using a web server to serve dynamic pages, we'll need somewhere to
cache the `SHA1` digests of the images, so we don't have to regenerate them on
every page view. Cache invalidation if dir time > cache time should work.

### MVP

Static pages that work with file:// urls also work over a web server, so start
with that.

Later we can add htmx with static file:// as fallback.

Theming: I'm not sure how to really do that, but I'll give it a shot.

### Separate generated files from images

It would be ideal if could store the statically generated files and thumbnails
in another directory than the image files. Something like:

```
  /nature-images/
    image1.jpg
    image2.jpg
    image3.jpg
    /mountains/
      mountain1.jpg
      mountain2.jpg
      /switzerland/
        swiss-mountain1.jpg
        swiss-mountain2.jpg
    /sea/
      sea1.jpg
  /nature-gallery/
    index.html
    /mountains/
      index.html
      /switzerland/
        index.html
    /sea/
      index.html
    /thumbnails/
      thumb-aaaa.jpg
      thumb-bbbb.jpg
      ...
      thumb-zzzc.jpg
```

And then `/nature-gallery/mountains/switzerland/index.html` links to e.g.:
* `../../thumbnails/thumb-cccc.jpg`
* `../../../nature-images/mountains/switzerland/swiss-mountain1.jpg`.


Or perhaps a flatter structure like:

```
  /nature-gallery/
    index.html
    mountains.html
    mountains-switzerland.html
    sea.html
    /thumbnails/
      thumb-aaaa.jpg
      thumb-bbbb.jpg
      ...
      thumb-zzzc.jpg
```

with simpler links. The problem here is the `/`-->`-` translation. If we have
both a `mountains/switzerland` *and* a `mountains-switzerland` directory,
they'll clash. But perhaps we can detect and escape or forbid that.

The gallery *could* be in another directory, but we should also handle it so
they *can* be in the same directory.


## Setup

PYTHONPATH=$w/pmorch-gallery/src $w/pmorch-gallery/venv/bin/python3 -m unittest *.py

PYTHONPATH=$w/pmorch-gallery/src $w/pmorch-gallery/venv/bin/python3 -c 'import pmorch_gallery; pmorch_gallery.cli_main()' --help


## Choice of slide-show-in-a-light-box library

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
bit it looks like that is going to be a lot of work, so PhotoSwipe seems to be
it.

In order to use Photoswipe, we'll need the dimensions for all the images. Which
is probably a good idea, whatever lib we end up using.

https://codesandbox.io/p/sandbox/photoswipe-rymtzg