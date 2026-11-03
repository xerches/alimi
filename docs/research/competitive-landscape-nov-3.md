# Competitive landscape beyond Vanta and Drata (Nov 3, 2026)

A scan of the compliance automation market made on the night of Nov 2 to 3, 2026, for the marketing lane: 30 searches, about 45 pages read (vendor announcements, release notes, pricing guides, review sites, MSP and insurer-side tools). Figures are as reported by those pages on that night; a competitor's blog is marked as such in the sources and was used for prices and feature lists only. The companion to `vanta-drata-complaints.md` and `vanta-drata-site-scan.md`. Re-run quarterly.

## The short version

1. **Vanta and Drata build for enterprises now.** Vanta passed $300M in annual recurring revenue with 16,000 customers (Apr 2026), was named a Leader in the Forrester GRC Wave (Q2 2026) and spent the year on the Vanta Agent, a Trust Graph, an MCP server, privacy operations and a Risk Graph. Drata redesigned its interface (Feb 2026), shipped agentic third-party risk (Sep 2026) and opened AI agent governance (Aug 2026). None of it addresses a 25-person company at an insurance renewal.
2. **Published prices below Silver exist.** ComplyJet $4,000 a year (one framework, up to 50 people), Screenata $5,988 (under 50), Trustero $5,000 (under 100, framework extra), Scytale $7,500 base, Sprinto $9,500, ControlMap $99 per client tenant a month for MSPs; Comp AI is free to self-host. At 50 people Silver is $7,800: mid-pack, not the cheapest. The claim is the compliance lead and the insurer-first output, not the lowest price.
3. **Software plus a person is the challengers' shape.** Oneleet bundles a pentest and a vCISO, Delve the audit and a pentest, Scytale a named expert, Thoropass employs its auditors, Comp AI quotes audit and pentest in one price. Alimi's compliance lead is in this lane; the missing piece the others sell is a pentest.
4. **Free tools cover part of the scanner's job.** Coalition Control (free to policyholders) watches Microsoft and Google sign-ins and rates cyber health; ControlMap and CloudCapsule have free tiers; CIPP is open source; Syncro and CyberDrain give MSPs a free Microsoft tenant assessment. The scan is not the product; the controls, evidence, policies, report and person around it are.
5. **The complaints generalize.** Opaque pricing, support thinning after year one, endpoint agents that stop reporting, too many clicks and renewals rising 20 to 40% appear in reviews of Sprinto, Secureframe, Scrut, Thoropass, Hyperproof and Drata alike. The Compare page's arguments hold against the field.

## The field

Prices are a year, as published on AWS Marketplace or a vendor page, or as reported by Vendr and pricing guides; "quote" means no public number.

