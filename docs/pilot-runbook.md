# Pilot runbook: a free pilot in one hour

How alimi onboards a free pilot: one company, one tenant, read-only, no fee, the full report in exchange for honest feedback and, if it goes well, a case study. Written for the operator (Alex) and kept short enough to follow live on a call. The rules in `CLAUDE.md` apply throughout: test tenants or a signed pilot letter only, read-only scopes, no customer tokens stored, no client data in the repo.

The scanner and report commands below are the ones in `tools/scanner/README.md` and `tools/report/README.md`; if those change, change this file in the same commit.

## 0. Before you offer a pilot

- [ ] The gates are met: the scanner and report run from your laptop (`alimi-scan m365`, `alimi-scan gws`, `alimi-report demo` all work in mock mode), the laptop has full-disk encryption on, and `pre-commit` is installed so nothing secret can be committed by accident.
- [ ] You have three pilot slots at most at any one time. A pilot is an hour of the client's admin time and about four hours of yours including the debrief.
- [ ] The pilot is free, read-only and produces a report. Fixing things, tabletops and anything that needs write access are paid services under an SOW and wait for the LLC and insurance.
- [ ] The prospect runs Microsoft 365 or Google Workspace, has 10 to 200 staff, and has a reason to care now: an insurance renewal, a customer questionnaire, a near miss. Write the reason down; it is the first line of the case study.

## 1. Days before: the letter and the prep email (15 minutes of your time)

1. Render the pilot authorization letter with the client's details:

   ```bash
   python templates/build/render.py --only pilot-authorization-letter \
     --set "Client=Acme Inc" --set "Client Address=..." --set "Client Contact=Dana Lee" \
     --set "Client Signatory=Sam Ortiz" --set "Client Title=CEO" \
     --set "Tenant=Microsoft 365" --set "Tenant Domain=acme.example" \
     --set "Start Date=2027-01-20" --set "End Date=2027-02-03" \
     --set "alimi Entity=..." --set "alimi Signatory=Alex Dennis" --set "alimi Address=..." \
     --set "Contact Email=..." --set "Contact Phone=..." --set "Effective Date=2027-01-15"
   ```

   Attach the appendix: the output of `alimi-scan checks -p m365` (or `-p gws`) and `alimi-scan permissions -p m365` (or `-p gws`), printed the same day. Send the DOCX for signature. **No access is created before the signed letter is back.**

2. Book a 45-minute call with the person who administers the tenant (in-house or their managed service provider) and the owner for the first ten minutes.

3. Send the prep email: the permissions table from `alimi-scan permissions`, a sentence that every permission is read-only and that nothing in the tenant will change, what the admin will do on the call (about 15 minutes of clicking), and that the owner should bring the insurance questionnaire or the customer's security questions if they have one.

4. Prepare your side: a fresh `.env` from `.env.example` with nothing filled in, an empty `out/` folder, and the client's row in your pilot tracker (date, company, platform, reason, contact, letter signed on).

## 2. The call (45 minutes)

### 0:00 to 0:10, with the owner

- Confirm the signed letter, the domain, the dates and who removes the access afterwards (their admin, on the date in the letter or straight after the scan if they prefer).
- Say what will happen in plain words: "We create a read-only key, I run a scan that reads settings and audit data, nothing changes, you get a report. If anything looks wrong on the way I stop."
- Ask the question that shapes the debrief: "If this report were perfect, what would you do with it?" (hand it to the broker, answer a customer, sleep better). Write the answer down.

### 0:10 to 0:30, with the admin, screen shared, the admin drives

**Microsoft 365.** Follow "Scan a real Microsoft 365 tenant" in the scanner README on the shared screen:

1. App registration named `alimi scanner (read-only)`, single tenant, no redirect URI.
2. API permissions, Microsoft Graph, *Application permissions*: the list from `alimi-scan permissions`. Grant admin consent. Point out on screen that every one ends in `Read`.
3. Client secret, 90 days or the pilot's length. The admin reads the secret aloud once while you type it into your `.env`, or sends it through a one-time secret link. Never by email or chat, and the admin can delete it the moment the scan is done.
4. The admin reads out the tenant ID and client ID; you fill `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_CLIENT_SECRET`.

**Google Workspace.** Follow "Scan a real Google Workspace tenant" in the scanner README. The service account lives in **your** Google Cloud project, created once before any pilot, so no key file ever moves between you and the client:

1. Give the admin your service account's client ID.
2. In their Admin console: Security, Access and data control, API controls, Manage Domain Wide Delegation, Add new; paste the client ID and the six read-only scopes from `alimi-scan permissions -p gws`.
3. The admin tells you which super admin address the scanner should act as; you fill `GWS_DELEGATED_ADMIN`. `GWS_SERVICE_ACCOUNT_FILE` already points at your key, kept outside the repo.
4. Ask whether they have knowingly approved any third-party apps (their helpdesk tool, an e-signature add-on) and note the client IDs for `--approved-app`, or leave it and discuss the list in the debrief.

### 0:30 to 0:40, the scan

```bash
alimi-scan m365 --tenant --authorized --save-snapshot
# or
alimi-scan gws --tenant --authorized --save-snapshot --approved-app <client id>
```

Watch the table. A row in magenta (`error`) names a permission or scope that was not granted: fix it with the admin on the call and run again. Yellow rows (`attestation needed`) are settings no API exposes; the report lists the screenshots the client will send you (outbound forwarding policy, audit log retention, third-party app restriction). Ask the admin to take those screenshots while you are still on the call; it saves a week of email.

If the scan fails outright, do not debug for more than five minutes on the client's time. Note the error, confirm the access is in place, and finish the scan on your own after the call. The connectors have not yet run against a real tenant at the time of writing, so the first pilot will probably find something; that is part of what the pilot is for.

