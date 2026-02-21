from django.conf import settings
import os


def sidebar_history(request):
    """Return a small list of recent uploaded files for the sidebar."""
    out = []
    media_dir = settings.MEDIA_ROOT
    try:
        if os.path.exists(media_dir):
            for fname in os.listdir(media_dir):
                fpath = os.path.join(media_dir, fname)
                if os.path.isfile(fpath):
                    out.append({
                        'name': fname,
                        'url': settings.MEDIA_URL + fname,
                    })
    except Exception:
        out = []

    # newest first and limit
    out = list(reversed(out))[:10]
    return {'sidebar_history_files': out}