| Product | Group | Built for | Price signal | What stands out | UI and reviews |
| --- | --- | --- | --- | --- | --- |
| Vanta | Incumbent | Startups to enterprises; 16,000 customers | Essentials $14,000 (1 to 20 people, AWS), Plus $21,500, Professional $23,000; Vendr median $20,000; add-ons: Trust Center $6,000, Questionnaire Automation $10,000, TPRM $13,600, Customer Trust Management $22,250 | 400 integrations claimed, AI Agent 2.0, Trust Graph, Vanta Privacy, MCP server; Forrester GRC Leader | Clean layout per reviewers; Capterra 4.2, G2 4.5 |
| Drata | Incumbent | Companies with an internal owner; 8,500 organizations | Foundation $15,000 (1 to 50 FTE, AWS); about $25,000 at 100 FTE plus $7,500 SOC 2; Vendr median $25,000; renewals reported up 20 to 40% | Deep tests, agentic TPRM (Sep 2026), AI agent governance (Aug 2026), hosted MCP server, SafeBase trust center | "New Drata Experience" (Feb 2026) got "more clicks" from some users; G2 4.7 |
| Secureframe | Incumbent | Teams that want managed support | From $7,500; Vendr median $20,000 | Comply AI suite (remediation, policies, risk, evidence validation); 2026 updates incremental | Guided setup praised; Reddit threads mostly about price; G2 4.7 |
| Sprinto | Mid-market | SaaS under 100 people | $9,500 list ($7,500 platform plus $2,000 framework) | Fast onboarding, 25+ automated frameworks, Dr. Sprinto agent | G2 4.7 (1,685), ease of use 9.2; agent flaky, support slows after year one, too many clicks, Microsoft security gaps |
| Scrut | Mid-market | Cloud-native SaaS, several frameworks | About $15,000 (AWS); quote | Risk-first, Scrut Teammates agents, white-label trust vault | G2 4.9 (1,298), Fall 2026 Best Usability and Easiest Setup; "overwhelming without support" |
| Thoropass | Audit-included | Platform and auditor from one vendor | Quote; readiness $20,000 to $37,000 by its own estimate | In-house auditors inside the platform, 30+ frameworks | Interface "cluttered"; G2 4.7 (551) |
| Scytale | Service-led | 20 to 75 people without compliance staff | $7,500 base, $2,100 per added framework, $36,000 virtual compliance (AWS) | A named compliance expert per customer | Clean; "product thinner than the service" |
| Hyperproof | Upper mid-market | Four or more frameworks with an owner | $12,000 to $41,000 reported | 118 frameworks, four AI agents | Clean but slow at scale; G2 4.5 |
| Anecdotes | Enterprise | Engineering-led teams | Quote | Deep technical evidence collection | Steep learning curve |
| Trustero | Small | Multi-framework teams and MSSPs | $5,000 under 100 people; SOC 2 framework $15,000 extra (AWS) | Questionnaire Copilot, auditor workspace | G2 4.9 on 29 reviews |
| TrustCloud | Small | Startups | $5,000 (51 to 500 people) | Free tier history, questionnaire AI | Few recent reviews |
| Oneleet | Challenger, security-first | Security-conscious startups; 1,000+ customers claimed | Quote, one all-inclusive price, "no add-on fees" | Human-led pentest and a vCISO bundled; 27 integrations | G2 4.9 on about 140 reviews |
| Delve | Challenger, AI-native | Fast-moving startups | $12,000 (1 to 20 people, AWS); about $22,000 with audit | AI agents, SAST on pull requests, computer-use evidence capture; $32M Series A | Mar 2026 investigation into boilerplate SOC 2 reports; removed from the YC directory Apr 2026 |
| Comp AI | Challenger, open source | Engineering-led, budget-conscious teams | Free to self-host (AGPL, github.com/trycompai/comp); managed from about $199 a month reported | 99% open source, device agent, AI policy editor, audit and pentest in the quote | Young; few reviews |
| ComplyJet | Challenger, published price | SaaS startups wanting one framework cheaply | Core $4,000 (one framework, up to 50 people), Plus $6,400 | Slack support, 350+ integrations claimed, 40 audit firms | Writes most competitor reviews found in this scan |
| Screenata | Challenger, published price | Small SaaS teams under 50 people | $5,988 per framework | 650+ checks across 30 providers | 2 to 10 employees; almost no reviews |
| Cynomi | vCISO platform for MSPs | MSPs and MSSPs | Per partner account, not per client | AI coworkers, scheduled scans (Jun 2026), 40+ frameworks; a partner serves 10 to 12 clients | Channel press positive |
| ScalePad ControlMap | MSP | MSPs, US defense clients | $0, $99 Essentials, $299 Pro per client tenant a month | 63 frameworks, client trust portals; the only per-client price published | Fits ScalePad users most |
| Compliance Scorecard | MSP | MSPs delivering governance | Quote, per client | FTC Safeguards, CMMC, CIS; PSA integrations | Governance-led, little automation |
| Apptega | MSP and SMB | MSPs managing hundreds of clients | Quote; 14-day trial | Branded client environments | US-centric |
| Kaseya Compliance Manager GRC | MSP | Kaseya MSPs | Licensed per site | Microsoft cloud scan, brandable portal, training | Older product (2022) |
| Coalition Control | Insurer-side | Coalition policyholders | Free with the policy | Sign-in monitoring on Microsoft and Google, cyber health rating, vendor monitoring | Sets the bar for "free with insurance" |

Also seen: Cyber Verify (MSPAlliance), Enactia (flat fee per client, EU frameworks), the Microsoft 365 posture tools for MSPs (Octiga, Augmentt, CloudCapsule with a free Analyze tier under 1,000 users and $1 a user a month to manage, Optimize365 from $2 a user a month, Inforcer, CoreView at $20,000 and up, the open-source CIPP), and OneTrust, AuditBoard, LogicGate and Diligent at the enterprise end.