### 0:40 to 0:45, close

- Tell the owner when the report will arrive (within two business days) and book the 30-minute debrief for a day after that.
- Agree the access removal date with the admin and put it in your tracker. If no rescan is planned, they can remove it now, while you watch.
- Thank them. Do not discuss findings yet; you have not read them.

## 3. After the call: the report (30 minutes of your time)

1. Read the findings file by hand before rendering anything. Check for false positives (a "legacy auth" sign-in from a scanner, a guest account that is a known contractor) and write them down for the debrief; do not edit the findings.
2. Render both versions:

   ```bash
   alimi-report render out/m365-<stamp>.findings.json --free --name acme-summary
   alimi-report render out/m365-<stamp>.findings.json --name acme-report
   ```

   The summary is what a free user would get; the pilot receives the full report. Open the PDF and read it as the owner would. If a sentence would not make sense to a non-technical person, fix the catalog text (`config/checks.yaml` `explain` and `remediation`) in a branch, not the report by hand, so every future report improves.
3. Send the full report to the contact named in the letter, by a link that expires or an encrypted attachment, never a plain attachment to a shared mailbox. Ask for the screenshots from the attestation list if you did not get them on the call.
4. Delete the `.env` values for this client now unless a rescan is agreed. The findings and snapshot stay in `out/` (git-ignored) until the deletion date in the letter.

## 4. The debrief call (30 minutes)

A script, not a speech. Keep the report on screen and let the owner drive the scrolling.

**Open (2 minutes).** "Thanks for the pilot. I will walk through the one-page summary, then the fixes, then what the report does not cover, then I have three questions for you. Stop me anywhere."

**The score and the grade (3 minutes).** Say what the number is: the weighted share of automated checks that passed, from settings read on that date. Say what it is not: a guarantee, an audit, or a prediction. If the grade is "At risk", say so plainly and follow with "all of this is fixable, and most of it in an afternoon".

**The insurer's questions (5 minutes).** Go down the table of Yes, No, You confirm, Not checked. For each No: what it means in one sentence, and the fix. For each You confirm: what evidence they would attach and where it comes from. Ask: "Which of these did your broker ask about last time?"

**The top five fixes (8 minutes).** In order. For each: what we found, why it matters to them (not in general), what to do, how long it takes, and whether it costs anything (a licence, a tool). Note which ones their admin can do this week. Point at the evidence pack checklist and explain it is the thing the broker wants.

**What the report does not cover (3 minutes).** Endpoints, backups, the incident plan: say they are attestation items and what evidence would satisfy an insurer. Mention the honest gaps (settings no API exposes) and that this is why the screenshots were requested. Credibility comes from this section more than from the score.

**Three questions (7 minutes).** Write the answers in the decisions log under "What partners and pilots said".

1. "What would you do with this report tomorrow?" Then: "Would you have paid for it? If so, what would have felt fair?" Read them the published range for the full report and for the fix-it service from `config/pricing.yaml`, and watch the reaction. Do not defend the price; record the reaction.
2. "Who else should see this?" The broker, the CPA, the attorney, the IT provider. Ask for an introduction by name. This is the partner pipeline.
3. The case-study ask (below).

**Close (2 minutes).** Confirm access removal happened or when it will, confirm the deletion date for your copies, and name the one next step: an introduction, a rescan after fixes, or nothing.

## 5. The case-study ask

Ask only when the pilot went well and the owner has said something you could quote. Words that work:

"Would you be willing to let me write up what we did as a one-page case study? You see the text before anything is published, you choose whether your company is named or it says 'a 40-person accounting firm in Boston', and you can withdraw it at any time. The results in it are only what we measured here."

If yes, render `templates/case-study-template.md` with their details, fill it from the findings and the debrief notes, send it for approval with the permission section, and publish nothing until the signed permission is back. If no, thank them and ask whether a sentence of feedback for your own use is fine. Never imply a client relationship in public that the permission form does not cover.

## 6. Clean-up checklist

Run this at the end of every pilot, whether or not it went well, and record the date of each step in your tracker.

**On the client's side (their admin does it, you confirm on a call or by screenshot):**

- [ ] Microsoft 365: delete the `alimi scanner (read-only)` app registration (or at minimum delete its client secret), and confirm it no longer appears under Enterprise applications.
- [ ] Google Workspace: remove the alimi client ID from Manage Domain Wide Delegation.
- [ ] Any screenshots or exports they made for the evidence pack are kept by them; you keep only what the letter allows.

**On your side:**

- [ ] Remove the client's values from `.env` (tenant ID, client ID, client secret, delegated admin). `git status` shows nothing to commit; `.env` was never tracked.
- [ ] Prove the access is gone: run the scan again. It must fail with an authentication or authorization error. Paste the error line into the tracker as the evidence of removal.
- [ ] On the deletion date in the letter (30 days after delivery unless the client asked otherwise), delete the findings, snapshot and report files from `out/`, from any encrypted attachment you sent, and from the trash. Tell the client by email that it is done.
- [ ] If a Google service account key was ever shared (it should not have been), rotate it in your project.
- [ ] Update the tracker: pilot closed, outcome, case-study status, introductions received.
- [ ] Write the lessons into the decisions log and open an issue or branch for any scanner or report fix the pilot revealed.

## 7. What to carry to every pilot

- The signed letter and this runbook.
- A laptop with the scanner and report installed, `pre-commit` on, disk encrypted, and a charged battery.
- The permissions tables for both platforms printed or on a second screen.
- The current price list (`config/pricing.yaml`) and the partner one-pager, for the three questions.
- A notebook. Half the value of a pilot is what the owner says when the report is on the screen.
