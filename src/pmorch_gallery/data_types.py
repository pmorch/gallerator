from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class MediaType(Enum):
    UNKNOWN = 1
    IMAGE = 2
    VIDEO = 3


@dataclass
class ImageInfo:
    path: Path
    width: int
    height: int

@dataclass
class MediaItem:
    """
        Representation of a gallery media item. Uses absolute paths for files.
    """
    type: MediaType
    title: str
    thumbnail: ImageInfo
    image: ImageInfo
    video: Path | None


@dataclass
class Directory:
    """
        Representation of a gallery directory. Uses absolute paths for files.
    """
    name: str
    path: list[str]
    url: str
    items: list[MediaItem] = field(default_factory=list)
    subdirectories: "dict[Directory]" = field(default_factory=dict)

@dataclass
class Breadcrumb:
    name: str
    url: str

@dataclass
class TemplateVars:
    gallery_name: str
    parent: Directory | None
    # Each element contains a name and a url
    breadcrumbs: list[Breadcrumb]
    media_items: list[MediaItem]
    thumbnail_height: int
    subdirectories: list[Directory]
    
    
class Renderer:
    """Abstract base class for renderers to implement"""

    def render(self, template_vars: TemplateVars):
        """Returns the contents of the index file for template_vars"""
        raise NotImplementedError

    def copy_static(self, gallery_path: Path):
        """Copies any required files to gallery_path"""
        raise NotImplementedError
