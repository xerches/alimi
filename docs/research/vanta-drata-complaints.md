# What Vanta and Drata customers complain about

Read Nov 2, 2026 at the founder's request: "rescan any bad reviews (less than 4 star reviews out of 5), scan for what feedback was given to improve product, and try to implement or highlight these complaints on a page comparing us to Drata and Vanta". This is the material behind `/compare` on the site. Everything is as reported by the source named; where a source is a competitor's blog that is said. Ratings are as read on Nov 2, 2026.

## The sources and their shape

| Source | Vanta | Drata |
| --- | --- | --- |
| G2 | 4.6 of 5 (178 reviews cited by Orbiq) | 4.7 of 5, 1,399 reviews; 87% five stars, "virtually no 1 to 2 star reviews" |
| Capterra | 4.2 of 5, 33 reviews; six at 1 star, one at 3 | 4.8 of 5, 6 reviews; none below 4 |
| Trustpilot | 3.1 of 5, 33 reviews; eleven 1-star reviews on the first page, two of them misattributed to other companies named Vanta | not listed |
| Gartner Peer Insights | 4.4 | 4.1 of 5, 17 ratings |
| TrustRadius | listed; reviews did not load | not covered |
| Other | ComplyJet, Orbiq, UnderDefense, Tutorsbot pricing and review summaries (competitors) | SOC2Auditors.org: 23 user interviews, five scoring below 4; Sprinto review (competitor); Reddit r/soc2 and r/cybersecurity threads; Hacker News |

Limits: G2 and Capterra show few low ratings for either product, so the sub-four material is thin and skews to billing disputes (Trustpilot) and to interview sets a third party ran. Several sources are competitors. The comparison page therefore says "reviewers report" and gives ranges, never a single number as fact.

## Themes, with what was said

### 1. Renewal price jumps and escalators (both)

- Vanta, UnderDefense: year-one discounts of 20 to 40% (up to 70%) "not locked in"; renewal quotes "30 to 50% higher than Year 1"; 5 to 10% annual escalators; a reported year-two invoice rising from $8,000 to $18,000; 60 to 90 days' notice or the contract auto-renews.
- Vanta, Orbiq: "Year 2 Cliff", renewal quotes up 40 to 100%; 60-day cancellation notice.
- Drata, UnderDefense: standard escalator about 8%, negotiable to about 3%; "base contracts rising from $7,500 to $20,000 within two cycles"; 20 to 40% year-two increases reported by reviewers.
- Drata, Costbench: renewal increases 15 to 30%; renews unless cancelled 30 to 60 days before term end (the page contradicts itself on auto-renewal).

### 2. Cancellation, auto-renewal and refund disputes (Vanta, the loudest theme)

- Capterra 1-star reviews: a CEO of a 2 to 10 person firm, "rigid contract with no early exit, high pricing"; an operations director, a cancellation after a government contract ended took months; a CEO "forced to pay nearly $18,000 over a two-year contract despite not using the product"; a CFOO auto-charged a $15,600 invoice "without clear auto-pay notice; refund refused"; a CEO "charged for a renewal without permission; documents went missing".
- Trustpilot 1-star reviews (2026): signed up for ISO 27001, never used the platform, early termination refused "even after escalation to the CEO"; a roughly $14,000 switch described as a mistake with a salesperson who stopped responding after the sale and a refused early-termination proposal; $8,250 paid for an auto-renewed year with access then cut off over late payment; a customer success manager believed to work for a competitor.

### 3. Add-on fees ("nickel and diming") (both)

- Vanta: additional frameworks about $5,000 a year each; Trust Center and VRM together about $17,000 a year, VRM alone $11,200 (UnderDefense); TPRM $13,600, questionnaire automation $10,000 to $16,000, Trust Center Advanced $10,000 on AWS Marketplace (Tutorsbot); "Users say Vanta charges extra for features that should be standard" (The Sector Post summary of G2 themes).
- Drata: additional frameworks $3,000 to $10,000; User Access Review $5,000 to $12,000; Workspaces $5,000 to $15,000; custom integrations $5,000 to $10,000; implementation $5,000 to $25,000 (UnderDefense).

