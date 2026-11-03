# Security awareness training: the lesson plan

Date: Nov 2, 2026. The founder asked for end-user training as part of the platform and whether video modules can be made. This is the plan: eight short lessons, each with a script, slides, a quiz and a completion record, delivered inside the platform (prompt 18) and included in every tier. Video is a production step on top of the script, not a separate product; see "About video" at the end.

Why it belongs in the product: every cyber insurance questionnaire asks whether staff receive security awareness training at least yearly, and SOC 2, ISO 27001 (A.6.3), HIPAA (164.308(a)(5)) and the FTC Safeguards Rule ask the same in their own words. The control in `config/controls.yaml` ("Security awareness training yearly, with phishing practice") is proven today by an attestation; with the module it is proven by completion dates per person, read by the People module and the insurer dashboard.

## Rules for every lesson

- Under ten minutes. One habit per lesson, named in the title. A quiz of five questions; pass at four; retake allowed.
- Plain English, every term defined the first time (phishing, MFA, BEC), no fear, no hooded figures, no red triangles. Brand colours from `config/brand.yaml`.
- Written for a company of 10 people and up where the learner is the receptionist, the bookkeeper and the owner, not an engineer.
- Scenarios are composites built from public sources (FBI IC3, CISA, FTC), never a client story. Figures carry their source and year on the slide.
- Each lesson maps to the policies it teaches (by POL ID) and the controls it proves, so completion lands on the right row of the frameworks.
- New hire: lessons 1 to 4 within 30 days of the start date (the onboarding checklist in the People module). Everyone: all eight once a year; the yearly cycle resets on the anniversary of completion. Finance and admins get their role lesson too.

## The eight lessons

| # | Lesson | The one habit | Policies | Audience |
| --- | --- | --- | --- | --- |
| 1 | Spot the phish | Stop before you click; check the sender and the ask, and report it | POL-02 Acceptable use, POL-13 Incident response | Everyone |
| 2 | Verify before you pay | A new bank detail or an urgent payment gets a callback to a known number | POL-23 Payment verification procedure (the fraud kit) | Everyone; required for finance |
| 3 | Passwords, MFA and your accounts | A password manager, a unique passphrase per account, MFA everywhere it is offered | POL-03 Access control | Everyone |
| 4 | Handle customer data with care | Know what is confidential, share it only through approved tools, never to a personal account | POL-05 Data classification and handling, POL-11 Privacy | Everyone |
| 5 | Working safely from anywhere | Lock the screen, update the device, use the company account, no public Wi-Fi without the VPN or hotspot | POL-08 Endpoint and device, POL-09 Remote work | Everyone |
| 6 | AI tools at work | Use approved tools, never paste customer or confidential data into a tool that trains on it, label AI-drafted work | POL-22 AI acceptable use | Everyone |
| 7 | Something looks wrong | Report early, to whom, with what; nobody is in trouble for reporting | POL-13 Incident response | Everyone |
| 8 | Role lessons | Admins: least privilege, admin accounts without mail, change logging. Finance: the full payment fraud training (PFK-05, 20 minutes). Managers: onboarding and offboarding duties | POL-03, POL-23, POL-07 | By role |

Lesson 2 and the finance half of lesson 8 reuse the existing 20-minute script in `kits/payment-fraud/training-video-script.md`: lesson 2 is its slides 1 to 7 cut to eight minutes; finance staff take the full version.

## Lesson outlines

Each lesson follows the same shape: the scene (90 seconds), why it works on busy people (2 minutes), the habit in three steps (3 minutes), what to do when it has already happened (90 seconds), the quiz.

**1. Spot the phish.** Scene: a Monday-morning email from "the CEO" asking for gift cards, and a login page that looks like Microsoft 365. Why it works: urgency, authority, a familiar name, a near-identical domain. Habit: read the address not the name; hover the link; ask "did I expect this?"; report with the button or the address, then delete. If clicked: change the password, tell IT or the security lead now, nobody is in trouble for reporting. Quiz: pick the real address from four; what to do after clicking; which of these is a sign (all of them); who to tell; is a text message phishing (yes).

**2. Verify before you pay.** Scene: the supplier's bookkeeper writes from her real address with new bank details the day before a $40,000 invoice is due (the composite from PFK-05). Habit: the three rules of the procedure, the callback to a number from the file not the email, the second approver above the threshold. If paid: call the bank within the hour, call the FBI's IC3 line, keep every email. Quiz on the three rules, the callback source, the threshold, the first hour, and "the CEO says skip it" (no).