## Features others have that Alimi does not

| Feature | Who has it | Matters for the 10 to 500 buyer? |
| --- | --- | --- |
| Audit included in the price | Thoropass, Delve, Oneleet, Comp AI, Scytale | Yes; Diamond has it. Open question: a CPA-partnered audit coordination add-on for Gold with a published fee |
| Penetration test bundled | Oneleet, Delve, Comp AI | Yes for B2B founders; a fixed-fee service after the LLC, not a tier feature |
| Named expert or vCISO | Oneleet, Scytale, Cynomi, Alimi | Alimi's strongest point; say "a person, not an agent" louder |
| AI agents doing the work | Vanta, Drata, Sprinto, Scrut, Hyperproof, Delve | Partly; users rate them flaky. Scope the assistant to three jobs: explain a failed test, draft a questionnaire answer, draft a policy |
| MCP server for Claude, ChatGPT, Cursor | Vanta (May 2026), Drata (Sep 2026) | Year two; cheap on FastAPI |
| AI agent governance | Drata (Aug 2026), Vanta | Yes; the Platinum AI governance module. Add AIUC-1 to the catalog when it ships |
| Privacy operations (ROPA, DPIA) | Vanta Privacy, OneTrust, Drata | Only once GDPR is mapped |
| Device agent | Vanta, Drata, Secureframe, Comp AI | Most-complained-about feature; Alimi reads Intune and Google endpoint management instead. Say so on Integrations |
| Customer trust management | Vanta, Drata SafeBase, Scrut, Sprinto | Gold has the trust page; per-customer commitments is enterprise |
| Risk graph with AI treatments | Vanta, Hyperproof | Gold's risk register covers it |
| Access reviews from HR and chat tools | Vanta, Drata, Secureframe | Platinum has access reviews; integration count is the limit |
| Per-client pricing for MSPs | ControlMap, Enactia, Cynomi | Yes; show the per-client arithmetic on For resellers |
| Free Microsoft 365 posture scan | Coalition Control, Syncro and CyberDrain Snapshot, CloudCapsule, CIPP | Threat to the paid assessment; the answer is 23 checks behind 40 controls and the person who reads them |
| "Audit in days" claims | Delve, Oneleet, Sprinto | "Insurance-ready in 30 days" is the honest version |
| Open source | Comp AI, CIPP | Not a buyer need at this size; Comp AI managed ($199 a month) is the competitor |
| Continuous insurer scoring | Coalition, At-Bay, Cowbell, Resilience | The market moving toward Alimi's position; partner with brokers, do not compete with carriers |

Site changes from this table: the no-agent sentence on Integrations, the per-client price on For resellers, "a person, not an agent" on Home and Compare. The rest are product decisions.

## What the better interfaces do

- Scrut: G2 Fall 2026 Best Usability and Easiest Setup; risk-first home; still "overwhelming without support".
- Sprinto: ease of use 9.2 from a guided onboarding flow; complaints about clicks and depth.
- Vanta: clean; since Aug 2026 a SOC 2 Guide home page for Essentials (a first-run checklist), the closest thing to Alimi's planned setup checklist.
- Drata: Feb 2026 redesign answered with "more clicks" and "relearning". Do not move the shell once customers live in it.
- Thoropass cluttered; Hyperproof clean but slow at scale; Delve chat-first.
- Nobody is praised for explaining a failed test; Drata's user interviews say failed tests are hard to trace, false positives pile up, integrations stop syncing silently.

For the B+ shell: keep the rail and the monthly Home with two scores; make the first-run checklist the first screen; every failed test shows cause, evidence, owner and a one-click task; integration health (last sync, errors) on Home; count clicks in review. For the site: show the failed-test screen and the integration health strip on Platform once built.

## Review themes across the field