### 4. Support and account management after the sale (Vanta mostly)

- Trustpilot: "no onboarding, training, or follow-up after the sale"; "generic and slow" support from a multi-year customer; a sales rep ending a call when the camera stayed off; aggressive outreach to a personal phone after hours.
- Gartner (via ComplyJet): users cite limited customer support and cost as reasons to switch.
- Capterra 4-star reviews: "little support once users go beyond standard setups"; "still had to manage the auditor directly".
- Drata, Gartner (June 2026): far more internal security, IT, policy and engineering effort than expected.

### 5. Noisy alerts and false positives (both)

- Vanta, Capterra: "too many notifications" (QA engineer, 51 to 200 people); "alarm fatigue from frequent failing-test notifications" (software engineer); summaries name "too noisy" monitoring and "alerts for minor issues".
- Drata, SOC2Auditors interviews: power user, 2 of 5, "too many false positives, intermittent integrations and workflow quirks for what we're paying", "automation created investigation work"; security lead, "some tests produce noise that must be investigated manually"; DevOps engineer, finding the cloud resource behind a failed test "more painful than it should be"; IT director wanted clearer explanations when tests fail; GRC consultant, "a green dashboard does not mean a control is well designed".
- Drata, G2 (4.5 stars): "when a control is marked as 'not ready' it's not always clear why".

### 6. Integrations that break or go shallow (both)

- Drata, SOC2Auditors interviews: healthcare security officer, 3.5 of 5, "when one quietly stops syncing, confidence in the dashboard drops fast"; Reddit r/cybersecurity (Aug 2024), connector and multi-framework frustrations.
- Drata, G2: "certain integrations or customizations require more manual effort"; "limitations on custom integration"; no on-premise support.
- Vanta, Capterra and G2: integrations "not quite up to the standard as the rest"; repeated requests for more integrations (provisioning, vendor management, MDM, an admin API); sync issues in complex environments (G2 and Reddit, via ComplyJet).

### 7. The endpoint agent (Vanta mostly)

- Capterra: "agent required on every computer, which is difficult for remote teams" (managing director); objects to the agent not being open source (software engineer, 3 stars).
- The Sector Post summary: engineering teams resist installing it ("Culture Shock"); G2 users report high CPU usage on older machines; staff worry it monitors them.
- Drata documentation: agent data overrides the MDM when both report a device; contractor and BYOD devices need a manual path (SOC2Auditors).

### 8. Generic templates and a product that assumes an expert (both)

- Vanta, Capterra: "policy templates need updating; no vendor security questionnaire feature" (CEO, 4 stars); "policy generator loses automation once edited offline" (chief compliance officer); "steep learning curve"; "initial setup feels overwhelming"; UI "dated", "rough and unintuitive".
- Drata interviews: founder "underestimated the judgment and remediation still needed"; first-time compliance manager, compliance looks "deceptively simple during a demo", someone still must handle scope and fixes; security analyst, Drata "does not resolve who owns approval decisions".
- Drata, Reddit r/soc2 (2026): a user who moved to Drata found the new interface worse and said earlier contracts included more; interviewees: familiar workflows "now take more clicks".

### 9. Smaller themes

- Access reviews show access as of the review day, not the period start, unless a CSV is exported at period start; no remediation inside (Drata docs).
- No HITRUST out of the box (Drata, Capterra 5-star con); no quality management system for ISO 9001 (Drata, G2).
- Daily tests run at a fixed hour, so a fix shows as passing only after a rerun or the next run (Drata docs).
- An evidence upload silently saving one of two files (Vanta, Capterra).
- Vanta's May 2025 incident: a faulty deploy removed a tenant-isolation filter for under a day; usernames, roles and MFA metadata visible across accounts for fewer than 4% of customers; no passwords or tokens (ComplyJet).

