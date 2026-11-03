# Platform pricing: comparables and the rule applied

Date: Nov 2, 2026 (replaces the per-company tiers of Nov 1). Prices are USD, platform only, as published by the vendors (AWS Marketplace listings, pricing pages) or reported by Vendr, Spendflo and the pricing guides listed at the end, checked in September to November 2026. Every vendor leaves the CPA audit fee out, as Alimi does.

The founder's rule: for a price without a direct comparable, take the vendors offering a similar service, average their prices, and cut 5 to 15%. Alimi cuts the full 15% because the buyer is smaller than the comparables' entry customer and the founder's time is the margin.

## The model (founder's direction, Nov 2, 2026)

Every platform price is **per user a month**. A user is a person with an account in the connected tenant; guests, shared mailboxes and service accounts do not count. The minimum subscription is 10 users. Four tiers: Silver, Gold, Platinum, Diamond. **One framework of the customer's choice is included** in every tier; each further framework is an add-on per user a month; with five or more frameworks on the account every added framework is 5% off, with ten or more 10% off, and ten is the most an account holds for now. The Alimi Security Posture Score is in every plan and outside the count. Billing: a 12-month term paid monthly at the list price, or month to month at 15% more; no automatic increase at renewal; price locked for 12 months (24 until Nov 3, 2026, founder's decision).

Why per user: the market prices by headcount band, so a 20-person company pays the band price ($12,000 to $15,000 at Vanta, Drata, Delve or Scrut) and the highest per-head rate of anyone. Per-user pricing gives every company the per-head rate the market reserves for the top of the band, which is where the 15% cut is applied.

## How each number was set

The reference company is 50 people with one framework, the middle of Alimi's 10 to 200 range and the band boundary most vendors use. For each vendor the plan that covers 50 people is divided by 50 users and 12 months. Add-ons and the Platinum and Diamond components are converted at 100 users, because the vendors quote those flat fees to their mid-market customers; at 50 users they would overstate the per-head price. The founder can change any of the five numbers in `config/pricing.yaml`; the site, the templates and the demo follow.

### Silver: entry plans, one framework

| Vendor | Plan | Price a year | Covers | Per user a month |
| --- | --- | --- | --- | --- |
| Vanta | Essentials | $12,000 (top of the $7,500 to $12,000 reported range for under 50 employees) | 50 | $20.00 |
| Drata | Foundation | $15,000 (AWS Marketplace, 1 to 50 FTE) | 50 | $25.00 |
| Secureframe | Fundamentals | $7,500 (one framework; headcount not stated) | 50 | $12.50 |
| Sprinto | Starter | $9,500 (up to 100 employees) | 50 | $15.83 |
| Scytale | platform, one framework | $7,500 | 50 | $12.50 |
| Thoropass | platform | $8,700 | 50 | $14.50 |
| Carbide | Foundation | $7,500 | 50 | $12.50 |
| Iru | Compliance Automation | $15,000 (Core, $9,000, stops at 25 users) | 50 | $25.00 |
| TrustCloud | TrustOps | $5,000 (51 to 500 employees) | 50 | $8.33 |
| Trustero | platform | $5,000 (under 100 employees) | 50 | $8.33 |
| Screenata | AI compliance officer | $5,988 (under 50 employees) | 50 | $9.98 |

Average of 11: **$14.95**. Minus 15%: $12.71. **Silver: $13 per user a month.** A 25-person company pays $3,900 a year, a 50-person company $7,800, a 100-person company $15,600.

Excluded: Delve ($12,000 for 1 to 20) and Scrut ($15,000 for up to 20) publish no plan that covers 50 people; Apptega ($590 to $1,200 a month) publishes no headcount; ComplyJet bundles an audit; SecureSlate's $2,688 covers five users; Comp AI and Oneleet publish no price.

### Gold: multi-framework mid tiers

| Vendor | Plan | Price a year | Per user a month at 50 |
| --- | --- | --- | --- |
| Vanta | Plus (band starts at 50) | $20,000, low end of $20,000 to $45,000 | $33.33 |
| Drata | Advanced (band starts at 51) | $22,000, Vendr 25th percentile | $36.67 |
| Secureframe | Vendr median | $20,000 | $33.33 |
| Carbide | Advanced | $12,500 | $20.83 |
| Carbide | Insights | $22,000 | $36.67 |
| Strike Graph | Scale | $21,500 | $35.83 |
| Scrut | AWS list | $15,000 | $25.00 |
| Trustero | mid-market | $10,000 | $16.67 |
| Iru | Compliance Automation | $15,000 | $25.00 |

Average of 9: **$29.26**. Minus 15%: $24.87. **Gold: $25 per user a month.** Gold is where the market puts vendor risk, the risk register, questionnaires and auditor access, so those are Gold's additions.

### Platinum: Gold plus the add-ons the market sells separately

Converted at 100 users.

| Component | Comparable | A year | Per user a month |
| --- | --- | --- | --- |
| Access reviews | Drata User Access Review, $5,000 to $12,000 | $8,500 | $7.08 |
| Custom integrations and API | Drata custom integrations, $5,000 to $10,000 each | $7,500 | $6.25 |
| Priority support | Drata premium support, 15 to 20% of licence, on Gold | $2,625 (17.5% of $15,000) | $2.19 |