| Theme | Where | What Alimi has | Gap |
| --- | --- | --- | --- |
| Opaque pricing, renewal jumps | Drata +20 to 40%; Sprinto, Secureframe, Scrut | Published price, no automatic increase | None; Compare can say "versus the field" |
| Support thins after year one | Sprinto, Secureframe, Hyperproof | Compliance lead and a call in every tier | Say "every tier, every year" |
| Endpoint agent | Sprinto, Vanta, Drata, Secureframe, Comp AI | No agent | One sentence on Integrations |
| Clicks and relearning | Drata, Sprinto | Shell not built | Design rule |
| Noisy tests, hard to trace | Drata, Vanta, Sprinto | False-positive notes, data-quality page (12b, 12c) | Name both on Platform once built |
| Silent sync failures | Drata | Data-quality page | Same |
| Flaky agents | Sprinto, Delve | Scoped assistant | "A person, not an agent" |
| Audit quality doubts (new) | Delve boilerplate SOC 2 reports | Diamond "audit run by Alimi" | Wording risk: say "coordinated with an independent CPA firm, named in the contract" (attorney review) |
| Product thinner than service (new) | Scytale, Thoropass | Platform and person | Keep the demo in step with the services |
| Microsoft security gaps (new) | Sprinto | 12 Microsoft 365 checks first | Say "Microsoft 365 first" |

## Where the field is going, 2026 to 2027

- Agents in every product (Vanta Agent 2.0, Agent for Risk Jun 2026, personnel agent tools Aug 2026; Drata agentic TPRM and AI questionnaire assistance Sep 2026; Sprinto, Scrut, Hyperproof, Secureframe). episki's State of GRC 2026: agents "in marketing decks more than production".
- AI governance as a framework family: Drata AI agent governance (Aug 2026) and AIUC-1 (Oct 2026); ISO 42001, EU AI Act, NIST AI RMF already in Alimi's catalog; add AIUC-1 when the module ships.
- Compliance data in the customer's own AI assistant via MCP (Vanta May 2026, Drata Sep 2026): year two for Alimi.
- Privacy operations folded in (Vanta Privacy, May 2026): relevant once GDPR is mapped.
- Regulation keeps adding frameworks: Drata EU CRA support (Sep 2026); NIS2 and DORA in every European list; CMMC Phase 2 suspended July 2026 (playbook research), defense demand uncertain.
- Incumbents move up: Vanta Organizations Center, Customer Commitments, Forrester Leader; Drata enterprise TPRM. The under-50 segment is left to challengers and MSP tools.
- Insurers run their own monitoring: Coalition Control free with the policy; At-Bay, Cowbell, Resilience bundle services. Expect evidence by feed within two years; the insurer report should be forwardable today and API-readable later.
- MSP platforms get AI: Cynomi AI coworkers (Jun 2026); ControlMap per-client pricing; Kaseya bundles. Resellers compare Alimi's wholesale price to these.
- Vanta's stated roadmap (VantaCon UK, May 2026): DocuSign and Google Drive contract sync (Q2), access-review integrations for Zoom, Intercom, Personio; Trust Graph claiming 400 integrations and 1,400 tests an hour.

Bets for 2027: insurer-first output, a person in every tier, Microsoft 365 and Google Workspace depth without an agent. Do not chase agents or MCP in year one.

## Price and positioning

| Size | Alimi Silver | Alimi Gold | Published challengers | Incumbents |
| --- | --- | --- | --- | --- |
| 25 people | $3,900 | $7,500 | ComplyJet $4,000; Trustero $5,000 + $15,000 SOC 2; Screenata $5,988; Scytale $7,500; Sprinto $9,500; Delve $12,000 | Vanta Essentials $14,000; Drata Foundation $15,000; Secureframe from $7,500 |
| 50 people | $7,800 | $15,000 | ComplyJet $4,000; Screenata $5,988; Scytale $7,500; Sprinto $9,500 | Drata Foundation $15,000; Vanta Plus $21,500 |
| MSP client, a month | $325 at 25 users before the reseller discount ($292.50 at Partner) | | ControlMap $99 Essentials, $299 Pro per client tenant | |