## Second pass, Nov 2, 2026 (late evening)

The founder asked whether any other low-rated reviews were worth building for. Six more sources were read; the Reddit and G2 pages themselves do not load from here, so G2 material comes syndicated through AWS Marketplace and two competitor digests.

| Source | What it is | Rating |
| --- | --- | --- |
| SoftwareAdvice, Vanta | Same 33 reviews as Capterra (shared database); six below four stars | 4.2 of 5 |
| AWS Marketplace, Vanta | G2 reviews syndicated, September 2026 pages, cons only | 4.6 of 5, 2,630 ratings |
| Trustpilot, Drata | Four reviews, all one star, profile unclaimed | 2.6 of 5 |
| PeerSpot, Drata | Ten reviews from security and audit staff | 4.0 of 5 |
| 6clicks blog | A competitor's digest of Vanta complaints from G2, Capterra, Reddit and AWS Marketplace | competitor |
| Cyber Sierra blog | A competitor's digest of Vanta and Drata complaints from Reddit and interviews | competitor |

New themes, beyond the nine above:

- **The bundled audit and auditor independence.** Trustpilot, Drata: "the bundled audit went horrible", switching auditors took "many weeks", "we had lost a deal in the process"; "overselling the offering and delivering only the automated semi-ready product"; "AVOID IF YOU ARE A SMALL BUSINESS". Capterra, Vanta: "we still had to handle auditor ourselves". Reddit r/soc2 (via 6clicks): allegations that auditor partnerships favour volume; reported as allegations.
- **A dashboard that does not say what to do today.** G2 via AWS Marketplace, Vanta: "unclear which controls need immediate attention; a filter for mandatory controls would help"; stale test statuses; "change tracking and rollback need improvement"; the AI "returns a blank response for 'no evidence found' and it is unclear whether it searched"; questionnaire automation "gives poor answers"; vendor assessments where it is "hard to tell which version is old and which is new". PeerSpot, Drata: "compliance readiness indicators can be misleading".
- **Built for a company that already has a security person.** SoftwareAdvice and Capterra, Vanta, 2 to 50 people: "seems built for enterprise clients", "the pricing was too high and we still had to handle auditor ourselves", wants "more automation... help with remediation, since the company has no dedicated IT team". PeerSpot, Drata: "you'll need some specific knowledge if you're a security policy manager"; "the industry tends to market these tools as security experts". Trustpilot, Drata: a contract "that will add no real value" for a small startup.
- **Hidden modules at the sale.** G2 via 6clicks, Vanta: "You need to buy modules, and this thing [is] not mentioned during initial marketing and pre-sale phase."
- **A framework that needs a module the tier lacks.** PeerSpot, Drata: "if you're paying for a subscription to ISO 27001, you must undergo a risk assessment", so the risk module should be included. Relevant to Alimi's Silver tier, where the risk register is not included; see `docs/agenda.md`.
- **Smaller:** marketing email after no sign-up (Trustpilot, Drata); auditors losing access to the audit hub mid-engagement (PeerSpot, Drata); cannot open the app in several tabs (PeerSpot, Drata); API documentation thin (PeerSpot, Drata); the device scanner over-flags small developer tools and needs manual approval to quiet (G2, Vanta); performance drops when an integration ingests a lot of data (G2, Vanta).

The first three became Compare page themes 9 to 11 on Nov 2, 2026; the hidden-modules quote joined theme 3; the ISO 27001 risk-module point is an open decision for the founder.

## What Alimi does with each, and where it already is

