// @ts-check
import { defineConfig } from "astro/config";
import { brand } from "./src/lib/config.js";

// Static output, no adapter, no client JavaScript. Pages build to /name.html so Netlify serves
// them at /name (its pretty URLs), which is also what the forms' thank-you redirect expects.
export default defineConfig({
  site: brand.site_url,
  output: "static",
  trailingSlash: "never",
  build: { format: "file", inlineStylesheets: "always" },
  compressHTML: true,
  devToolbar: { enabled: false },
});
