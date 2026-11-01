---
id: PFK-02
slug: callback-scripts
title: Callback Scripts for Finance Staff
kind: scripts
---
> Part of the alimi Payment Fraud Protection Kit. Adapt the names and numbers to your company before adopting.

# {{Company}} Callback Scripts for Finance Staff

These are the words to use when the Payment Verification Procedure says "call". Read them aloud once before you need them; after that they are a safety net, not a script to recite. The goal of every call is the same: reach a person you already know, on a number you already had, and hear them confirm the details in their own words.

## Before you dial

- Find the number in the vendor record, the signed contract, or the vendor's website typed into the browser. Not the email. Not the invoice. Not the voicemail that asked you to call back.
- Have the request in front of you: what changed, who asked, when.
- Open the verification log so you can write while you talk.
- If the vendor's only number on file is a mobile belonging to the person who sent the request, call the company's main line instead and ask to be put through. A criminal who controls someone's email may also control their phone forwarding.

## Script 1. A vendor asks to change bank details

**Reach the main line, then the person you know.**

> Hi, this is {{Your Name}} from {{Company}} accounts payable. Could I speak with [known contact] in your finance team, please?

**When you have them:**

> We received an email on [date] asking us to change the bank account we pay you into. Before we change anything, we call to confirm. Did you send that request?

**If yes:**

> Thanks. Can you read me the new account number and routing number, please? [Compare with the email, digit by digit. Do not read them out first.] And the bank name? Can you tell me why the account changed? [Note the reason.] Who at your company approved the change? Thank you. We will update our records after a 24-hour hold, so the first payment to the new account will go out no earlier than [date]. Our first payment will be [small amount] and we will ask you to confirm it arrived before we release the rest.

**If no, or unsure:**

> Then please treat your email as possibly compromised. We will not change anything, and we will keep paying the account we already have. I am going to forward the message to your IT contact if you give me their name. Please let us know what you find.

Then tell {{Security Lead}} and log the attempt as fraud.

**If the person who answers is not someone you know, or the number on file now rings somewhere odd:**

> I need to speak with [known contact] or your finance manager directly. If they are not available, I will call back tomorrow; please do not change anything for us in the meantime.

Hang up, note it, and try again the next business day on the same number. Never accept "call this other number instead" from the person on the line.

## Script 2. Setting up a new vendor

**Call the number you found independently (company website, registry, business directory), not the one on the form.**

> Hello, this is {{Your Name}} from {{Company}}. We are setting you up as a new supplier. Could I speak with whoever handles your invoicing or accounts receivable?

**When you have them:**

> We have a vendor form from [name] at your company giving your bank details for payment. I would like to confirm them with you directly. What is the account name? [Should be the company's legal name, not a person.] And the account number and routing number? [Compare.] Is [name] someone who works with you? Thank you. Our first payment will be after a one-business-day hold.

## Script 3. The boss asks for an urgent payment

The request arrives by email, text or chat: "I need you to send $X to this account today, I'm tied up, I'll explain later, keep this between us."

**Do not reply to the message. Call {{CEO}} on the number you have, or walk over.**

> Hi, it's {{Your Name}}. I got a message from you asking me to send [amount] to [payee] today. I'm calling to confirm it's really you before I do anything.

**If they confirm:** it still goes through the procedure. Say so.

> Great. I'll need the payee set up under the normal steps, so it will go out after the callback and the hold. If it genuinely cannot wait, you and {{Finance Lead}} both need to sign the exception.

**If they did not send it:** tell {{Security Lead}} immediately and keep the message. Their email or phone may be compromised.

**If they push back:** this line is approved by {{CEO}} in advance.

> I understand it's urgent. The procedure is the same for everyone, including you, and you asked us to hold to it. I can have it ready to go the moment the steps are done.

## Script 4. An employee asks to change their direct deposit

**By email, text or chat:**

> Thanks for letting me know. For security we don't take bank changes by message. Please update it yourself in [payroll system] with your login, or come by with your ID and we will do it together. It takes two minutes.

**Then, before the next pay run, call the employee on the number in their HR record:**

> Hi, it's {{Your Name}} in payroll. I'm confirming that you changed your direct deposit on [date] to an account ending in [last four digits]. Was that you? Thanks. It takes effect on [pay date].

If the employee did not make the change, lock their payroll access, revert the account, and tell {{Security Lead}}.

## Script 5. A customer asks us to confirm our own bank details

A customer calls or emails: "We received a notice that your bank details changed."

> Thank you for checking. {{Company}} has not changed its bank account, and we never notify changes by email. Please do not pay the new details. Could you forward the message you received to {{Security Lead}} at [address]? We are going to treat this as a security incident on our side.

Then open an incident. Our email, or theirs, is compromised.

## Script 6. You cannot reach anyone

The number on file rings out, goes to a full voicemail, or the only person who answers cannot confirm anything.

> This is {{Your Name}} from {{Company}}. We are calling to verify a payment detail before we release funds. Please have [known contact] or your finance manager call me back on [our main number]; we will not be able to pay until we have spoken.

Log the attempt. Do not pay. Do not use an alternative number offered by email. Try again the next business day. A real vendor would rather wait a day than lose the payment to a criminal, and most will thank you for calling.

## Things you never say on a callback

- The new account number first. Let them read it to you.
- "I'm sure it's fine, I just have to tick a box."
- "Can you give me a better number to reach you?" when the caller suggests one.
- "We'll pay now and sort it out later."

## Red flags to listen for

- The person is reluctant to put you through to someone you know.
- The story about why the account changed shifts when you ask a second question.
- Pressure: "the CEO is waiting", "the deal falls through today", "I'll lose my job".
- A request to keep the change quiet or to avoid the usual contact.
- Background that does not match a business office.

If you hear any of these, end the call politely, log it, and talk to {{Finance Lead}} before anything else happens.

## After every call

Write it in the verification log: date and time, who you called, which number and where it came from, who answered, what they confirmed, the reason given, and the outcome. The second approver reads the log entry, not the email, before approving.