| Theme | Alimi's answer | Where |
| --- | --- | --- |
| Renewal jumps | Published per-user price, no automatic increase, 12-month lock | `config/pricing.yaml`, site pricing page |
| Cancellation disputes | 12-month term paid monthly or month to month; renewal is a conversation | pricing.yaml billing, MSA outline |
| Add-on fees | Vendors, risks, questionnaires, trust page inside Gold; frameworks at $4 per user with discounts | pricing.yaml, platform page |
| Post-sale support | Named compliance lead in every tier; founder on support | pricing.yaml included_everywhere |
| Noisy tests | Raw evidence and rule on every test; false-positive note with reason in the audit log; insurer-relevant checks only | prompts 12a and 12b |
| Silent integrations | Two integrations done deeply; data-quality page; unreadable data is an error naming the permission, never a pass | scanner (PR #12), prompt 12c |
| Agent | No agent; device compliance from Intune or Google endpoint management | platform page; prompt 12a Integration model |
| Templates and expertise | 23 policies tailored in a workshop; versions and sign-offs in the platform; the compliance lead makes scope calls | policies, services, prompt 13 |
| Access reviews as of a date | Period-start snapshot kept with the review | prompt 12b, to add |
| Tenant isolation | Row-level security on every customer table, tested | prompt 12a |
| Bundled audit | The CPA firm is the customer's choice and paid by the customer; Alimi takes no fee from any auditor; the export pack goes to any firm; Diamond coordinates, the firm stays independent | pricing.yaml Diamond, compare page, MSA outline (to add) |
| Unclear priorities | Home screen ordered by insurer impact with the top five fixes and 30-day due list; two scores; computed statuses; on-demand re-run after a fix; version history on policies and controls; the assistant says what it searched | prompts 12b, 12c, 13 |
| Built for experts | Named compliance lead in every tier; plain-English fix on every failing check; fixed-fee remediation services | pricing.yaml included_everywhere and services |
| Hidden modules | The whole price list, add-ons included, on the pricing page; questionnaire allowances published | pricing page, Nov 2 |
| Framework needs a module the tier lacks | Open: include the risk register with any included framework that requires a risk assessment | docs/agenda.md |
| Auditor access | Auditor and broker access as time-limited links with an audit log | prompt 12b, to add |
| Several tabs | Server-rendered pages, every URL stands alone, no client state | prompt 12a (FastAPI and HTMX) |

## Sources

- https://www.capterra.com/p/211459/Vanta/reviews/
- https://ca.trustpilot.com/review/vanta.com
- https://www.complyjet.com/blog/vanta-reviews (competitor)
- https://www.thesectorpost.com/compliance/soc2/vanta-review
- https://www.trustradius.com/products/vanta/reviews (reviews did not load)
- https://underdefense.com/blog/vanta-pricing/ (competitor, Vendr data)
- https://www.orbiqhq.com/comparisons/vanta-pricing (competitor)
- https://tutorsbot.com/blog/vanta-pricing-2026-soc-2-cost-per-employee
- https://soc2auditors.org/insights/drata-review/
- https://www.g2.com/products/drata/reviews?qs=pros-and-cons
- https://www.capterra.com/p/218441/Drata/
- https://sprinto.com/blog/honest-drata-review/ (competitor)
- https://underdefense.com/blog/drata-pricing/ (competitor, Vendr data)
- https://costbench.com/software/compliance-management/drata/
- https://cipherssecurity.com/vanta-vs-drata-pricing-2026/
- https://www.softwareadvice.com/audit/vanta-profile/reviews/ (second pass)
- https://aws.amazon.com/marketplace/reviews/reviews-list/prodview-5ophamrbfxt44?page=3 (G2 reviews syndicated; second pass)
- https://nz.trustpilot.com/review/drata.com (second pass)
- https://peerspot.com/products/drata-pros-and-cons (second pass)
- https://www.6clicks.com/resources/blog/understanding-vantas-limitations-insights-from-real-user-experiences (competitor; second pass)
- https://cybersierra.co/blog/vanta-drata-review/ (competitor; second pass)
