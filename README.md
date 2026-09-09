# phosphorscrt.com

Marketing site for **Phosphors CRT**, the physical-phosphor CRT simulator for
macOS. Static HTML, CSS and a dozen lines of JS. No build step, no
dependencies. Hosted on GitHub Pages.

- App: https://apps.apple.com/us/app/phosphors-crt/id6784439481?mt=12
- App repo: `../../Swift/Phosphors` (private), engine: `../../Swift/CRTEngine` (private)

## Layout

```
index.html          Landing page: hero, why it's different, features, pipeline,
                    display types, recording, pricing, FAQ
how-it-works.html   Long-form explanation of the simulation (beam, phosphor,
                    mask, signal path, display pass, audio)
support.html        Support page (App Store "Support URL")
privacy.html        Privacy policy (App Store "Privacy Policy URL")
404.html            Not-found page
assets/css/site.css All styles
assets/js/site.js   Mobile nav toggle
assets/img/         Icon renditions and screenshots
```

## Preview locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

GitHub Pages, serving the `main` branch from `/` (root). Every push to
`main` deploys. `.nojekyll` is present so nothing is preprocessed.

Enable once, after the repo exists:

```
gh repo create spetrequin/phosphorscrt --public --source . --push
gh api -X POST repos/spetrequin/phosphorscrt/pages -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/'
```

The site is then live at https://spetrequin.github.io/phosphorscrt/.

## Switching on the custom domain (phosphorscrt.com)

Two steps, whenever you are ready. Nothing on the site needs to change; the
canonical URLs already point at phosphorscrt.com.

1. **DNS at the registrar.** Add these records:

   | Type  | Host | Value                       |
   |-------|------|-----------------------------|
   | A     | @    | 185.199.108.153             |
   | A     | @    | 185.199.109.153             |
   | A     | @    | 185.199.110.153             |
   | A     | @    | 185.199.111.153             |
   | CNAME | www  | spetrequin.github.io        |

2. **Tell GitHub Pages.** Either add a file named `CNAME` at the repo root
   containing the single line `phosphorscrt.com` and push, or set the custom
   domain in the repo's Settings → Pages. Tick "Enforce HTTPS" once the
   certificate is issued (usually within an hour of DNS propagating).

Until step 2 is done, do not commit a `CNAME` file: GitHub redirects the
github.io URL to the custom domain as soon as the file exists, which breaks the
site if DNS is not ready.

After the domain is live, update the Support URL and Privacy Policy URL in
App Store Connect to `https://phosphorscrt.com/support.html` and
`https://phosphorscrt.com/privacy.html`. The old phosphors-site pages can
then be replaced with redirects or retired.

## Imagery: what is real and what to capture

Everything on the site today comes from one real asset, the App Store
screenshot (VGA monitor preset, 4K render, stripe mask, 158% zoom), plus the
app icon. That screenshot predates 1.0.4: its Output section still shows "HDR
Brightness" and "Smooth Color", which are now "Peak Highlights" and Pattern
Focus. It should be replaced.

Shot list, in priority order. Capture at 2× (Retina) so they stay sharp.

1. **Hero app window, current UI.** Same framing as the existing screenshot,
   NTSC color preset on a colourful clip, settings panel visible, 2880×1800
   or larger. Replaces `assets/img/app-vga-monitor-2000.jpg`.
2. **Phosphor detail crop.** Viewing zoom pushed high on a face or bright
   highlight so individual RGB stripes and scanlines resolve. About 1120×700.
   Replaces `assets/img/detail-stripes.jpg`.
3. **Picture only, one per display type.** Six 4:3 recordings or frame grabs:
   NTSC color, NTSC B&W, VGA, Green, Amber, B&W monitor. Same source clip
   for all six so the comparison reads. About 1600 px wide each. These would
   turn the display-type table into a visual gallery.
4. **Signal path row.** The same freeze frame through RF, Composite, S-Video
   and Component so dot crawl and snow are visible side by side.
5. **Mask geometry trio.** Deep zoom on aperture grille, slot mask and
   shadow mask, ideally over a white or grey field. Would replace the SVG
   diagram in the "not a filter" section.
6. **A 10 to 15 second looping hero video.** A music-video style clip
   recorded through Phosphors at 1080p, H.264 Web tier, muted. Sits in the
   hero in place of the static crop. Keep it under 4 MB.
7. **Conditions.** One frame each of a torn H-Hold and a rolling V-Hold,
   for the Conditions feature card.

Drop replacements into `assets/img/` under the same filenames and nothing
else needs editing.

## Copy sources

Every claim on the site is taken from the shipped app's Help book, the App
Store listing, or CRTEngine's physics documentation. Deliberately not claimed:
playback smoothness or A/V sync (per the 1.0.4 notes-to-self), and any
frame-rate or GPU numbers.
