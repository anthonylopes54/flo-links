# Flo's Links — self-hosted link-in-bio page

Free replacement for the paid Linktree at linktr.ee/f.olguin.fdz, for the food
creator flo_olguin (Flo's Food Diaries). Built in a Claude chat; this repo is
now the project's home.

## Files
- `index.html` — the entire site in one self-contained file (~210 KB). The
  background photo (WebP), favicon (PNG), and apple-touch-icon (JPEG) are
  embedded as base64 data URIs; all CSS is inline. Only external dependency:
  Google Fonts (Fraunces + Inter).
- `og.jpg` — 1200×630 share-preview image referenced by the og:image tags.
  Must be deployed next to index.html.
- `floEatingFood.jpeg` — original source photo (previously named
  IMG_8044.jpeg), only needed to regenerate images. Not committed to git.

## Hard constraints
- Stay a single self-contained `index.html`: no frameworks, no build step,
  no npm, no separate CSS/JS files. Images stay embedded as base64.
- Don't change the visual design without asking. Current design: full-bleed
  fixed background photo (`background-position: 50% 22%` keeps the subject's
  face clear), dark gradient scrim heavier at the bottom, bottom-anchored
  content with `padding-top: 40vh`, frosted-glass pill buttons
  (backdrop-filter blur, `rgba(255,255,255,.14)` fill, 1px translucent
  border, `@supports` solid fallback), name in Fraunces 600, everything else
  Inter, rem-based type.
- Keep the exact link titles, order, URLs, and the 4-line emoji bio unless
  told otherwise. The Substack and YouTube links intentionally carry
  `?utm_source=bio_link&utm_medium=link_page`.
- Each button has `data-goatcounter-click="substack|instagram|buymeacoffee|youtube|tiktok|facebook"`
  — inert until analytics is enabled. Leave the GoatCounter script at the
  bottom of the file commented out unless asked to enable it.

## Regenerating embedded images (Pillow, from floEatingFood.jpeg)
- Always `ImageOps.exif_transpose` first.
- Background: resize to 1280 px wide, save WebP quality 80.
- Avatar crop (basis for icons): square of side = image width, top offset =
  10% of image height (keeps the face upper-center).
- Favicon: avatar crop → 64 px, circular alpha mask, PNG.
- Touch icon: avatar crop → 180 px, JPEG quality 82.
- og.jpg: full-width band with 1.905:1 aspect, vertically centered at 30% of
  image height, resized to 1200×630, JPEG quality 82.
Then base64-encode and splice into the matching `data:` URIs in index.html.

## Deployment (July 19, 2026)
- Live at https://flosfooddiaries.com/ — GitHub Pages, deploy-from-branch:
  `main`, root folder. Pushing to `main` redeploys (~1 min; CDN caches
  pages up to 10 min). HTTPS enforced (Let's Encrypt via GitHub).
- Domain: flosfooddiaries.com, registered at Cloudflare Registrar. DNS on
  Cloudflare in DNS-only mode (grey cloud — do NOT enable the orange-cloud
  proxy; it breaks GitHub's cert renewal): 4 A records on the apex to the
  GitHub Pages IPs (185.199.108-111.153) and a `www` CNAME to
  anthonylopes54.github.io. www and the old github.io URL 301 to the apex.
- Repo: https://github.com/anthonylopes54/flo-links (public). Tracked:
  `index.html`, `og.jpg`, `CNAME`. The `gh` CLI is installed and
  authenticated as anthonylopes54.
- Analytics: GoatCounter, account code `flo-links` — dashboard at
  https://flo-links.goatcounter.com. Script active at the
  bottom of index.html; buttons report click names via
  data-goatcounter-click. No cookies, so no consent banner.
- Local preview: `.claude/launch.json` serves the folder at
  http://localhost:8923 (python3 http.server).

## Later, optional
- Verify the domain at the GitHub account level (Settings → Pages →
  Verified domains, TXT record) to guard against takeover.
