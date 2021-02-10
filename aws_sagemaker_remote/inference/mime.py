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
    types = [
        'audio/wav',
        'audio/x-wav',
        'audio/wave',
        'audio/x-wave',
        'audio/ogg',
        'audio/oga',
        'audio/webm',
        'audio/weba',
        'audio/mp4',
        'audio/mp3',
        'audio/mpeg',
        'audio/mpeg3',
        'audio/x-mpeg-3',
    ]
    exts = [
        'wav',
        'webm',
        'weba',
        'oga',
        'ogg',
        'opus',
        'mp3',
        'mp4',
        'mpeg'
    ]
    for t in types:
        for k, v in [
            ("Base", mimetypes),
            ("Mod", MIME)
        ]:
                print(f"db {k}, mime {t}: {v.guess_all_extensions(t)}")
    for e in exts:
        for k, v in [
            ("Base", mimetypes),
            ("Mod", MIME)
        ]:
            f = f"path/file.{e}"
            print(f"db {k}, ext {e}: {v.guess_type(f)}")


    # print(next(mimetypes.types_map.items().__iter__()))
    # print(next(mimetypes.suffix_map.items().__iter__()))