Sum: **$15.52**. Minus 15%: $13.19. **Platinum: $25 + $13 = $38 per user a month.** Unlimited integrations, SSO, custom controls and frameworks and the AI governance module ride along; Vanta prices SCIM, custom frameworks and custom roles as add-ons without publishing figures.

### Diamond: Platinum plus the audit run by Alimi

| Component | Comparable | A year | Per user a month at 100 |
| --- | --- | --- | --- |
| Audit coordination | Vanta Seamless SOC, $10,000 to $25,000 | $17,500 | $14.58 |

Minus 15%: $12.39. **Diamond: $38 + $12 = $50 per user a month.** The dedicated compliance lead's monthly session, the quarterly board report and multi-entity support (a $5,000 to $15,000 "Workspaces" add-on at Drata) are included without a separate charge.

### Add-on frameworks

| Vendor | Reported fee per additional framework a year |
| --- | --- |
| Vanta (UnderDefense) | $5,000 |
| Vanta (Ciphers Security) | $5,000 |
| Vanta (Orbiq, midpoint of $5,000 to $15,000) | $10,000 |
| Drata (UnderDefense, midpoint of $3,000 to $10,000) | $6,500 |
| Drata (Tutorsbot, midpoint of $1,500 to $3,000) | $2,250 |
| Drata (Costbench) | $5,000 |
| Drata (AWS Marketplace, SOC 2 on the 100-FTE platform listing) | $7,500 |

Average of 7: **$5,893** a year; per user a month at 100 users $4.91; minus 15%: $4.17. **$4 per user a month per added framework.** A second framework costs a 25-person company $1,200 a year and a 50-person company $2,400, against $5,000 to $7,500 at the incumbents. With the discounts: $3.80 from the fifth framework, $3.60 from the tenth.

### Month to month and the minimum

The 15% month-to-month premium is the founder's rule applied to the 15 to 25% premium SaaS vendors typically charge for no commitment (open until the founder confirms it). The 10-user minimum keeps the smallest invoice at $130 a month; the comparables have no plan below $2,688 a year.

## What the totals look like

One framework, 12-month term, a year:

| People | Silver | Gold | Platinum | Diamond |
| --- | --- | --- | --- | --- |
| 10 | $1,560 | $3,000 | $4,560 | $6,000 |
| 25 | $3,900 | $7,500 | $11,400 | $15,000 |
| 50 | $7,800 | $15,000 | $22,800 | $30,000 |
| 100 | $15,600 | $30,000 | $45,600 | $60,000 |
| 200 | $31,200 | $60,000 | $91,200 | $120,000 |

Against the market: a 25-person company on Silver pays a third of Vanta Essentials or Drata Foundation; a 50-person company on Gold with two frameworks ($17,400) pays well under Vanta Plus with one add-on framework ($25,000 and up); a 200-person company on Silver ($31,200) sits inside the $25,000 to $45,000 the incumbents quote for that size, which is where the per-user model stops being the cheapest and the tier's content has to carry it. The number to repeat on the site is the published per-user price, not the discount.

## Sources

- Vanta pricing breakdown, UnderDefense (competitor blog, Vendr data): https://underdefense.com/blog/vanta-pricing/
- Vanta pricing 2026, Orbiq (competitor): https://www.orbiqhq.com/comparisons/vanta-pricing
- Vanta AWS Marketplace prices and add-on list, Tutorsbot: https://tutorsbot.com/blog/vanta-pricing-2026-soc-2-cost-per-employee
- Vanta pricing page (plans, no prices): https://www.vanta.com/pricing
- Drata pricing guide, UnderDefense (Vendr data): https://underdefense.com/blog/drata-pricing/
- Drata pricing 2026, Costbench: https://costbench.com/software/compliance-management/drata/
- Drata AWS listings and interviews, SOC2Auditors.org: https://soc2auditors.org/insights/drata-review/
- Drata pricing page (plans, no prices): https://drata.com/pricing
- Vanta vs Drata pricing 2026, Ciphers Security: https://cipherssecurity.com/vanta-vs-drata-pricing-2026/
- SOC 2 software pricing comparison, soc2auditors.org, Sep 30, 2026: https://soc2auditors.org/insights/soc-2-software-pricing-comparison/
- 25 SOC 2 platforms reviewed, soc2auditors.org: https://soc2auditors.org/software/
- Vanta alternatives compared on price, SecureSlate, Oct 13, 2026: https://getsecureslate.com/blog/top-7-affordable-compliance-platforms-for-smart-compliance
- Compliance tools for early-stage startups by year-one cost, StackScout: https://www.stackscout.net/articles/cc_20260927_174714.html
- Vanta and Secureframe on the Vendr marketplace: https://www.vendr.com/marketplace/vanta, https://www.vendr.com/marketplace/secureframe
- Sprinto pricing 2026: https://soc2auditors.org/insights/sprinto-pricing/
- Thoropass pricing guide 2026, UnderDefense: https://underdefense.com/blog/thoropass-pricing-guide/

Re-check before the first paying customer; these listings move every quarter.
