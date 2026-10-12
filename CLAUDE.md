# certonymity.com

Static site (no build step), published from `public/` on Netlify. Pages: `/`, `/about/`, `/contact/` and `/cemail-data-deletion`. The Netlify site is `cemail` (id in `.netlify/state.json`, gitignored). It is not linked to GitHub, so deploys are manual and only when asked: `npx netlify-cli deploy --prod --dir=public`, run from the repo root.

## Rule: keep SEO / GEO metadata in sync with the content

Whenever you change page copy, add, remove or rename a page, or change a company or product fact, update everything derived from it in the same change:

- Per page: `<title>`, meta description, `og:*`, `twitter:*`, canonical and JSON-LD.
- Site files: `public/sitemap.xml`, `public/llms.txt` (pages list, relationships, company details), `public/robots.txt`, `public/site.webmanifest`.
- Then run `python3 scripts/check-site.py`. It must exit 0 before any commit.

Consistency rules the script enforces: `og:title` and `twitter:title` equal `<title>`; `og:description` and `twitter:description` equal the meta description (160 characters max); `og:url` equals the canonical, which is listed in the sitemap; exactly one `<h1>` per page; every sitemap URL is linked from `llms.txt`; brand names are written c.Email, cDot and Certonymity. Update the script when the set of pages or expected links changes.

## Facts (single source of truth)

- Company: Certonymity Ltd, company no. 16871742, registered in England and Wales. Registered office: 86–87 Campden Street, London, W8 7EN. Email: info@certonymity.com.
- Relationship: Certonymity Ltd builds both products. c.Email (c.email) is the first product, live on iOS, Android and Chrome, and is built on the cDot framework. cDot (cdot.world) is the network for secure identity, communication and payments, built on the C-Layer, by the team behind c.Email. The cDot app (cdot.app) is the consumer product on the network.
- **Status: the cDot app and cdot.app are NOT live yet.** The homepage says "Coming soon" and the About page speaks of the app's release in the future. When it goes live, update the homepage ("Live now"), About, the cDot node in the homepage JSON-LD, `llms.txt` (relationship, pages, link to cdot.app's llms.txt), and the expected links in `scripts/check-site.py`.
- Related sites each publish their own `llms.txt`: `https://c.email/llms.txt` and `https://cdot.world/llms.txt`. Sibling repos are in `~/Documents/cdot-world`, `~/Documents/cdot-app` and `~/Documents/c.email-website`. Read them to keep facts consistent. Don't copy their prose, and don't edit them from this repo unless asked.

## Conventions

- Footer on every page: About, Contact, c.Email, cDot, then "© 2026 Certonymity" (a link to the homepage on every page except the homepage). The company details live on `/contact/`, together with the privacy notice (`/contact/#privacy`). There are no Terms or Privacy pages here, and `/terms` and `/privacy` are redirected in `public/_redirects`.
- External links open in a new tab with `rel="noopener noreferrer"`.
- Fonts are self-hosted (Inter, Darker Grotesque). Don't add third-party requests (fonts, analytics, embeds) without asking, because the site sets no cookies and has no consent banner.
- Git commits: don't add a Co-Authored-By line.
- Preview locally with `python3 -m http.server 8080 --directory public`, and hard-reload (Cmd+Shift+R), because the browser caches CSS.
