"""Static resource references for portable related-document copies.

CSS syntax is delegated to tinycss2. Nothing is fetched or executed.
"""
import re

import tinycss2


def srcset_urls(value):
    """HTML's URL-token/descriptor split, preserving commas inside data URLs."""
    rest = value
    while rest.strip(" \t\r\n\f,"):
        rest = rest.lstrip(" \t\r\n\f,")
        match = re.match(r"[^\t\n\f\r ]+", rest)
        url = match[0]
        rest = rest[len(url):]
        if url.endswith(","):
            yield url.rstrip(",")
            continue
        descriptors, separator, remainder = rest.partition(",")
        if any(not re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+)[wxh]", word)
               for word in descriptors.split()):
            raise ValueError("Unsupported or malformed srcset descriptor")
        yield url
        rest = remainder if separator else ""


def _token_urls(tokens):
    for token in tokens:
        if token.type == "error":
            raise ValueError("Malformed CSS cannot establish portable dependencies")
        if token.type == "url":
            yield token.value
        elif token.type == "function":
            arguments = [part for part in token.arguments if part.type not in {"whitespace", "comment"}]
            if token.lower_name == "url":
                if len(arguments) != 1 or arguments[0].type != "string":
                    raise ValueError("Unsupported CSS URL function")
                yield arguments[0].value
            else:
                if token.lower_name in {"image-set", "-webkit-image-set"}:
                    yield from (part.value for part in arguments if part.type == "string")
                yield from _token_urls(token.arguments)
        elif hasattr(token, "content"):
            yield from _token_urls(token.content)


def css_urls(value, *, inline=False):
    if inline:
        yield from _token_urls(tinycss2.parse_component_value_list(value))
        return
    rules = (tinycss2.parse_stylesheet_bytes(value)[0] if isinstance(value, bytes)
             else tinycss2.parse_stylesheet(value))
    for rule in rules:
        if rule.type == "error":
            raise ValueError("Malformed stylesheet cannot establish portable dependencies")
        prelude = getattr(rule, "prelude", [])
        if rule.type == "at-rule" and rule.lower_at_keyword == "import":
            significant = [part for part in prelude if part.type not in {"whitespace", "comment"}]
            if significant and significant[0].type == "string":
                yield significant[0].value
        yield from _token_urls(prelude)
        if getattr(rule, "content", None) is not None:
            yield from _token_urls(rule.content)


def resource_urls(soup):
    """Yield ordinary URL attributes and static CSS/srcset dependencies."""
    for tag in soup.find_all(True):
        for attribute in ("href", "src", "poster", "data", "xlink:href"):
            if tag.get(attribute):
                yield tag.get(attribute), tag.name == "a"
        for attribute in ("srcset", "imagesrcset"):
            if tag.get(attribute):
                yield from ((url, False) for url in srcset_urls(tag[attribute]))
        if tag.get("style"):
            yield from ((url, False) for url in css_urls(tag["style"], inline=True))
        if tag.name == "style":
            yield from ((url, False) for url in css_urls(tag.get_text()))
