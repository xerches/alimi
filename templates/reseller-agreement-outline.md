---
slug: reseller-agreement-outline
title: Reseller Agreement Outline
---
> **DRAFT. Not legal advice. Review by a Massachusetts attorney before use.**

# Reseller agreement: outline

*Structure and plain-language intent for the attorney who drafts the agreement. Discount tiers, inclusions and the channel principle are read from `config/pricing.yaml` so this document and the price list cannot disagree. Clauses marked [Attorney review] need legal text.*

**Parties:** {{alimi Entity}} ("alimi") and {{Reseller}} ("Reseller"). **Effective date:** {{Effective Date}}.

## 1. Who this is for

{{pricing.partners.reseller.who}}. The Reseller sells alimi's products and services to its own clients, under its own client relationship and invoices, and alimi supplies the products, the reports and, where the Reseller chooses, the delivery of the services.

## 2. Appointment

alimi appoints the Reseller as a non-exclusive reseller of the products and services listed in Schedule A (the current price list) to companies of 10 to 200 people. No territory is exclusive. The Reseller may not appoint sub-resellers without written consent.

## 3. Pricing and tiers

The Reseller buys at {{pricing.partners.reseller.buys_at}}. The discount depends on the number of the Reseller's client companies with an active alimi product or service:

{{pricing.partners.reseller.tiers_table}}

{{pricing.partners.reseller.review}}. The Reseller sets its own price to its clients. alimi's list prices may change with 60 days' notice; the discount tiers change only by written amendment.

## 4. The channel promise

{{pricing.partners.principle}} If a client of the Reseller approaches alimi directly, alimi refers them back to the Reseller unless the client asks in writing to deal with alimi, in which case alimi tells the Reseller and honours the Reseller's price.

## 5. What the Reseller gets

{{pricing.partners.reseller.includes}}

## 6. White-label terms

- The Reseller may put its own name and logo on the scanner report and the policy pack, with the "powered by alimi" line kept, and may present them as its own service to its clients.
- The Reseller may not change findings, scores, evidence or policy statements; it may add its own commentary in a clearly separate section.
- The Reseller may not claim certifications, insurer endorsements or results that alimi has not stated in writing. The honesty rules in alimi's own materials apply to the Reseller's use of them.
- alimi's templates and tools remain alimi's property; the Reseller gets a licence to use them only to serve its clients during the agreement. **[Attorney review]** Trademark licence and quality control wording.

## 7. Ordering, billing and payment

{{pricing.partners.reseller.billing}}. alimi invoices at the wholesale price on the first business day of each month for the previous month's activations and services; payment within 30 days. The Reseller is responsible for its clients' payment to it. Services delivered by alimi to the Reseller's client are scheduled with the Reseller and the client together.

## 8. The Reseller's clients' data

- Every client whose tenant alimi scans signs a pilot authorization letter or an SOW naming alimi, or the Reseller holds written authority from the client that covers alimi's read-only access and passes alimi's data-handling terms through. The Reseller warrants that it has that authority before it points alimi at a client tenant.
- Where the Reseller holds administrative access to the client's tenant (as a managed service provider), the Reseller creates the read-only access itself and alimi never receives the Reseller's administrative credentials.
- alimi processes client data only to deliver the product or service, under the data-handling terms of its Master Services Agreement, and treats it as the client's confidential information; alimi does not market to the Reseller's clients. **[Attorney review]** Data processing terms between alimi, the Reseller and the end client, and liability allocation if a client claims.

## 9. Marketing and conduct

Each party may name the other as a partner in its marketing with prior approval of the wording. The Reseller describes alimi's products accurately, using alimi's current materials, and does not make claims about insurance outcomes, audit results or breach prevention that alimi does not make. alimi provides the partner training session and one-pager in Schedule B and updates them when products change.

## 10. Leads

Inbound leads in the Reseller's area are offered to the Reseller first; the Reseller responds within five business days or the lead returns to alimi. Lead registration: the Reseller may register a prospect for 90 days, during which alimi does not sell to that prospect directly.

## 11. Support

alimi supports the Reseller's staff (not the end clients directly, unless a service SOW says so) by email within one business day. The Reseller provides first-line support to its clients.

## 12. Term and termination

One year, renewing automatically unless either party gives 60 days' notice. Either party may end for material breach not fixed within 30 days. On termination: in-progress services are completed or refunded; the Reseller stops using alimi's materials and name; clients with active products may continue with alimi directly or move with the Reseller to another supplier at the client's choice, and alimi honours the Reseller's price for those clients for six months. **[Attorney review]** Post-termination client handling.

## 13. Confidentiality, IP, liability, indemnity

As in alimi's Master Services Agreement, adapted to a channel relationship: each party keeps the other's business information confidential; alimi owns its products; liability capped at the amounts paid under the agreement in the previous twelve months with the usual carve-outs. **[Attorney review]** Full clauses.

## 14. Independent contractors, no agency

The Reseller is not alimi's agent and cannot bind alimi; alimi is not the Reseller's agent.

## 15. Governing law and disputes

Massachusetts law; principals' discussion, then mediation in Boston, then the Massachusetts courts. **[Attorney review]**

## Schedules

- **A.** Current price list and discount tiers (generated from `config/pricing.yaml` on the signing date).
- **B.** Partner training outline and sales one-pager.
- **C.** White-label specification: where the Reseller's logo appears, the "powered by alimi" line, and what may not be altered.

## Signatures

| | alimi | {{Reseller}} |
| --- | --- | --- |
| Name | {{alimi Signatory}} | {{Client Signatory}} |
| Title | | {{Client Title}} |
| Date | | |
