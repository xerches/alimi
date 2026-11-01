# Decisions log

Newest first. One line per decision: date, what, why.

| Date | Decision | Why |
| --- | --- | --- |
| 2026-11-01 | Payment fraud kit ships as five Markdown documents (procedure, callback scripts, poster, Massachusetts closing checklist, training script) with three fixed rules: verified callback to a number already on file, two people above a threshold and on every bank-detail change, 24-hour hold on new details | The rules match what the FBI and title insurers advise and what cyber insurers ask about funds-transfer fraud; documents only, so it ships on the $0 path and feeds the half-day workshop |
| 2026-11-01 | Policy library ships as 23 Markdown policies with YAML front matter, a requirements catalogue (SOC 2, ISO 27001, ISO 42001, HIPAA Security Rule, insurer questions) holding only criterion IDs and our own one-line summaries, a generated coverage matrix, a pandoc build with --fill and a --final gate, and tests | Every requirement ID is covered by at least one policy, so the pack can be sold and audited on its own; the platform and the AI policy kit read the same front matter; no framework text is stored, which keeps the copyright rule |
| 2026-11-01 | Working name is alimi; denimi retired after one day | Founder prefers the sound; denimi risks the "denim" autocorrect in search; no security company or US trademark found under alimi on a first web check; MA entity, USPTO and domain checks still pending |
| 2026-11-01 | Policy library in /policies mapped to SOC 2, ISO 27001 and ISO 42001 by criterion ID; sold as a policy pack and reused by the platform and the AI policy kit | Every compliance buyer needs policies first; writing them once feeds the services, the platform and the kits |
| 2026-11-01 | Reseller program for MSPs: wholesale tiers of 20/30/40% by active client count, white-label, not-for-resale licence; 10% referral fee for brokers, CPAs and attorneys | Resellers need margin to sell on our behalf; starting numbers, confirm before the first partner conversation |
| 2026-11-01 | Build order: workspace scanner and insurer report first, payment fraud kit second, AI policy kit third | Founder wants a Vanta/Drata-style product; the scanner is its first module and sells on its own |
| 2026-11-01 | The scanner grows into a hosted compliance platform (phases 3-4); stack is Python, FastAPI, HTMX, Postgres | One language, reuses the scanner package; plan at https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a |
| 2026-11-01 | The report is one self-contained HTML page with print CSS; PDF comes from WeasyPrint as an optional extra, and the free summary must print on one page | HTML needs no system libraries and prints to PDF from any browser; one page is what a broker will actually read |
| 2026-11-01 | Google Workspace is read through a service account with domain-wide delegation and six read-only scopes; a setting no API exposes (the API controls restriction on unconfigured third-party apps) becomes an attestation finding with a screenshot ask, never a guess | Same honest-gaps rule as Microsoft 365; the scopes are listed in code so the README cannot drift |
| 2026-11-01 | The hosted platform holds no customer data until LLC, insurance, a signed pilot letter and an outside security review exist | Storing other companies' tokens is the biggest liability a security company can take on |
| 2026-10-31 | Working name is alimi; Caprius retired | Founder wanted a rebrand; name passes a first web check, formal checks pending |
| 2026-10-31 | Build three products first: AI policy kit, workspace scanner, payment fraud kit | One buyer, one referral network, each has a free product tier and a paid service tier |
| 2026-10-31 | Consulting and products first, MSP/MSSP later | Resume is GRC-heavy; a solo MSP needs ~210 seats to match 4-5 consulting clients |
| 2026-10-31 | No LLC until one referrer and one paid pilot exist | Massachusetts LLC costs $500 to file and $500 a year; nothing to protect yet |
