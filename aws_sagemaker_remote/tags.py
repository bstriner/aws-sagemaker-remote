import re
MAX_LENGTH = 256
SUFFIX = '...'


def clip_tag(value, max_length=MAX_LENGTH, suffix=SUFFIX):
    if len(value) > max_length:
        return "{}{}".format(value[:max_length-len(SUFFIX)], suffix)
    else:
        return str(value)


def clean_tag(value:str):
    value = value.strip()
    value = re.sub("\\s+", "-", value)
    value = "".join(re.findall("[\\w\\=\\-\\.:_\\+@/]", value))
    return value


def make_tags(tags):
    tags = [
        {
            "Key": k,
            "Value": clip_tag(clean_tag(v))
        }
        for k, v in tags.items() if v
    ]
    tags = [tag for tag in tags if tag['Value']]
    return tags

if __name__=='__main__':
    print(clean_tag("[a]sd a/sd-_/+@"))