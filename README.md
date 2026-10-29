# Alvin Kallicharran website

A single-page site for Alvin Kallicharran BEM: his story, timeline, career scorecard, book, coaching, foundation, India tour, media, news and contact details.

Website created by Ritvik Shivakumar.

The site is plain HTML, CSS and a little JavaScript. A small Python script (standard library only) wraps the page into a complete document and writes the files to host into `dist/`.

## What is in the project

```
build_site.py        builds dist/, previews locally, and prepares new photos
src/page.html        the whole page: title, styles, content and scripts
src/photos/          web-ready photos (thumbnails and full size)
dist/                the built site, ready to host (rebuilt by build_site.py)
.github/workflows/   deploys to GitHub Pages on every push to main
```

## Build and preview

You need Python 3.8 or newer. Nothing to install.

```
python3 build_site.py            # writes dist/index.html and dist/photos/
python3 build_site.py serve      # builds, then opens a preview at http://localhost:8000
```

## Host it on Render

`render.yaml` defines a Render static site. In the Render dashboard choose **New**, then **Blueprint**, and select this repository. Render builds with `python3 build_site.py build` and publishes `dist/`. Every push to `main` redeploys.

To set it up by hand instead, create a **Static Site** with build command `python3 build_site.py build` and publish directory `dist`.

## Host it on GitHub Pages

1. Create a new repository on GitHub and push this folder to the `main` branch.
2. In the repository, open Settings, then Pages, and set Source to **GitHub Actions**.
3. Push any change. The workflow in `.github/workflows/pages.yml` builds the site and publishes it. The address appears on the Pages settings screen and in the workflow run.

`dist/` is committed so you can also host it anywhere that serves static files. To use Netlify, Cloudflare Pages, Vercel or a plain web server, upload the contents of `dist/` (or point the host at that folder with no build step).

## Edit the content

Open `src/page.html`. Sections appear in this order and each has an `id` you can search for:

`top` (opening banner), `story`, `timeline`, `cricket`, `book`, `academy` (coaching), `foundation`, `india`, `watch` (videos), `photos`, `news`, `contact`. The footer holds the website credit.

After editing, run `python3 build_site.py` again.

Colors, fonts and spacing are defined once at the top of the `<style>` block in `src/page.html` (the `:root` variables), with a separate set for dark mode.

## Adding photos

1. Put the original photos in any folder and run `python3 build_site.py optimize path/to/folder`. It writes `NAME-thumb.webp` and `NAME-full.webp` into `src/photos/`.
2. In `src/page.html`, copy one existing gallery button (look for `class="ph"`) into the "At the crease" or "Off the field" group and change the file names, caption and alt text:

```html
<button type="button" class="ph" data-full="photos/NAME-full.webp" data-cap="Caption" data-alt="Describe the photo" aria-label="Enlarge photo: Caption"><img src="photos/NAME-thumb.webp" width="640" height="480" alt="Describe the photo" loading="lazy"><span>Caption</span></button>
```

Set `width` and `height` to the thumbnail's real size (the optimize command prints it). The photo viewer picks up new buttons automatically.

## Before the site goes public

- **Photo rights.** Many gallery photos and the opening banner look like press or agency photos. Get licences or add credits, or replace them with photos you own.
- **Captions.** Gallery captions only describe what is visible. Replace them with real captions, dates and credits.
- **Videos.** The Media section links to YouTube searches and to his site for Cricket & Coffee with Kalli. Swap in direct video links.
- **Contact.** The page shows his email with a copy button, because a static site cannot send a contact form. The newsletter link goes to his current site.
- **Address.** His street address is listed in the Contact section as it appears on his own site. Remove it if you prefer.
- **Facts to confirm with Alvin.** Birthplace (Port Mourant on Wikipedia and Cricinfo, Georgetown on his site), where he is based (Charlotte coaching, Morrisville address), and the details of the Stanley School of Cricket.
- **Statistics.** Career figures come from ESPNcricinfo, Wikipedia and Wisden. Update them if needed.
- **Articles.** News cards link out to each publisher. Check the links still work before launch.

## Notes

- Fonts load from Google Fonts. If they are blocked, the page falls back to Georgia and system fonts.
- The page follows the visitor's light or dark setting.
- Everything outside `dist/` is source. Do not edit `dist/` by hand, because the next build overwrites it.
