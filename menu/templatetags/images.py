"""Serve media through Vercel's edge image optimizer in production."""

from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def thumb(url, width=640):
    """Resized, AVIF/WebP, edge-cached variant of an image URL.

    Locally there is no optimizer, so the original URL is returned. The
    width must be one of the sizes configured in vercel.json.
    """
    if not url or not getattr(settings, "VERCEL_IMAGE_OPTIMIZATION", False):
        return url
    return f"/_vercel/image?url={quote(str(url), safe='')}&w={width}&q=75"
