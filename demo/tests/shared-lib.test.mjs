// The demo keeps byte-for-byte copies of the site's config, token and contrast helpers (the two
// projects install their own dependencies, so they cannot import across). This test keeps the copies
// identical, so config/brand.yaml stays the one source of truth for both.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
for (const file of ["config.js", "tokens.js", "contrast.js"]) {
  test(`src/lib/${file} matches site/src/lib/${file}`, () => {
    const ours = readFileSync(path.join(here, "../src/lib", file), "utf8");
    const theirs = readFileSync(path.join(here, "../../site/src/lib", file), "utf8");
    assert.equal(ours, theirs, `${file} differs from the site's copy; copy it over (cp ../site/src/lib/${file} src/lib/)`);
  });
}
