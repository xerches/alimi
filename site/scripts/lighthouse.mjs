// Lighthouse CI in two passes (Nov 6, 2026). One run per page, which takes about six minutes for the pages
// in lighthouserc.json, catches a regression. A performance score on a shared runner can still dip on one
// run of a heavy page while the same commit passes on the next (the home page scored 0.91 and Pricing 0.94
// on one run of PR #30 and 100 on the other), so the pages that fail on performance alone are measured
// again, three runs with the median asserted, the setup Lighthouse CI recommends. A failure in any other
// category (accessibility, best practices, SEO) is deterministic and fails at once. While every page
// passes this costs nothing extra, which matters once the repository is private and Actions minutes
// are metered. Exits with Lighthouse CI's own status.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";

const cli = createRequire(import.meta.url).resolve("@lhci/cli/src/cli.js");
const autorun = (args) => spawnSync(process.execPath, [cli, "autorun", ...args], { stdio: "inherit" }).status ?? 1;

const first = autorun([]);
if (first === 0) process.exit(0);

const results = ".lighthouseci/assertion-results.json";
if (!existsSync(results)) process.exit(first);
const failed = JSON.parse(readFileSync(results, "utf8")).filter((r) => r.level === "error" && !r.passed);
const performanceOnly = failed.every((r) => r.auditId === "categories" && r.auditProperty === "performance");
if (failed.length === 0 || !performanceOnly) process.exit(first);

const pages = [...new Set(failed.map((r) => new URL(r.url).pathname))];
console.log(`\nlighthouse: performance under the bar on one run of ${pages.join(", ")}; measuring again, three runs, median.\n`);
process.exit(autorun(["--collect.numberOfRuns=3", "--assert.aggregationMethod=median", ...pages.map((p) => `--collect.url=http://localhost${p}`)]));
