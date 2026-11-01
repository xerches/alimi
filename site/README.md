# alimi marketing site

Static [Astro](https://astro.build) site for https://alimibeta.netlify.app (the beta host until the domain exists). No client JavaScript, no webfonts, no server. Prices, partner terms, the insurer questions and the policy names are read from the repo at build time, so the site cannot drift from `config/pricing.yaml`, `config/checks.yaml` or `/policies`.

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
| Prices, tiers, partner terms | `config/pricing.yaml` | `src/lib/config.js` (`product()`, `partners()`, `retainer()`) |
| Insurer questions, check counts, the sample finding | `config/checks.yaml` | `src/lib/content.js` |
| Policy names on the Policy Pack page | `/policies/NN-*.md` front matter | `src/lib/content.js` |
| Name, tagline, founder, site URL, GitHub | `config/brand.yaml` | layout, header, footer, About |

A value of `TODO` in brand.yaml (domain, contact email, LinkedIn) renders as absent, so nothing fake ships. Placeholder copy is wrapped in the `<Todo>` component, visible on purpose; the build prints how many remain for prompt 11.

## Color system

One source of truth: the `colors` map in `config/brand.yaml`, grouped by purpose (brand, backgrounds and surfaces, text, borders, semantic, interactive states). Components use `var(--color-…)` only. Dark bands (header, footer, the `.dark` sections) switch to the `*_on_dark`, `*_inverse` and `*_dark` tokens through CSS, not through a second palette.

Two checks keep it honest:

- `tests/contrast.test.mjs` computes the WCAG ratio of every pairing the stylesheet relies on and fails under 4.5:1 for text and 3:1 for controls and focus rings.
- `scripts/check-dist.mjs` fails the build if any hex, `rgb()`, `hsl()` or named color appears in the built HTML outside the inlined token block. The favicon is generated from the same tokens by `src/pages/favicon.svg.js`.

## Pages and forms

| Page | Path | Netlify form |
| --- | --- | --- |
| Home | `/` | |
| Workspace Security Scan | `/workspace-security-scan` | `waitlist-workspace-scan` |
| Policy Pack | `/policy-pack` | `waitlist-policy-pack` |
| Payment Fraud Protection Kit | `/payment-fraud-kit` | `waitlist-payment-fraud-kit` |
| AI Policy Kit | `/ai-policy-kit` | `waitlist-ai-policy-kit` |
| For partners | `/for-partners` | `partners` |
| About | `/about` | |
| Contact | `/contact` | `contact` |
| Thank you | `/thank-you` | |
| Not found | `/404` | |

Forms are plain HTML with `data-netlify="true"`, a `bot-field` honeypot and a redirect to `/thank-you`. Netlify detects them from the built HTML; form detection is enabled on the site. Submissions arrive in the Netlify dashboard and by email notification, which is set there, not here.

## Deploy

`netlify.toml` at the repo root sets the base directory to `site`, the publish directory to `dist`, Node 22, security headers (a strict Content Security Policy, no framing, no sniffing) and a long cache for hashed assets. Pushes to `main` deploy automatically; pull requests get a deploy preview. The site builds to `/name.html`, which Netlify serves at `/name`.

## Checks in CI

`.github/workflows/site.yml` runs `npm ci`, `npm test`, `npm run build` and Lighthouse CI whenever `site/`, `config/`, `policies/` or `netlify.toml` change.

## Adding a page

1. Create `src/pages/<name>.astro`, wrap it in `Base` and pass `title`, `description` and `path="/<name>"`.
2. Use `Section`, `Hero`, `Steps`, `Pricing`, `Callout`, `WaitlistForm` from `src/components`.
3. Add it to the header links if it belongs in the main navigation.
4. Run `npm run build`; the checks tell you what is missing.
