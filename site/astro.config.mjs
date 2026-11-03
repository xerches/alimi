// @ts-check
import { defineConfig } from "astro/config";
import { brand } from "./src/lib/config.js";

// Static output, no adapter. Pages build to /name.html so Netlify serves them at /name (its pretty
// URLs), which is also what the forms' thank-you redirect expects. Component scripts (the menu
// script, the pricing calculator) are emitted as files under /_astro/, never inlined: the Content
// Security Policy in netlify.toml allows scripts from the site's own origin and one hashed inline
// script (the theme script), and an inlined bundle would be blocked; scripts/check-dist.mjs checks
// every inline script against the policy.
export default defineConfig({
  site: brand.site_url,
  output: "static",
  trailingSlash: "never",
  build: { format: "file", inlineStylesheets: "always" },
  vite: { build: { assetsInlineLimit: 0 } },
  compressHTML: true,
  devToolbar: { enabled: false },
});
