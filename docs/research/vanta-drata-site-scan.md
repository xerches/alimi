# Vanta and Drata, as they sell themselves: site scan of Nov 2, 2026

Read at the founder's request ("review vanta.com and drata.com, scan products, features, and other info that stands out"). Home pages, pricing pages and product pages of both vendors, fetched Nov 2, 2026. Everything below is what the sites say; the review and price research is in `vanta-drata-complaints.md` and `platform-pricing.md`. Key findings for Alimi are at the end, for the founder to accept or reject.

## What the two home pages say

| | Vanta | Drata |
| --- | --- | --- |
| Headline | "Get your compliance together"; "Agentic Trust Platform" | "The Agentic Trust Management Platform"; "Win With Trust" |
| Promise | "SOC 2, ISO 27001, HIPAA, and 35+ frameworks, automated with AI and continuously monitored"; "weeks instead of months" | Autonomous AI agents that automate compliance, manage internal and third-party risk, and prove security posture |
| Scale claims | "Trusted by 16,000 businesses"; "400+ tools"; "35+ frameworks" | "Trusted by 8,500+ global customers"; "hundreds of tools"; about 30 pre-mapped frameworks; "4.8 / 5.0 G2" |
| Modules | Compliance, Continuous GRC, Personnel and Access, Risk Management, Third Party Risk Management, Questionnaire Automation, Trust Center, Streamlined audits, Customer Commitments, AI Governance, API | Enterprise GRC, Compliance Automation, Trust Center (SafeBase), Questionnaire Automation, Third-Party Risk, AI Agent Governance ("New Product") |
| AI | "The Vanta Agent: your 24/7 GRC engineer" drafts policies, completes questionnaires, flags issues; "Vanta AI" surfaces insights | Questionnaire agents, third-party risk agents that assess vendors and chase them, governance agents that discover and police AI agents in the company |
| Outcome stats | "2,000 hrs. saved annually", "20% faster deal cycles", "Automated 93% of questionnaires", not tied to a named customer | "3x productivity", "10x faster trust documentation", "$20M annual revenue accelerated for the average enterprise", no methodology |
| Calls to action | "Get a demo"; "See an interactive demo" in the Platform menu; "Plans" link; no trial | "Get Started", "Get a Demo", "Contact Sales"; no trial; space-mission theme ("[INITIATE LAUNCH]") |
| Segmentation | Startups, Mid-market, Enterprise; Healthcare, Government, Fintech | Startup "Launch Fast", Growth "Accelerate Smoothly", Enterprise "Command at Scale" |
| Own trust signals | SOC 2 Type II, ISO 27001, ISO 42001, GDPR badges; status page; trust center; Forrester Wave Leader Q2 2026 | Trust Center, status pages for Drata and SafeBase, Responsible AI page |
| Channel | "Find a partner" directory, partner and auditor networks, MSP programme; "Vanta Trusted Network" launching Nov 17, 2026 with "tiered incentives" and "co-selling support" | Partners menu; nothing specific on the home page |

## The pricing pages

Neither page shows a price. Both end in "get a demo".

**Vanta** (vanta.com/pricing): Essentials, Plus (labelled "Most popular"), Professional, Enterprise; the button is "Get personalized pricing".

- Essentials: one framework, agentic policy generator, a Vanta AI Agent, automated evidence collection, basic reporting and audit workflows, continuous controls monitoring, Auditor API, Trust Center, access to partners. "For companies who want to stay focused on building."
- Plus: adds automated policy onboarding, questionnaire automation (25 a year) and Access Management.
- Professional: adds 144 questionnaires a year, risk management, Advanced Trust Center, custom monitoring tests, automated access management, six advanced reports, advanced control management, "agentic issue management".
- Enterprise: "fully customizable".
- Add-ons marked in the table: questionnaire response automation, security reviews. Elsewhere reported: additional frameworks about $5,000 a year, VRM, Trust Center Advanced, custom frameworks, custom roles.

**Drata** (drata.com/pricing): two product tracks, each in Foundation, Advanced and Enterprise, plus third-party risk management.

