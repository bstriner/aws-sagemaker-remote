import mimetypes
import os
JSON_TYPES = [
    'application/json',
    'text/javascript',
    'application/javascript',
    'text/json'
]
MIME_KEYS = [
    'mimetype',
    'mime-type',
    'content-type',
    'type'
]
MIME = mimetypes.MimeTypes(
    filenames=(
        os.path.abspath(os.path.join(__file__, '../mime.types')),
    ),
    strict=True
)
FIX_FORMATS = {
    'weba': 'webm',
    'oga': 'ogg',
    'opus': 'ogg'
}

if __name__ == '__main__':
    for k, v in [
        ("Base", mimetypes),
        ("Mod", MIME)
    ]:
        print(k)
        print(v.guess_all_extensions('audio/wav'))
        print(v.guess_all_extensions('audio/x-wav'))
        print(v.guess_all_extensions('audio/wave'))
        print(v.guess_all_extensions('audio/x-wave'))
        print(v.guess_all_extensions('audio/ogg'))
        print(v.guess_all_extensions('audio/webm'))
        print(v.guess_all_extensions('audio/weba'))
        print(v.guess_type('path/file.wav'))
        print(v.guess_type('path/file.webm'))
        print(v.guess_type('path/file.weba'))
        print(v.guess_type('path/file.oga'))
        print(v.guess_type('path/file.ogg'))
        print(v.guess_type('path/file.opus'))

    # print(next(mimetypes.types_map.items().__iter__()))
    # print(next(mimetypes.suffix_map.items().__iter__()))