1. At 25 people Silver is the lowest full-platform price in the field that includes a person.
2. At 50 people Silver is mid-pack and Gold equals Drata Foundation: "published, not the cheapest". Never claim lowest price.
3. Per-user pricing turns against Alimi above about 100 users (Silver at 200 is $31,200, above Vanta Professional $23,000 and Drata at 100 FTE $25,000). Recommendation: volume bands stepping the rate down at 100 and 250 users, computed with the same rule at those sizes; a pricing decision for the founder, announced to the product thread before the calculator changes. No 200-person comparison on the site until then.
4. For resellers the comparison is ControlMap's $99: show that the Alimi price includes policies, training, the report and a compliance lead.
5. Audit-included pricing is the challengers' hook; a published audit coordination add-on for Gold would meet it without moving the tiers. Founder decision.

Positioning holds: "a person, not an agent", "the price is the price", insurer-first. Nobody else leads with the cyber insurance questionnaire except the carriers' free tools, so partner with brokers rather than compete with carriers.

## Next steps for marketing (Nov 3, 2026)

This week: merge #18, #21, #24 and the audit-fix PR in order; one copy PR (no-agent sentence, per-client arithmetic, "versus the field" paragraph, "Microsoft 365 first"); the Resources page accessibility fix; deploy when Netlify credits return.

Needs the founder: Integrations to 15 tiles with the six new connectors marked planned; the insurer-first landing page and search cluster, then prompt 17; For resellers as the MSP front door; audit wording on Pricing; volume bands above 100 users; the employer outside-work check before any named post; the Nov 17 Vanta Trusted Network webinar.

This month: partner email and 10-minute talk; pilot invitations for January 2027; re-run this scan quarterly.

## Sources

Read Nov 3, 2026, 02:00 to 04:00 UTC. Competitor blogs marked (competitor).

- Vanta: vanta.com/resources/vanta-crosses-300m-in-arr-as-growth-accelerates (Apr 29, 2026); vanta.com/resources/introducing-vantas-agentic-trust-platform (Nov 18, 2025); vanta.com/resources/vantacon-uk-2026-recap (May 2026); businesswire.com/news/home/20260602347223/en/ (Agent for Risk, Jun 2, 2026); releasebot.io/updates/vanta; research.oz.spotlightar.com (Forrester GRC Wave Q2 2026 leaders).
- Drata: drata.com/blog/product-updates-2026-02; drata.com/about/news/drata-extends-trust-management-platform (Sep 2026); releasebot.io/updates/drata; peerspot.com/products/comparisons/drata_vs_vanta.
- Secureframe: secureframe.com/newsroom/secureframe-new-suite-of-ai-capabilities (May 2024); support.secureframe.com/en/articles/15111813-2026-product-feature-updates.
- Pricing and reviews: soc2auditors.org/insights/drata-review/, /insights/vanta-pricing/ (updated Oct 15, 2026), /software/oneleet/, /software/trustero/, /software/screenata/; soc2-auditors.com/insights/delve-review; complyjet.com/blog (competitor): thoropass-review, scrut-automation-review, scytale-review, hyperproof-reviews, drata-pricing-plans, comp-ai-pricing, delve-pricing; soc2compliancetools.com/solutions/complyjet; secureleap.tech (Sprinto review); sprinto.com/blog/oneleet-vs-vanta-vs-delve/ (competitor); oneleet.com/oneleet-vs-drata (competitor); scrut.io/post/scrut-automation-g2-fall-2026-results (vendor); helpnetsecurity.com/2026/04/07/comp-ai-open-source-compliance-platform/; redditmaster.com/reddit-intelligence/best/soc-2-compliance-automation.
- Market comparisons: securityboulevard.com (compliance automation platforms compared 2026, Jun 2026); guptadeepak.com/tools/top-10-compliance-automation-platforms-2026/ and /tools/top-5-cyber-insurance-platforms-2026/; consilien.com/news/best-compliance-automation-platforms-2026; grsee.com platform comparison; softwaretestinghelp.com compliance software list; episki.com/blog/state-of-grc-2026 (Jan 21, 2026).
- MSP and insurer side: channelinsider.com (Cynomi AI integrations, Jun 24, 2026); channelfutures.com (Kaseya Compliance Manager GRC); enactia.com/vanta-alternatives-for-msps/ (competitor); cyberverify.com/best-compliance-software-for-msps; ScalePad ControlMap pricing page; coalitioninc.com/control.

Two pages failed to load (the Syncro and CyberDrain Snapshot announcement on vmblog; a CyberArrow trends post); their search summaries were used and nothing rests on them alone.
