# Owen Johnson — professional portfolio

Dependency-free HTML, CSS, and JavaScript. Python 3.9+ generates the static pages from shared content. No backend or package installation required. All meaningful content and navigation work without JavaScript.

## Update personal details

Edit `data/profile.json`. Empty fields deliberately render as unavailable rather than fabricated or broken links.

- `email`: real email address.
- `linkedin`, `github`: full HTTPS profile URLs.
- `portrait`: local path, e.g. `assets/owen.jpg`; update `portraitAlt`.
- `resumePdf`: add the actual PDF as `assets/resume.pdf`, then set this field to `assets/resume.pdf`.
- `siteUrl`: actual deployed origin, e.g. `https://your-domain.example`. Enables canonical URLs and sitemap generation.

Run `python3 build.py` after editing data. Configured files must exist; invalid asset paths and URLs fail the build. Portraits use `object-fit: cover`; adjust `object-position` if needed. No fake résumé PDF is generated. `/resume/` contains a web résumé based only on supplied facts.

## Add or update projects

Edit `data/projects.json`, then run `python3 build.py`. Each record supports `slug`, `title`, `question`, `description`, `status`, `date`, `topics`, `visual`, `sections`, `images`, and `sources`. The homepage cards and detail pages use this same data. Only add projects actually being worked on; change status when supported by completed work.

Sections use `title` and `text`. An optional `table` object supports `caption`, `headers` (array), and `rows` (array of arrays). Tables receive a keyboard-accessible horizontal scrolling region on mobile. Images use `src`, meaningful `alt`, and optional `caption`. Sources use `title`, absolute HTTP(S) `url`, and optional `note`. Text is escaped rather than interpreted as HTML. For charts, export an SVG or image and add meaningful alt text and a caption describing the underlying data.

The `diagram()` function in `build.py` is the reusable research diagram. Update its stages and upstream inputs as research progresses. Its sequence becomes vertical on mobile. The current framework explicitly describes itself as conceptual, with no research findings claimed.

`build.py` also contains shared layout, contact, ProjectCard, ProjectPage, experience, and page metadata renderers. `style.css` defines site and report styles. `script.js` handles the accessible mobile menu (including Escape and focus restoration). Each generated route has its own title and metadata, one H1, and static content.

## Preview and verification

```sh
python3 build.py
python3 verify.py
python3 -m http.server 8000
```

Visit `http://localhost:8000`. Review at 375px, 768px, and desktop widths. Check keyboard focus, the mobile menu, project contents navigation, and the stacked diagram. No JavaScript test runner or lint configuration existed in the starter; verification uses Python's standard library. Google Fonts is optional: the site has local Arial/sans-serif fallbacks.

## Deploy to Cloudflare Pages

Connect this repository to Cloudflare Pages. Select no framework, use `python3 build.py` as the build command, and use `dist` as the output directory. The build creates a public-only distribution excluding source data and scripts. You can also upload `dist/` directly. Directory routes serve their `index.html`; the root `404.html` provides a real not-found page instead of an SPA fallback.

Never put private files or secrets inside public assets. Once the deployment URL is known, set `siteUrl` and rebuild. No deployment credentials or live hosting configuration were present, and no deployment is performed by the build. When removing a project or asset, use a fresh build checkout for deployment so old generated files are not retained.
