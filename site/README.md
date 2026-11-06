# Alimi marketing site

Static [Astro](https://astro.build) site for https://alimibeta.netlify.app (the beta host until the domain exists). No webfonts, no server, and no client JavaScript except the pricing calculator and the theme toggle, both progressive enhancements (the page shows worked examples without the one, and follows the device's light or dark setting without the other). One offer, the Alimi platform. Prices, the framework catalog, partner terms, the insurer questions and the policy titles are read from the repo at build time, so the site cannot drift from `config/pricing.yaml`, `config/frameworks.yaml`, `config/checks.yaml`, `config/controls.yaml` or `/policies`. No policy text is rendered anywhere (Nov 2, 2026).

## Run it

```bash
cd site
npm ci
npm run dev          # http://localhost:4321
npm test             # config and contrast tests (node:test)
npm run build        # astro build, then scripts/check-dist.mjs
npm run lighthouse   # Lighthouse CI on dist/, 95+ required on every page; a page under the performance bar on one run is measured three more times and the median counts (scripts/lighthouse.mjs)
```

Node 22 or newer. Lighthouse needs a Chrome; set `CHROME_PATH` if it is not on the path.

## Where things come from

| What | Source | Read by |
| --- | --- | --- |
| Colors and fonts, in two themes | `config/brand.yaml` `colors` (light, the default), `colors_dark`, `typography` | `src/lib/tokens.js` turns a map into `--color-*` and `--font-*` custom properties; `src/lib/theme.js` inlines the light set as the default and the dark set under `prefers-color-scheme: dark` and under `[data-theme="dark"]`, in `<head>` by `src/layouts/Base.astro` |
| Per-user tiers, framework add-on pricing, billing terms, services, partner and reseller terms and incentives | `config/pricing.yaml` | `src/lib/config.js` (`platform()`, `quote()`, `frameworkPricing()`, `services()`, `partners()`, `resellerTiers()`, `retainer()`) |
| Framework catalog (49 entries in six categories, the Alimi Recommended Security Posture Score first) | `config/frameworks.yaml` | `src/lib/config.js` (`frameworkCatalog()`, `choosableFrameworks()`, `frameworksByCategory()`, `frameworkBySlug()`, `alwaysIncludedFrameworks()`) |
| Header menus, footer columns, the 404 and thank-you link lists | `src/lib/nav.js` | `Header.astro`, `Footer.astro`; `tests/nav.test.mjs` checks every path has a page |
| Insurer questions, check counts, the sample finding | `config/checks.yaml` | `src/lib/content.js` |
| Control counts, framework requirement counts | `config/controls.yaml`, `policies/requirements.yaml` | `src/lib/content.js` (`controlSummary()`, `mappedFrameworks()`) |
| Policy titles and count (front matter only, never the body) | `/policies/*.md` | `src/lib/content.js` (`policies()`) |
| Name, tagline, founder, site URL, demo URL (`demo_url`, the "See the product" links) | `config/brand.yaml` | layout, header, footer, home, platform, About |

A value of `TODO` in brand.yaml (domain, contact email, LinkedIn) renders as absent, so nothing fake ships. Placeholder copy, if any is ever needed again, goes in the `<Todo>` component, visible on purpose; the build prints how many remain (zero since prompt 11).

## Layout

Since Nov 3, 2026 the site wears the product's shell (the "B+" layout chosen for the demo and the platform), so a prospect sees one product from the first page to the app, with one difference the founder asked for: the menu runs across the top, not down the side.

- **Header, row one:** the app's ink strip of captioned icons, one per top-level menu (`icon` in `src/lib/nav.js`, drawn in `src/lib/icons.js`). The current section carries the app's highlight bar. Dropdowns are `<details>` elements, so they work without JavaScript; one bundled script closes the others when one opens.
- **Header, row two:** the app's light bar, here with a breadcrumb trail (`breadcrumbs()` in `nav.js`: Home, the menu that lists the page, the page) and the two links every page wants: "See the product" and "Work out your price".
- **Page:** the app's canvas (`background_alt`), white cards with a 10px radius, number tiles with a colored top edge (`.tile`), status pills with a dot (`.pill`), the app's buttons, tables and callouts.
- **Home hero (Nov 3, evening):** the product itself, beside the copy: the app's Home for the demo's sample company in a frame (`.frame`), with the renewal countdown, readiness with a bar (`.meter`), the Posture Score tile and the month's three items, labelled as a sample. On a wide screen the strip stays stuck to the top and the light bar scrolls away.
- **Motion:** CSS only, in the "Motion" block at the end of `global.css`, and none of it under `prefers-reduced-motion: reduce`: the hero settles on load, the bar fills, a linked card lifts under the pointer, and browsers that support scroll-driven animations reveal cards as they scroll in. Everything ends in its resting state.
- No webfonts, as before: `typography` in brand.yaml names Inter with system fallbacks, and the demo renders the same way.

## Color system and themes

One source of truth: the `colors` map in `config/brand.yaml`, grouped by purpose (brand, backgrounds and surfaces, text, borders, semantic, interactive states). Components use `var(--color-…)` only. Dark bands (header, footer, the `.dark` sections) switch to the `*_on_dark`, `*_inverse` and `*_dark` tokens through CSS, not through a second palette.

Two themes since Nov 3, 2026. `colors` is the light theme and the default. `colors_dark` lists the same keys for the dark theme; `src/lib/theme.js` inlines it under `@media (prefers-color-scheme: dark)` (for `:root:not([data-theme="light"])`) and under `:root[data-theme="dark"]`, so the site follows the device setting unless the visitor picks the other theme with the toggle in the top bar. `src/scripts/theme.js`, inlined in `<head>` by the layout so it costs no request and runs before first paint (the Content Security Policy in `netlify.toml` allows it by the hash of its exact text; change the file and the build check tells you to update the hash), sets `data-theme` on `<html>`, keeps the choice in `localStorage` under `alimi-theme` only when it differs from the device setting, and marks the toggle pressed when the dark theme is on. Without JavaScript the toggle is hidden and the device setting applies. The stylesheet never branches on the theme: only the tokens change. Two tokens exist for the labels whose background changes hue between themes: `primary_contrast` (white on indigo, ink on periwinkle) and `primary_on_dark_contrast` (ink on periwinkle in both).

Three checks keep it honest:

- `tests/contrast.test.mjs` computes the WCAG ratio of every pairing the stylesheet relies on, in both themes, and fails under 4.5:1 for text and 3:1 for controls and focus rings.
- `tests/theme.test.mjs` checks the inlined block carries both themes, the two maps share their keys, the theme script stays small and plain, and `netlify.toml` carries its current hash.
- `scripts/check-dist.mjs` fails the build if any hex, `rgb()`, `hsl()` or named color appears in a style context of the built HTML (every page, document pages included) outside the inlined token block, if a page lacks the dark tokens or the inlined theme script, or if that script's hash is not the one the Content Security Policy allows. The favicon is generated from the same tokens by `src/pages/favicon.svg.js`.

## Pages and forms

| Page | Path | Netlify form |
| --- | --- | --- |
| Home | `/` | |
| Platform (how it works, the modules) and one page per module with screens from the demo (`src/lib/modules.js`, `public/screens`) | `/platform`, `/platform/<module>` | |
| Integrations (a tile per connection, two connected, what each connection reads, what comes next) | `/integrations` | |
| Frameworks (the catalog by category) and one page per framework; the five mapped ones carry an owner's FAQ from `src/data/framework-faq.yaml` | `/frameworks`, `/frameworks/<slug>` | |
| Security (how the platform protects your data) | `/security` | |
| Solutions (by who sent you, industry, size, framework) | `/solutions` | |
| Pricing (catalog by group, add-on bands, calculator, worked examples, FAQ) | `/pricing` | `waitlist` |
| Compare (Alimi, Vanta, Drata; sourced) | `/compare` | |
| For partners | `/for-partners` | `partners` |
| For resellers (tiers, margin examples, the per-client arithmetic, incentives) | `/for-resellers` | |
| For insurance brokers, For CPAs (what each sees, what Alimi does for the client, the referral terms) | `/for-brokers`, `/for-accountants` | |
| Resources (library), Glossary, Help center, Academy, Community, Customer stories | `/resources`, `/glossary`, `/help`, `/academy`, `/community`, `/customers` | |
| About (mission, story, beliefs, leadership), Press, Careers | `/about`, `/press`, `/careers` | |
| Trust page, Status, Accessibility (what is tested, not a score), Legal, Privacy notice | `/trust`, `/status`, `/accessibility`, `/legal`, `/privacy` | |
| Contact | `/contact` | `contact` |
| Thank you | `/thank-you` | |
| Not found | `/404` | |

Pages added on Nov 2, 2026 for the sections Vanta and Drata have (solutions, integrations, customers, help, academy, community, press, careers, trust, status, legal) are honest placeholders where there is no content yet: each says what exists and what comes when. No scalable count (checks, controls, policies, requirement IDs) is printed on the site; the framework count is the one number allowed (founder's rule). `scripts/check-dist.mjs` also checks that every internal link and fragment resolves to a built page.

The old product URLs (`/workspace-security-scan`, `/policy-pack`, `/payment-fraud-kit`, `/ai-policy-kit`) redirect to the platform page and the former Free resources document pages (`/resources/*`) to the resource library in `netlify.toml`. Forms are plain HTML with `data-netlify="true"`, a `bot-field` honeypot and a redirect to `/thank-you`. Netlify detects them from the built HTML; form detection is enabled on the site. Submissions arrive in the Netlify dashboard and by email notification, which is set there, not here.

## Deploy

`netlify.toml` at the repo root sets the base directory to `site`, the publish directory to `dist`, Node 22, security headers (a strict Content Security Policy, no framing, no sniffing) and a long cache for hashed assets. The policy allows scripts from the site's own origin plus one inline script by hash (the theme script), so Astro's component scripts (the menu script, the pricing calculator) are emitted as files under `/_astro/` (`vite.build.assetsInlineLimit: 0` in `astro.config.mjs`); until Nov 3, 2026 Astro inlined them and the policy blocked them on the live site, which `scripts/check-dist.mjs` now catches by checking every inline script's hash against the policy. Pushes to `main` deploy automatically; pull requests get a deploy preview. The site builds to `/name.html`, which Netlify serves at `/name`.

## Checks in CI

`.github/workflows/site.yml` runs `npm ci`, `npm test`, `npm run build` and Lighthouse CI whenever `site/`, `config/`, `policies/` or `netlify.toml` change.

## Adding a page

1. Create `src/pages/<name>.astro`, wrap it in `Base` and pass `title`, `description` and `path="/<name>"`.
2. Use `Section`, `Hero`, `Steps`, `Tiers`, `PartnerTiers`, `Callout`, `WaitlistForm` from `src/components`.
3. Add it to the header links if it belongs in the main navigation.
4. Run `npm run build`; the checks tell you what is missing.
