# Alimi marketing site

Static [Astro](https://astro.build) site for https://alimibeta.netlify.app (the beta host until the domain exists). No webfonts, no server, and no client JavaScript except the pricing calculator, which is a progressive enhancement (the page shows worked examples without it). One offer, the Alimi platform. Prices, the framework catalog, partner terms, the insurer questions and the policy titles are read from the repo at build time, so the site cannot drift from `config/pricing.yaml`, `config/frameworks.yaml`, `config/checks.yaml`, `config/controls.yaml` or `/policies`. No policy text is rendered anywhere (Nov 2, 2026).

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
| Per-user tiers, framework add-on pricing, billing terms, services, partner and reseller terms and incentives | `config/pricing.yaml` | `src/lib/config.js` (`platform()`, `quote()`, `frameworkPricing()`, `services()`, `partners()`, `resellerTiers()`, `retainer()`) |
| Framework catalog (49 entries in six categories, the Alimi Recommended Security Posture Score first) | `config/frameworks.yaml` | `src/lib/config.js` (`frameworkCatalog()`, `choosableFrameworks()`, `frameworksByCategory()`, `frameworkBySlug()`, `alwaysIncludedFrameworks()`) |
| Header menus, footer columns, the 404 and thank-you link lists | `src/lib/nav.js` | `Header.astro`, `Footer.astro`; `tests/nav.test.mjs` checks every path has a page |
| Insurer questions, check counts, the sample finding | `config/checks.yaml` | `src/lib/content.js` |
| Control counts, framework requirement counts | `config/controls.yaml`, `policies/requirements.yaml` | `src/lib/content.js` (`controlSummary()`, `mappedFrameworks()`) |
| Policy titles and count (front matter only, never the body) | `/policies/*.md` | `src/lib/content.js` (`policies()`) |
| Name, tagline, founder, site URL, demo URL (`demo_url`, the "See the product" links) | `config/brand.yaml` | layout, header, footer, home, platform, About |

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
| Platform (how it works, the modules) | `/platform` | |
| Integrations (what each connection reads, what comes next) | `/integrations` | |
| Frameworks (the catalog by category) and one page per framework | `/frameworks`, `/frameworks/<slug>` | |
| Security (how the platform protects your data) | `/security` | |
| Solutions (by who sent you, industry, size, framework) | `/solutions` | |
| Pricing (catalog by group, add-on bands, calculator, worked examples, FAQ) | `/pricing` | `waitlist` |
| Compare (Alimi, Vanta, Drata; sourced) | `/compare` | |
| For partners | `/for-partners` | `partners` |
| For resellers (tiers, margin examples, incentives) | `/for-resellers` | |
| Resources (library), Glossary, Help center, Academy, Community, Customer stories | `/resources`, `/glossary`, `/help`, `/academy`, `/community`, `/customers` | |
| About (mission, story, beliefs, leadership), Press, Careers | `/about`, `/press`, `/careers` | |
| Trust page, Status, Legal, Privacy notice | `/trust`, `/status`, `/legal`, `/privacy` | |
| Contact | `/contact` | `contact` |
| Thank you | `/thank-you` | |
| Not found | `/404` | |

Pages added on Nov 2, 2026 for the sections Vanta and Drata have (solutions, integrations, customers, help, academy, community, press, careers, trust, status, legal) are honest placeholders where there is no content yet: each says what exists and what comes when. No scalable count (checks, controls, policies, requirement IDs) is printed on the site; the framework count is the one number allowed (founder's rule). `scripts/check-dist.mjs` also checks that every internal link and fragment resolves to a built page.

The old product URLs (`/workspace-security-scan`, `/policy-pack`, `/payment-fraud-kit`, `/ai-policy-kit`) redirect to the platform page and the former Free resources document pages (`/resources/*`) to the resource library in `netlify.toml`. Forms are plain HTML with `data-netlify="true"`, a `bot-field` honeypot and a redirect to `/thank-you`. Netlify detects them from the built HTML; form detection is enabled on the site. Submissions arrive in the Netlify dashboard and by email notification, which is set there, not here.

## Deploy

`netlify.toml` at the repo root sets the base directory to `site`, the publish directory to `dist`, Node 22, security headers (a strict Content Security Policy, no framing, no sniffing) and a long cache for hashed assets. Pushes to `main` deploy automatically; pull requests get a deploy preview. The site builds to `/name.html`, which Netlify serves at `/name`.

## Checks in CI

`.github/workflows/site.yml` runs `npm ci`, `npm test`, `npm run build` and Lighthouse CI whenever `site/`, `config/`, `policies/` or `netlify.toml` change.

## Adding a page

1. Create `src/pages/<name>.astro`, wrap it in `Base` and pass `title`, `description` and `path="/<name>"`.
2. Use `Section`, `Hero`, `Steps`, `Tiers`, `PartnerTiers`, `Callout`, `WaitlistForm` from `src/components`.
3. Add it to the header links if it belongs in the main navigation.
4. Run `npm run build`; the checks tell you what is missing.
