import mimetypes
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
AUDIO_TYPES = {
    '.wav': [
        'audio/x-wav',
        'audio/x-wave',
        'audio/wave',
        'audio/wav'
    ],
    '.weba': [
        'audio/webm'
    ],
    '.webm': [
        'audio/webm'
    ],
    '.ogg': [
        'audio/ogg'
    ]
}
FIX_FORMATS = {
    'weba': 'webm'
}

for k, v in AUDIO_TYPES.items():
    for f in v:
        mimetypes.add_type(type=f, ext=k)


if __name__ == '__main__':
    print(mimetypes.guess_type('asdasdad.wav'))
    print(mimetypes.guess_all_extensions('audio/wav'))
    print(mimetypes.guess_all_extensions('audio/x-wav'))
    print(mimetypes.guess_all_extensions('audio/wave'))
    print(mimetypes.guess_all_extensions('audio/x-wave'))