- Compliance Foundation: up to 50 FTEs, one pre-mapped framework chosen from SOC 2, ISO 27001, Cyber Essentials, HIPAA and GDPR only, pre-built integrations, risk management, custom controls, compliance as code, open API. Advanced: any framework, custom connections and tests, custom fields. Enterprise: Risk Management Pro, Compliance as Code Pro, user access review.
- Trust Center Foundation: branded trust center, knowledge base, clickwrap NDA, AI help on up to 100 questionnaires; Advanced adds SCIM, Docusign or Ironclad NDAs, an API and a webhook, Salesforce and HubSpot; Enterprise adds dashboards, unlimited APIs, Dynamics, data warehouse sync.
- Add-ons: additional frameworks, user access review, Risk Management Pro, Workspaces (multi-entity), custom frameworks, agentic TPRM assessments, extra approved domains and questionnaires.

## Key findings for Alimi, for the founder to review

1. **"Agentic" is the word of the year at both.** Vanta sells a "24/7 GRC engineer"; Drata sells agents that assess vendors and police other AI agents. Alimi's assistant is "in preview" and framed as read-only. Decision to make: keep the assistant modest and honest (it suggests, a person accepts) and make the named compliance lead the headline, or add two bounded agent tasks the small company actually wants (draft the questionnaire answer from evidence; draft the policy change summary). Recommendation: the former on the site, the latter in prompt 13's scope.
2. **Drata limits the included framework to five; we allow any of 22.** Operationally we can only deliver the five that are mapped today (insurer, SOC 2, ISO 27001, HIPAA, ISO 42001). Decision: either say "any framework" and schedule the 17 requirement lists before launch (prompt 14), or follow Drata and name the included choices on the pricing page until the rest are mapped. Recommendation: name the choices now, widen as mappings land; the site table already shows which are mapped.
3. **Questionnaires are metered everywhere** (Vanta 25 and 144 a year; Drata 100 on the Trust Center). Gold includes questionnaires with no number. Decision: a published fair-use allowance (for example 24 a year on Gold, 100 on Platinum, unlimited on Diamond) or none. Recommendation: publish an allowance; an unlimited promise becomes an argument later.
4. **Risk management sits in different tiers**: Drata includes it in Foundation, Vanta only in Professional. Alimi has it in Gold. Fine, but a cheaper competitor includes it at entry; consider moving the risk register (not vendors) into Silver. Recommendation: leave it in Gold until a pilot asks.
5. **Both run their own compliance in public**: SOC 2 Type II, ISO 27001, ISO 42001, GDPR badges on Vanta's footer. Alimi should plan to run its own programme in its own platform from day one (dogfooding) and publish the trust page, then pursue SOC 2 Type I once revenue allows the audit fee. Add to the plan after the LLC.
6. **Vanta's "See an interactive demo, no sales call" is the pattern that fits us.** Our demo (Saltmarsh Payroll) exists and is unlisted. Decision: link it from the site as "See the product" once the policy text is trimmed from it (done in this round). Recommendation: yes, with a noindex kept until the hosted app exists.
7. **Unsourced outcome stats** ("2,000 hrs saved", "$20M accelerated") are standard on both sites. Alimi's honest-claims rule forbids them; that is a feature to say out loud on the compare page rather than a gap.
8. **Trust Center as a separate product with its own tiers** (Drata via SafeBase). Alimi bundles the trust page in Silver. Keep; it is a cheap differentiator and the questionnaire allowance above is where the metering should live.
9. **Multi-entity ("Workspaces") is an enterprise add-on at Drata.** Alimi puts it in Diamond and gives it to resellers free in the multi-tenant view. Keep.
10. **Channel is a live front**: Vanta's new Trusted Network (Nov 17, 2026) promises tiered incentives and co-selling. Alimi's reseller page now publishes its incentives; watch the Vanta webinar and adjust before the first MSP conversation.
11. **Both pages segment by stage (startup, growth, enterprise) and industry.** Alimi segments by what the buyer has to prove (insurer, customer, auditor), which is the right axis for 10 to 200 people; no change, but a "Who it is for" block by referral channel (broker's client, CPA's client, MSP's client) would help partners.

## Sources

- https://www.vanta.com/ and https://www.vanta.com/pricing, fetched Nov 2, 2026
- https://drata.com/, https://drata.com/pricing and https://drata.com/product, fetched Nov 2, 2026
- https://www.vanta.com/webinars/introducing-the-vanta-trusted-network (webinar Nov 17, 2026)
- https://help.vanta.com/en/articles/11346128-msp-program-faqs
- https://help.drata.com/en/articles/5329593-frameworks
