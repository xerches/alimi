// @ts-check
import { defineConfig } from "astro/config";

// Static output, no adapter. Pages build to /name.html so Netlify serves them at /name. The demo
// has its own unlisted site; DEMO_SITE_URL overrides the address for canonical links.
export default defineConfig({
  site: process.env.DEMO_SITE_URL || "https://alimi-demo.netlify.app",
  output: "static",
  trailingSlash: "never",
  build: { format: "file", inlineStylesheets: "always" },
  compressHTML: true,
  devToolbar: { enabled: false },
});