**3. Passwords, MFA and your accounts.** Scene: one reused password from a shopping site opens the company mailbox. Habit: the password manager generates and remembers; a passphrase you never reuse for the manager and the laptop; MFA (a second proof, usually the phone app) on every account that offers it; the authenticator app over text messages where possible. If a code prompt arrives you did not ask for: deny and report, it means someone has the password. Quiz on reuse, what MFA is, the unexpected prompt, sharing an account (never), where passwords live.

**4. Handle customer data with care.** Scene: a spreadsheet of client payroll data forwarded to a personal Gmail "to finish at home". Habit: the three labels (public, internal, confidential) and what each may travel in; share from the company drive with a link that expires; personal accounts and personal devices are off limits for confidential data; shred and delete on the schedule. If sent wrongly: recall if you can, tell the security lead, record it (it may be a notifiable incident). Quiz on labels, the right way to share a file with a client, personal email, a USB stick found in the car park, who decides a label.

**5. Working safely from anywhere.** Scene: a laptop left unlocked in a café while ordering. Habit: lock the screen every time you stand up (the shortcut); install updates the day they arrive; use the company account and the company device; on public Wi-Fi use the phone hotspot or the VPN; shoulder surfers and video calls in public. If the device is lost: report within the hour so it can be wiped; the password manager means nothing else is lost. Quiz.

**6. AI tools at work.** Scene: a draft contract pasted into a free chatbot to "tidy the wording". Habit: the approved list and how to ask for a tool; what never goes in (customer data, personal data, credentials, confidential plans) unless the tool is approved for it; check every fact an AI writes; label drafts; the company account not a personal one. If pasted: tell the AI lead, the tool's data controls may allow deletion. Quiz on approved tools, what may be entered, checking output, labelling, personal accounts.

**7. Something looks wrong.** Scene: the laptop fan is loud, files have strange names, a colleague's email asks for something odd. Habit: report early, to the named person, with the four facts (what, when, which device or account, what you did); do not investigate, do not switch off (unplug the network instead if told to); nobody is in trouble for reporting, including a false alarm. Quiz on the four facts, who to tell, "I only clicked, nothing happened" (report anyway), the ransom note on screen, the false alarm.

**8. Role lessons.** Admins (10 minutes): separate admin accounts without mailboxes, least privilege and reviews, MFA that cannot be bypassed, logging on and read the alerts, change control. Finance (20 minutes): the full PFK-05 training with the drill. Managers (8 minutes): the day-one checklist for a hire, the same-day checklist for a leaver, approving access, acknowledging policies for the team.

## What the frameworks require, and the review before building

The founder reviews the eight lessons against each framework's training requirement before prompt 18 runs (agenda item of Nov 2, 2026). The table of requirement IDs, our one-line summaries and the lessons that answer each is in `docs/agenda.md` under "The training review"; once verified it moves here and the lessons' front matter carries the IDs, so a completion record lands on the right requirement of every framework the customer holds.

## Build (prompt 18, after prompt 13)

- Content lives in `/training` as Markdown with YAML front matter: id, title, audience, minutes, policies, controls, version, script, slide list, quiz (questions, choices, answer, explanation). The platform imports it the way it imports `/policies`.
- The platform renders a lesson as a page of slides with the script as the reading text (and the video embedded when one exists), then the quiz; a pass writes a completion record (person, lesson, version, date, score) that the People module and the insurer dashboard read. Reminders at 14 and 3 days before the yearly due date; the onboarding checklist adds lessons 1 to 4.
- Slides build to PPTX and PDF from the same Markdown (the fraud kit's build script is the pattern), so a company without the platform can run the lesson in a meeting.
- Content is never public: lessons are behind sign-in, like the policies.

## About video

Video cannot be recorded in this repository or by the assistant; what can be produced is everything a recording needs: the script with timings, the slides, the quiz and the production notes (the fraud kit's PFK-05 is the model). To make the videos at no cost: record each lesson as a screen capture with voice over the slides (OBS Studio is free; Loom's free tier allows five-minute clips, so lessons would be split), or generate a voice from the script with a free text-to-speech tool and lay it over the slides. The platform treats a lesson with no video as a reading lesson and marks completion the same way, so the insurer's question is answered before any video exists.
