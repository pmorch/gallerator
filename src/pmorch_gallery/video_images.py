import sys
from contextlib import redirect_stdout

from vcsi.vcsi import MediaInfo
from vcsi.vcsi import main as vcsi_main

from . import constants, generated_set


def run_vcsi(*args):
    old_sys_argv = sys.argv
    sys.argv = ['vcsi'] + [ str(s) for s in args ]
    try:
        # vcsi is noisy and prints progress to stdout. Don't do that.
        with redirect_stdout(None):
            vcsi_main()
    finally:
        sys.argv = old_sys_argv


class VideoSamples(generated_set.GeneratedSet):

    def __init__(self, generated_dir):
        super().__init__(generated_dir)

    def generated_file_prefix(self):
        return 'video-sample'

    def generated_file_suffix(self, fpath):
        return ".jpg"

    def create_file(self, source, destination):
        # If we just let vcsi create a single image, it will do so towards the
        # middle of the video. Testing shows that the first image in the contact
        # sheet, about 12% into the video, is better. Find the time 12% in. For
        # that we could use ffprobe (like vcsi does), but it already does
        # everything so well, so why not let it...
        #
        # That being said, we calculate the width that should make the height
        # constants.thumbnail_height (300) but the result is actually 395
        # (landscape video) or 413 (portait) so I guess it is good enough. But
        # not precise...
        media_info = MediaInfo(source)
        thumbnail_seconds = media_info.duration_seconds * \
            constants.video_thumbnail_time_fraction
        minutes = int(thumbnail_seconds / 60)
        seconds = int(thumbnail_seconds) % 60
        ratio = media_info.display_height / constants.thumbnail_height
        width = media_info.display_width / ratio
        # print(" ".join([str(source),
        #             '-t',
        #             '-g', '1x1',
        #             '--width', str(width),
        #             '-m', f'{minutes}:{seconds}',
        #             '-o', str(destination)]))
        run_vcsi(source,
                    '-t',
                    '-g', '1x1',
                    '--width', int(width),
                    '--metadata-position', 'hidden',
                    '-m', f'{minutes}:{seconds}',
                    '-o', destination)

class VideoContactSheets(generated_set.GeneratedSet):

    def __init__(self, generated_dir):
        super().__init__(generated_dir)

    def generated_file_prefix(self):
        return 'video-contact-sheet'

    def generated_file_suffix(self, fpath):
        return ".jpg"

    def create_file(self, source, destination):
        run_vcsi(source, '-t', '-o', destination)
