"""Fetch follower count + latest posts for the Instagram card.

Runs in GitHub Actions (.github/workflows/instagram-refresh.yml).
Requires IG_ACCESS_TOKEN: a long-lived Instagram API token for the
flosfooddiaries professional account (runbook in CLAUDE.md).

Writes instagram.json and ig-1..3.webp (240x300, 4:5) in the repo root.
Exits non-zero on API errors so the workflow run shows as failed.
Side file .new-token holds a refreshed token for the workflow to store.
"""
import datetime
import io
import json
import os
import pathlib
import sys

import requests
from PIL import Image, ImageOps

API = 'https://graph.instagram.com/v23.0'
TOKEN = os.environ['IG_ACCESS_TOKEN'].strip()


def get(path, **params):
    params['access_token'] = TOKEN
    r = requests.get(f'{API}/{path}', params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def human(n):
    for cut, suffix in ((1_000_000, 'M'), (1_000, 'K')):
        if n >= cut:
            return f'{n / cut:.1f}'.rstrip('0').rstrip('.') + suffix
    return str(n)


me = get('me', fields='username,followers_count')
media = get('me/media', fields='media_type,media_url,thumbnail_url,caption,permalink', limit=10)

posts = []
for m in media.get('data', []):
    url = m.get('thumbnail_url') if m.get('media_type') == 'VIDEO' else m.get('media_url')
    if not url:
        continue
    caption = (m.get('caption') or '').split('\n')[0][:80].strip()
    posts.append({'url': url, 'alt': caption or 'Instagram post', 'permalink': m.get('permalink')})
    if len(posts) == 3:
        break

if len(posts) < 3:
    sys.exit('fewer than 3 usable posts returned')

meta = []
for i, p in enumerate(posts, 1):
    img = ImageOps.exif_transpose(
        Image.open(io.BytesIO(requests.get(p['url'], timeout=30).content))).convert('RGB')
    w, h = img.size
    tw, th = (w, int(w * 5 / 4)) if h >= w * 5 / 4 else (int(h * 4 / 5), h)
    img = img.crop(((w - tw) // 2, (h - th) // 2, (w + tw) // 2, (h + th) // 2))
    img.resize((240, 300), Image.LANCZOS).save(f'ig-{i}.webp', 'WEBP', quality=80)
    meta.append({'file': f'ig-{i}.webp', 'alt': p['alt'], 'permalink': p['permalink']})

pathlib.Path('instagram.json').write_text(json.dumps({
    'handle': me['username'],
    'followers': human(me['followers_count']),
    'followers_count': me['followers_count'],
    'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
    'source': 'instagram-graph-api',
    'posts': meta,
}, indent=1) + '\n')

# Long-lived tokens last 60 days; refresh on every run. The workflow
# stores the new one only if a rotation PAT is configured.
try:
    r = requests.get('https://graph.instagram.com/refresh_access_token',
                     params={'grant_type': 'ig_refresh_token', 'access_token': TOKEN}, timeout=30)
    if r.ok and r.json().get('access_token'):
        pathlib.Path('.new-token').write_text(r.json()['access_token'])
except requests.RequestException as e:
    print(f'token refresh skipped: {e}')

print(f"ok: {me['username']}, {me['followers_count']} followers, {len(meta)} posts")
