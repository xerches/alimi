---
id: PFK-01
slug: payment-verification-procedure
title: Payment Verification Procedure
kind: procedure
---
> Part of the alimi Payment Fraud Protection Kit. Adapt the names, numbers and threshold to your company before adopting.

# {{Company}} Payment Verification Procedure

| Field | Value |
| --- | --- |
| Owner | {{Finance Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Two-person threshold | {{Threshold}} |
| Bank fraud line | {{Bank Fraud Line}} |

## 1. Why this exists

The most expensive crime a company of {{Company}}'s size faces is not a hack. It is an email. Someone pretending to be a supplier, a colleague or the boss asks for a payment to go somewhere new, and the money is sent before anyone picks up the phone. The FBI calls this **business email compromise (BEC)**: a criminal either breaks into a real email account or sends from a look-alike address, watches for an invoice or a deal about to close, and swaps in their own bank details. Wires are usually gone within hours. Recovery is possible only if the bank is called the same day, and often not then.

Technology helps, but the control that works is a habit: before money goes to a new place, a person calls a number they already trust and asks. This procedure makes that habit a rule, with two more rules behind it so that one busy afternoon cannot cost the company a year's profit.

## 2. Who follows it

Everyone who can create a vendor, change bank details, approve or release a payment, change payroll details, or ask someone else to do any of those. That includes {{CEO}}. The rules do not bend for seniority, urgency, size of customer or how well we know the vendor, because every one of those is exactly what the criminal counts on.

## 3. The three rules

**Rule 1. Verified callback.** Any request to add or change where money goes (a new vendor, new bank details, a new payee for payroll, a new address to mail a check) is confirmed by calling a phone number {{Company}} already had on file before the request arrived: the number in the signed contract, in the vendor record, or on the vendor's own website reached by typing its address. Never a number from the email, the invoice, the letter or the caller. We speak to a person we know, read back the full account number, and ask why it changed.

**Rule 2. Two people.** Every bank-detail change, and every payment above {{Threshold}}, involves two different people: one prepares it, the other approves it after seeing the callback record. Nobody approves their own request, and nobody approves on the strength of a forwarded email.

**Rule 3. Twenty-four-hour hold.** New or changed bank details are not paid for 24 hours (one business day) after the callback. Where the vendor allows it, the first payment to new details is a small one, confirmed as received before the balance follows.

## 4. The procedure

### 4.1 New vendor

1. The person who wants to use the vendor sends them {{Company}}'s vendor form, which collects legal name, tax ID, address, a named contact, a phone number from an independent source, and bank details on the vendor's own letterhead.
2. {{Finance Lead}} (or the person they delegate) checks the vendor exists: website, business registry or tax ID match, and a phone number for the main office found independently of the form.
3. Rule 1: call the independently found number, reach the named contact, and read back the account number, routing number and bank name. Note who you spoke to and when in the verification log.
4. Rule 2: a second person reviews the form, the log entry and the evidence, then approves the vendor record.
5. Rule 3: the first payment is scheduled no sooner than the next business day.

### 4.2 Change to an existing vendor's bank details

Treat every change request as fraud until proven otherwise. Most are genuine; the one that is not will look the most genuine of all.

6. Do not reply to the message, click its links or open its attachments. Save it for the log.
7. Look at the sender's address letter by letter and compare it with earlier messages from the same vendor. Look-alike domains swap a letter (rn for m, 1 for l) or add a word. A real address can also be compromised, so a matching address proves nothing on its own.
8. Rule 1: call the vendor on the number already in the vendor record. Ask for the contact we know. Confirm whether they asked for the change, read back the new details, and ask why the account changed. "Our bank was acquired" and "we changed banks for better rates" need the vendor's finance person on the line, not the salesperson.
9. If the vendor says they did not ask: tell them their email may be compromised, keep the message as evidence, and tell {{Security Lead}}. The old details stay.
10. If confirmed: record the call, the person, the time and the reason. Rule 2: a second person approves the change against the log. Rule 3: hold 24 hours; pay a small first amount where the vendor agrees.
11. Changes requested by phone or in person follow the same steps: the callback still goes to the number on file, not to the number the caller offers.

### 4.3 Payroll and expense changes

12. Requests from staff to change direct deposit details are made in the HR or payroll system with the employee's own login and a second factor, or in person with identification. A request by email, text or chat is not acted on; the employee is asked to use the system or come by.
13. {{Finance Lead}} or HR confirms the change with the employee by phone on the number in the HR record or face to face before the next pay run. A change received in the last three business days before payday takes effect the following run unless confirmed in person.

### 4.4 Requests from the boss

14. {{CEO}} and other managers will never ask, by email, text or chat alone, for a payment outside this procedure, for gift cards, for a transfer to be kept confidential, or for the rules to be skipped "just this once". Any such request is verified by calling the person on their known number or walking over. Urgency plus secrecy means stop.
15. A manager who is told "I'm in a meeting, just do it" by someone claiming to be them should expect staff to refuse. That refusal is the procedure working, and it is thanked, not punished.

### 4.5 Protecting our own customers

16. {{Company}} tells customers, in the contract and on every invoice, that its bank details never change by email and that a customer who receives a change notice should call {{Finance Lead}} on the number in the contract before paying.
17. If a customer reports a change notice or pays the wrong account, {{Company}} treats it as an incident: our email may be compromised. {{Security Lead}} is told at once and the Incident Response Policy applies.

### 4.6 Choosing how to pay

18. Where the vendor accepts it, pay by ACH (the US bank-to-bank network used for direct deposit and most bill payments) or by card rather than by wire. A wire is final within hours; ACH gives a short window to recall and card payments can be disputed. Checks are mailed only to addresses verified under Rule 1 and the bank's positive-pay service is used where available.
19. Payment files and online banking are protected by multi-factor authentication, separate approval rights for the second person, and daily limits agreed with the bank.

### 4.7 The verification log

20. Every callback is logged: date and time, vendor or payee, who requested the change and how, what changed, the number called and where it came from, who answered, the outcome, the approver and the date the hold ended. The log is kept for seven years. {{Finance Lead}} spot-checks ten entries a quarter against the payments actually made.

## 5. Red flags

Any of these means slow down and call:

- A change of bank details, however routine the wording.
- Urgency, secrecy, or pressure to skip a step.
- A new contact person, a new domain, a reply-to address that differs from the sender, or "please use my personal email while our system is down".
- An invoice that arrives just before a known payment date, or for a round amount.
- Bank account in a different country or state from the vendor, or in a person's name rather than the company's.
- A request to pay by gift card, cryptocurrency, or a payment app.
- A phone number in the email that does not match the one on file.
- Grammar or tone slightly off for a person we know.

## 6. If money has gone out

The first hour matters more than anything else.

21. Call the bank's fraud line ({{Bank Fraud Line}}) immediately, say it is a fraudulent transfer, and ask for a recall. If you know the receiving bank, the bank can contact it directly. For ACH payments ask for a return; for card payments open a dispute.
22. Report to the FBI's Internet Crime Complaint Center at ic3.gov the same day, with the amounts, account numbers and times. For wires of $50,000 or more sent internationally within the last 72 hours, tell the bank and the FBI that you are asking for the Financial Fraud Kill Chain, the FBI's recall process with foreign banks.
23. Tell {{CEO}} and {{Security Lead}}. {{Security Lead}} opens an incident under the Incident Response Policy: preserve the emails and headers, check the mailboxes involved for forwarding rules and unknown sign-ins, reset credentials, and notify the cyber insurer within the time the policy allows.
24. Tell the real vendor, so that they can warn their other customers and check their own email.
25. Do not negotiate with or reply to the fraudster, and do not wipe any device or mailbox until {{Security Lead}} says so.

## 7. Exceptions

There are no exceptions to Rule 1 or Rule 2. {{CEO}} may change the threshold in writing. The 24-hour hold may be shortened for a specific payment only when {{CEO}} and {{Finance Lead}} both confirm in writing, after a completed callback, that the business need is real; the exception is logged next to the callback.

## 8. Training and drills

26. Everyone who can touch a payment watches the 20-minute training in their first week and once a year, and keeps the staff poster at their desk.
27. Once a year {{Security Lead}} runs a drill: a realistic change request, agreed in advance with {{CEO}}, sent to the finance team. Nobody is named afterwards; the result goes into the next training.
28. New finance staff shadow a verified callback before doing one.

## 9. Review

{{Finance Lead}} reviews this procedure yearly, after any attempted or successful fraud, and when the bank, the payment system or the team changes.

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi Payment Fraud Protection Kit |
