import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich import print

from pmorch_gallery import constants, video_images
from pmorch_gallery import thumbnails as thumbnails_module

image_suffixes = {'.' + ext for ext in {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "gif",
    "svg"
}}

video_suffixes = {'.' + ext for ext in {
    "avi",
    "mp4",
    "wmv",
    "mov",
    "ram"
}}


class MediaType(Enum):
    UNKNOWN = 1
    IMAGE = 2
    VIDEO = 3

    @staticmethod
    def determine(path):
        """Determine the media type of path, perhaps being UKNOWN"""
        suffix = path.suffix.lower()
        if suffix in image_suffixes:
            return MediaType.IMAGE
        elif suffix in video_suffixes:
            return MediaType.VIDEO
        else:
            return MediaType.UNKNOWN

    @staticmethod
    def determine_known(path):
        """Determine the media type of path, UKNOWN being an error"""
        mediatype = MediaType.determine(path)
        if mediatype == MediaType.UNKNOWN:
            raise ValueError(f"{path} does not have a known file extension")
        return mediatype


def find_media(src_path: Path, recursive: bool) -> list[Path]:
    media = []
    method = 'rglob' if recursive else 'glob'
    # call src_path[method]
    file_iterator = getattr(src_path, method)('*')
    for path in sorted(file_iterator):
        if path.is_dir():
            continue
        if MediaType.determine(path) == MediaType.UNKNOWN:
            continue
        media.append(path)
    return media


def group_media_in_directories(media: list[Path], src_path):
    directories = {}
    for path in sorted(media):
        dir = str(path.parent.resolve().relative_to(src_path))
        # special case for the root of the tree
        if dir == '.':
            dir = ''
        directories[dir] = directories.get(dir, []) + [path]
    return directories


@dataclass
class DerivedMedia:
    thumbnails: thumbnails_module.Thumbnails
    video_samples: video_images.VideoSamples
    video_contact_sheets: video_images.VideoContactSheets


def register_derived_media(media, generated_dir):
    thumbnails = thumbnails_module.Thumbnails(generated_dir)
    video_samples = video_images.VideoSamples(generated_dir)
    video_contact_sheets = video_images.VideoContactSheets(generated_dir)
    for path in media:
        match MediaType.determine_known(path):
            case MediaType.IMAGE:
                thumbnails.register_source(path)
            case MediaType.VIDEO:
                video_samples.register_source(path)
                video_contact_sheets.register_source(path)
            case _:
                raise RuntimeError(f"Unknown type for {path}")
    return DerivedMedia(
        thumbnails=thumbnails,
        video_samples=video_samples,
        video_contact_sheets=video_contact_sheets)


@dataclass
class MediaItem:
    type: MediaType
    title: str
    thumbnail: Path
    image: Path
    video: Path | None


def create_media_items(media, derived_media, gallery_path):
    items = []
    for path in media:
        type = MediaType.determine_known(path)
        match type:
            case MediaType.IMAGE:
                thumbnail = derived_media.thumbnails.generated_path(path)
                image = path
                video = None
            case MediaType.VIDEO:
                thumbnail = derived_media.video_samples.generated_path(path)
                image = derived_media.video_contact_sheets.generated_path(path)
                video = path
            case _:
                raise ValueError(f"Uknown type for {path}")
        item = MediaItem(
            type=type,
            title=path.name,
            thumbnail=thumbnail.relative_to(gallery_path, walk_up=True),
            image=image.relative_to(gallery_path, walk_up=True),
            video=video.relative_to(
                gallery_path, walk_up=True) if video is not None else None
        )
        items.append(item)
    return items


@dataclass
class Directory:
    name: str
    path: list[str]
    items: list[MediaItem] = field(default_factory=list)
    subdirectories: "dict[Directory]" = field(default_factory=dict)

    @staticmethod
    def path_url(paths):
        if len(paths) == 0:
            return 'index.html'
        else:
            # Escape any ":" chars in directory names
            return ("_".join([re.sub(r"_", "__", p) for p in paths])) + ".html"
    
    def url(self):
        return Directory.path_url(self.path)


def create_missing_media(derived_media):
    for (disp, obj) in [
        ('Thumbnails', derived_media.thumbnails),
        ('Video Samples', derived_media.video_samples),
        ('Video Contact Sheets', derived_media.video_contact_sheets),
    ]:
        missing = obj.missing()
        if len(missing) > 0:
            print(f"Creating missing {disp}")
            obj.create_missing(missing)


def create_directory_media(src_path: Path, gallery_path: Path, recursive=True):
    media = find_media(src_path, recursive)
    generated_dir = gallery_path / constants.generated_dir_basename
    derived_media = register_derived_media(media, generated_dir)
    create_missing_media(derived_media)
    directory_media = group_media_in_directories(media, src_path)
    flat_directory_items = {}
    for directory in directory_media:
        flat_directory_items[directory] = create_media_items(
            directory_media[directory], derived_media, gallery_path)

    directory_names = sorted(list(directory_media.keys()))
    root = Directory(name='', path=[], items=flat_directory_items[''])
    for dir in directory_names:
        # already setup root
        if dir == '':
            continue
        current_dir = root
        current_parts = []
        for part in dir.split('/'):
            current_parts.append(part)
            if part not in current_dir.subdirectories:
                current_dir.subdirectories[part] = Directory(
                    name=part, path=current_parts.copy()
                )
            current_dir = current_dir.subdirectories[part]
        current_dir.items = flat_directory_items[dir]
    return root


if __name__ == "__main__":
    sample = Path(__file__).parent.parent.parent / "sample"
    gallery_path = sample.parent / 'gallery'
    root = create_directory_media(sample, gallery_path, True)

    print(root)
