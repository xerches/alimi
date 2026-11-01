---
slug: master-services-agreement-outline
title: Master Services Agreement Outline
---
> **DRAFT. Not legal advice. Review by a Massachusetts attorney before use.**

# Master services agreement: outline

*This is the structure and plain-language intent of each clause, for the attorney who drafts the agreement. Clauses marked [Attorney review] need legal text that alimi does not write itself. Prices and payment terms come from `config/pricing.yaml` through the render script, so the agreement never contradicts the price list.*

**Parties:** {{alimi Entity}} ("alimi") and {{Client}} ("Client"). **Effective date:** {{Effective Date}}.

## 1. Structure

The agreement sets the terms that apply to every piece of work; each piece of work is described in a Statement of Work (SOW) signed by both parties that names the service, scope, deliverables, timeline and fee. If an SOW conflicts with this agreement, the agreement wins unless the SOW says it is changing a named clause on purpose.

## 2. Definitions

Services, Deliverables, Client Data (anything alimi receives from or about the Client's systems, including scan results), Confidential Information, SOW, Fees, Authorized Access (access the Client creates for alimi under an SOW or a pilot authorization letter).

## 3. Services

alimi performs the services in each SOW with reasonable skill and care, using people with suitable experience. alimi may use subcontractors only with the Client's written agreement and stays responsible for them. The Client gets the deliverables named in the SOW; anything else is out of scope and handled by a change order (section 11).

## 4. Client responsibilities

The Client provides timely access, information and decisions; names a contact with authority; confirms it has the right to grant access to any system it points alimi at; keeps its own backups; and remains responsible for operating its systems and for decisions made on alimi's advice. Delays caused by the Client move the timeline and may change the fee under section 11.

## 5. Access and data handling

- Access is read-only unless an SOW says otherwise, created by the Client's administrator with the permissions listed in the SOW, and removed when the work ends.
- alimi does not store Client credentials or tokens; where a hosted service holds a connection, it is encrypted with keys kept outside the database and never written to logs.
- Client Data is processed only to deliver the services, kept on encrypted systems, and deleted or returned within 30 days of the end of the SOW unless the Client asks otherwise or the law requires retention.
- alimi tells the Client within 24 hours of discovering any security incident affecting Client Data. **[Attorney review]** Data protection terms, and whether a separate data processing or business associate agreement is needed for personal or health data.

## 6. Fees and payment

Fees are stated in each SOW and are drawn from alimi's published price list at the time of signing. Payment terms: {{pricing.terms.payment}}. Retainers are billed monthly in advance with a minimum of {{pricing.terms.minimum_monthly_retainer}}. Platform subscriptions are billed yearly in advance. Expenses are charged only when an SOW allows them and at cost. **[Attorney review]** Late payment interest and suspension rights.

## 7. Term and termination

The agreement runs from the effective date until either party ends it with 30 days' written notice; ending the agreement does not end an SOW already in progress unless that SOW is also ended. Either party may end an SOW for the other's material breach that is not fixed within 15 days of notice. On termination the Client pays for work done to the termination date, alimi hands over deliverables for which it has been paid, and section 5's data return and deletion applies. **[Attorney review]** Termination for insolvency and survival clause.

## 8. Confidentiality

Each party keeps the other's Confidential Information secret, uses it only for the agreement, limits it to people who need it, and returns or destroys it on request. Usual exceptions apply (public, already known, independently developed, required by law with notice). The duty lasts three years after the agreement ends, and indefinitely for Client Data and security findings. **[Attorney review]** Wording.

## 9. Intellectual property

alimi owns its tools, scanner, templates, policy library, report formats, training materials and any improvements to them, including improvements made while serving the Client. The Client owns its data and the reports, policies and documents prepared for it, and receives a perpetual licence to use any alimi template material embedded in those deliverables for its internal purposes, not for resale. Neither party uses the other's name or logo publicly without written permission; a case study requires the separate permission form. **[Attorney review]** Licence wording and pre-existing material.

## 10. Warranties and disclaimers

alimi warrants that services are performed with reasonable skill and care and that deliverables will match the SOW for 30 days after delivery; the remedy is re-performance. alimi does not promise that the Client will obtain insurance, pass an audit, meet a legal requirement, or avoid a security incident or fraud; the Client's own decisions and operations determine those outcomes. Scan results describe the configuration on the day of the scan. **[Attorney review]** Disclaimer of implied warranties.

## 11. Changes

Either party may ask for a change to an SOW in writing; alimi responds with the effect on scope, timeline and fee; nothing changes until both sign the change order.

## 12. Limitation of liability

Each party's total liability under the agreement is capped at the fees paid under the relevant SOW in the twelve months before the claim, and neither party is liable for indirect or consequential loss, lost profits, or lost data, except for breach of confidentiality, misuse of Client Data, or liabilities that the law does not allow to be limited. **[Attorney review]** Cap, carve-outs, and consistency with alimi's professional and cyber liability insurance once in place.

## 13. Indemnities

**[Attorney review]** Mutual indemnities for third-party claims arising from each party's breach, and alimi's indemnity for infringement claims about its own materials.

## 14. Insurance

alimi maintains professional (errors and omissions) and cyber liability insurance at the levels stated in the SOW once alimi is an incorporated entity, and provides a certificate on request. *Note for alimi: this clause is a gate; no paid SOW is signed before the policy exists.*

## 15. Independent contractor

alimi is an independent contractor, not an employee, partner or agent of the Client, and controls how the work is done.

## 16. Non-solicitation of staff

Neither party hires away the other's staff involved in the services during the agreement and for six months after, except through general advertising. **[Attorney review]** Enforceability in Massachusetts.

## 17. Governing law and disputes

Massachusetts law. The parties try to resolve disputes between their principals within 30 days, then by mediation in Boston, and only then in the Massachusetts courts. **[Attorney review]** Venue and whether arbitration is preferable.

## 18. Notices, assignment, entire agreement

Notices by email to the named contacts with confirmation. Neither party assigns the agreement without consent, except to a successor of its whole business (and alimi to its own newly formed company). This agreement and its SOWs are the entire agreement; changes must be signed.

## Signatures

| | alimi | {{Client}} |
| --- | --- | --- |
| Name | {{alimi Signatory}} | {{Client Signatory}} |
| Title | | {{Client Title}} |
| Date | | |
