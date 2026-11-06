# Founder's agenda: open items, with dates

Started Nov 2, 2026 at the founder's request ("add to our agenda at some point to review end-user training modules"). One line per item, newest at the bottom of each section; move an item to `decisions.md` when it is decided and delete it here. CLAUDE.md points here for anything that waits on the founder.

## Waiting on the founder now

| Item | Why | Where it lands |
| --- | --- | --- |
| Pick the module page layout from the three pictures (screen first, walkthrough, one screen); "screen first" is built on every module page until you say otherwise | The eight module pages under /platform/ went up Nov 5, 2026 (D1); the layout is one constant in `site/src/pages/platform/[module].astro` | The site thread switches it in one line |
| Decide the volume bands above 100 users (D11): keep the flat per-user price, or 10% off the per-user rate from the 101st user and 20% from the 251st, or quote above 250 | The pricing rule (comparables minus 15%) has no comparable at 250 users in `docs/research/platform-pricing.md`, so the bands would be Claude's arithmetic, not the rule; the calculator and the Solutions examples change with it, and the product thread has to hear first | `config/pricing.yaml`, then the calculator |
| Decide the free-content rule for D6 (a yearly "What insurers ask" report), D9 (a monthly "See the product" session) and V4 (a guide per mapped framework as a web page) | All three are free resources, which the Nov 2 decision ended; each would be in Alimi's own words, never a carrier's or a standard's text | The site thread builds whichever gets a yes |
| Attorney review of the audit wording: "the audit managed by Alimi with an independent CPA firm" (Diamond) and the independence statement on Pricing and Security, mirrored in the MSA outline | Changed Nov 5, 2026 (D10) so Alimi never reads as the auditor; the MSA clause has to say the same | `templates/master-services-agreement-outline.md` |
| Decide how CI spends Actions minutes once the repository is private: every workflow runs twice per pushed commit today (the `push` and `pull_request` triggers), and the Free plan meters 2,000 minutes a month on a private repository | Raised by the product thread Nov 6, 2026 when the site's Lighthouse job started re-measuring pages; running `push` on `main` only would halve the minutes without losing a check, since every branch gets a pull request | The six workflows in `.github/workflows/` |
| Set the `alimi-demo` production branch to `main` and deploy, then "See the product" becomes the main header button (D2) and the module pages' "click through it" links land on the current build | The demo on Netlify still serves the Nov 1 build; the module pages were captured from the B+ shell branch locally | Netlify, then `site/src/components/Header.astro` |
| In Netlify, link the `alimi-demo` site to the GitHub repository (Site configuration, Build and deploy, Continuous deployment, Link repository: `xerches/alimi`, base directory `demo`, production branch `main`), or upload a fresh build of `demo/` with the Netlify CLI as on Nov 1 | The live demo was uploaded directly on Nov 1, 2026 (Netlify records the deploy source as the API, from a `feat/demo` checkout), not built from GitHub, so it stopped there and still shows full policy text, against the no-policy-text rule, while the site links it as "See the product". The Nov 2 fast-forward of `feat/demo` to main (commit `7dc5537`, the founder's choice on the card) could not change it, because no build is connected to the repository. Once linked, every merge to main deploys itself | Netlify settings, founder only |
| Flip the GitHub repository to private (Settings, Danger zone, Change visibility) | Chosen Nov 2, 2026; Claude's GitHub access cannot change repository settings | `decisions.md` row of Nov 2; CLAUDE.md rule "No policy or lesson text in public" |
| Confirm or change the per-user prices: Silver $13, Gold $25, Platinum $38, Diamond $50; the $4 add-on framework; the 10-user minimum; that the 5 and 10 framework discounts count the included framework; the 15% month-to-month premium | All set by the pricing rule, none confirmed in the founder's words yet | `config/pricing.yaml`; everything else follows |
| Decide whether the risk register comes with any included framework that requires a risk assessment (ISO 27001, HIPAA, NIST CSF, SOC 2 in practice), at every tier | A PeerSpot reviewer of Drata: paying for ISO 27001 and finding the risk module an upsell. Today Alimi's risk register is in Gold, so a Silver customer who picks ISO 27001 has a gap; recommendation is to include the register whenever the chosen framework needs it | `config/pricing.yaml` Silver includes; the pricing FAQ |

## Dated

| Date | Item | What to do |
| --- | --- | --- |
| Nov 17, 2026 | Vanta "Trusted Network" webinar (tiered partner incentives, co-selling) | Watch it; compare with Alimi's Partner, Preferred, Premier tiers and the four incentives in `config/pricing.yaml`; adjust before the first MSP conversation |
| Nov 30, 2026 | CISSP exam | November build time is limited; nothing is scheduled to land before Dec 5 |
| Before prompt 18 (after prompt 13, target May 2027) | Review the eight training lessons in `docs/training-modules.md` against what each framework requires (table below) | Decide which lessons are mandatory for which framework, the pass mark, the yearly cycle and the new-hire window; then write the lessons |
| Jan 2027 | Pilots open; first partner conversations (15 planned, 5 of them MSPs on the reseller terms) | Pilot letter and runbook are ready; reseller incentives are proposals until the first conversation |
| Feb 2027, then quarterly | Re-read the Compare page sources | Ratings, counts and reported prices change; the page states the month they were read |
| Before the first paying customer | Re-check the pricing comparables in `docs/research/platform-pricing.md` | AWS Marketplace listings and Vendr data move every quarter |
| After the LLC | Alimi runs its own program in its own platform (the founder's tenant), publishes its own trust page, pursues SOC 2 Type I when revenue covers the audit fee | Decided Nov 2, 2026 from the site scan; prompt 12a seeds the Alimi organization |

## The training review: what the frameworks require

Requirement IDs and our own one-line summaries only (the standards' text is copyrighted). The IDs are from memory and are the first thing to verify in the review; the lesson numbers refer to `docs/training-modules.md`.

| Framework | Requirement ID | What it asks, in our words | Lessons that answer it |
| --- | --- | --- | --- |
| Cyber insurance questionnaire | `training` (controls.yaml) | Security awareness and phishing training for all staff at least yearly | 1 to 7, yearly; phishing practice alongside |
| SOC 2 | CC1.4, CC2.2 | Competent people; security responsibilities communicated internally, with evidence | 1 to 7 plus the role lesson for admins |
| ISO 27001:2022 | 7.3, A.6.3 | Staff aware of the policy and their part in it; an awareness, education and training program | 1 to 7; lesson 4 for data handling |
| ISO 27701 | via ISO 27001 7.3 and A.6.3 | The same, with privacy roles made explicit | 4 |
| ISO 42001 | 7.2, 7.3 | Competence and awareness of people who work with AI systems | 6 |
| HIPAA | 164.308(a)(5) | A security awareness and training program for the workforce, with periodic reminders | 1, 3, 4, 7 |
| PCI DSS 4.0 | 12.6 | A security awareness program, at least yearly, with acknowledgement | 1, 2, 3, 4 |
| GDPR | Art. 39(1)(b) | The data protection officer's tasks include awareness-raising and training of staff who process personal data | 4 |
| CCPA | 1798.130(a)(6) | People who handle consumer requests are informed of the requirements | 4 |
| NIST CSF 2.0 | PR.AT | Awareness and training so personnel can do their security duties | 1 to 7 |
| NIST SP 800-53 | AT-2, AT-3 | Literacy training for everyone; role-based training for privileged roles | 1 to 7; 8 for admins |
| NIST SP 800-171 | 3.2.1, 3.2.2 | Awareness of risks and policies; trained to carry out assigned duties | 1 to 7; 8 |
| CMMC 2.0 | AT.L2-3.2.1, AT.L2-3.2.2 | The same two practices | 1 to 7; 8 |
| CIS Controls v8 | Control 14 | A security awareness and skills training program | 1 to 7 |
| Cyber Essentials | none | No training control; good practice only | none required |
| NIS2 | Art. 21(2)(g) | Basic cyber hygiene practices and cybersecurity training | 1 to 7 |
| FTC Safeguards Rule | 16 CFR 314.4(e) | Security awareness training for personnel, kept current | 1 to 7 |
| 201 CMR 17.00 | 17.03(2)(b)(1) | Ongoing employee training on the information security program | 1 to 7 |
| NYDFS Part 500 | 500.14(a)(3) | Periodic awareness training, at least yearly, including social engineering | 1, 2, 7 |
| SOX ITGC | none explicit | Training is a general control, not a named requirement | none required |
| EU AI Act | Art. 4 | AI literacy for staff who deal with AI systems | 6 |
| NIST AI RMF | GOVERN 2.2 | Personnel receive AI risk management training | 6 |

Review questions: which lessons are mandatory per framework; whether the pass mark stays at four of five; whether a phishing simulation (not built) is needed for the insurer question or an attestation suffices; how new-hire timing (30 days) and the yearly cycle are evidenced in the People module.
