# alimi marketing site

Static [Astro](https://astro.build) site for https://alimibeta.netlify.app (the beta host until the domain exists). No client JavaScript, no webfonts, no server. One offer, the alimi platform. Prices, partner terms, the insurer questions, the control counts and the free documents are read from the repo at build time, so the site cannot drift from `config/pricing.yaml`, `config/checks.yaml`, `config/controls.yaml`, `/policies` or `/kits`.

## Run it

```bash
cd site
npm ci
npm run dev          # http://localhost:4321
npm test             # config and contrast tests (node:test)
npm run build        # astro build, then scripts/check-dist.mjs
npm run lighthouse   # Lighthouse CI on dist/, 95+ required on every page
```

Node 22 or newer. Lighthouse needs a Chrome; set `CHROME_PATH` if it is not on the path.

## Where things come from

| What | Source | Read by |
| --- | --- | --- |
| Colors and fonts | `config/brand.yaml` `colors`, `typography` | `src/lib/tokens.js` turns them into `--color-*` and `--font-*` custom properties, inlined in `<head>` by `src/layouts/Base.astro` |
| Platform tiers, services, free resources, partner terms | `config/pricing.yaml` | `src/lib/config.js` (`platform()`, `services()`, `freeResources()`, `partners()`, `retainer()`) |
| Insurer questions, check counts, the sample finding | `config/checks.yaml` | `src/lib/content.js` |
| Control counts, framework requirement counts | `config/controls.yaml`, `policies/requirements.yaml` | `src/lib/content.js` (`controlSummary()`, `frameworks()`) |
| Free documents (three core policies, the AI policy, the payment fraud procedure) as pages | `/policies/*.md`, `/kits/payment-fraud/*.md` (front matter + body, rendered with `marked`) | `src/lib/content.js` (`freeDocs()`, `freeDoc()`), `src/pages/resources/[slug].astro` |
| Name, tagline, founder, site URL, GitHub | `config/brand.yaml` | layout, header, footer, About |

A value of `TODO` in brand.yaml (domain, contact email, LinkedIn) renders as absent, so nothing fake ships. Placeholder copy, if any is ever needed again, goes in the `<Todo>` component, visible on purpose; the build prints how many remain (zero since prompt 11).

## Color system

One source of truth: the `colors` map in `config/brand.yaml`, grouped by purpose (brand, backgrounds and surfaces, text, borders, semantic, interactive states). Components use `var(--color-…)` only. Dark bands (header, footer, the `.dark` sections) switch to the `*_on_dark`, `*_inverse` and `*_dark` tokens through CSS, not through a second palette.

Two checks keep it honest:

- `tests/contrast.test.mjs` computes the WCAG ratio of every pairing the stylesheet relies on and fails under 4.5:1 for text and 3:1 for controls and focus rings.
- `scripts/check-dist.mjs` fails the build if any hex, `rgb()`, `hsl()` or named color appears in a style context of the built HTML (every page, document pages included) outside the inlined token block. The favicon is generated from the same tokens by `src/pages/favicon.svg.js`.

## Pages and forms

| Page | Path | Netlify form |
| --- | --- | --- |
| Home | `/` | |
| Platform | `/platform` | |
| Pricing | `/pricing` | `waitlist` |
| Free resources | `/resources` | `resources` |
| A free document | `/resources/<slug>` (eight pages from `FREE_DOCS` in `content.js`) | |
| For partners | `/for-partners` | `partners` |
| About | `/about` | |
| Contact | `/contact` | `contact` |
| Thank you | `/thank-you` | |
| Not found | `/404` | |

The old product URLs (`/workspace-security-scan`, `/policy-pack`, `/payment-fraud-kit`, `/ai-policy-kit`) redirect in `netlify.toml`. Forms are plain HTML with `data-netlify="true"`, a `bot-field` honeypot and a redirect to `/thank-you`. Netlify detects them from the built HTML; form detection is enabled on the site. Submissions arrive in the Netlify dashboard and by email notification, which is set there, not here.

## Deploy

`netlify.toml` at the repo root sets the base directory to `site`, the publish directory to `dist`, Node 22, security headers (a strict Content Security Policy, no framing, no sniffing) and a long cache for hashed assets. Pushes to `main` deploy automatically; pull requests get a deploy preview. The site builds to `/name.html`, which Netlify serves at `/name`.

## Checks in CI

`.github/workflows/site.yml` runs `npm ci`, `npm test`, `npm run build` and Lighthouse CI whenever `site/`, `config/`, `policies/` or `netlify.toml` change.

## Adding a page

1. Create `src/pages/<name>.astro`, wrap it in `Base` and pass `title`, `description` and `path="/<name>"`.
2. Use `Section`, `Hero`, `Steps`, `Tiers`, `PartnerTiers`, `Callout`, `WaitlistForm` from `src/components`.
3. Add it to the header links if it belongs in the main navigation.
4. Run `npm run build`; the checks tell you what is missing.
