---
id: POL-17
slug: physical-and-environmental-security-policy
title: Physical and Environmental Security Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: "{{Company}}'s offices, any room or cabinet that holds equipment or paper records, and equipment wherever it is"
requirements:
  soc2: [CC6.4, CC6.5, A1.2]
  iso27001: ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.7.8", "A.7.11", "A.7.12", "A.7.13", "A.7.14"]
  iso42001: []
  hipaa: ["164.310(a)(1)", "164.310(c)"]
  insurer: []
related: [POL-05, POL-12, POL-18, POL-20]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Physical and Environmental Security Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-17 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Most of {{Company}}'s information lives in cloud services, but the laptops that reach it, the network equipment in the cupboard, the printer tray, the whiteboard after a planning session and the filing cabinet with signed contracts are all physical, and all of them can be walked out of the door. This policy keeps unauthorised people away from equipment and records, protects equipment from the environment it sits in, and makes sure nothing with data on it leaves the building unnoticed.

## 2. Scope

Every office, coworking space or shared building where {{Company}} staff work regularly; any server room, network cupboard, storage room or locked cabinet; the equipment and paper records in them; and company equipment while it is in transit or being repaired. Working from home and public places is the Remote Work and Personal Devices Policy. Data centres run by cloud providers are covered by the provider's own controls, reviewed under the Vendor and Third-Party Risk Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy, decides which areas are secure areas, reviews access lists and visitor records. |
| {{IT Lead}} or managed service provider | Keeps equipment rooms and network equipment secure, maintains equipment, supervises repairs. |
| Office manager or {{HR Lead}} | Issues and recovers keys and badges, hosts visitors, keeps the visitor log, liaises with the landlord. |
| Everyone | Wears their badge where used, challenges or reports strangers, keeps desks and screens clear, escorts their visitors. |

## 4. Policy statements

### 4.1 Zones and who may enter

1. {{Security Lead}} divides the premises into public areas (reception, meeting rooms used by visitors), staff areas (open office) and secure areas (server or network rooms, records storage, any room where regulated data is handled on paper). Each area has a named owner and a list of who may enter.
2. Staff areas are protected by a locked door with a key, code, badge or smart lock; the office is not left open and unattended. Secure areas have their own lock, a list of named key or code holders kept by {{Security Lead}}, and where the value justifies it, an access log or camera. Codes are changed and keys recovered when a holder leaves or at least yearly.
3. Keys, badges and codes are issued by name, recorded, and returned on the leaver checklist under the Human Resources Security Policy. Loss of a key or badge is reported the same day and the lock or code is changed if the loss could be exploited.
4. Visitors sign in with name, company, host and time, wear a visitor badge, are escorted in staff and secure areas at all times, and sign out. Contractors who need unescorted access (cleaners, building maintenance, the managed service provider) are vetted by the office manager, listed, and their access limited to the hours and areas they need. Deliveries are received at reception, not in the office.
5. Everyone is expected to politely challenge an unbadged stranger ("Can I help you find someone?") or report them to the office manager. Tailgating through a locked door is not allowed, even for people who look like they belong.

### 4.2 Inside the office

6. Screens are locked when unattended, and desks are cleared of confidential paper, removable media and unlocked devices at the end of the day and before visitors use the space. Printouts are collected immediately; printers use release-on-badge or a code where available. Whiteboards in shared rooms are wiped after meetings about confidential matters. Confidential paper goes in locked shred bins, never in the recycling.
7. Offices and meeting rooms used for confidential work face away from windows where passers-by could read screens, or use privacy filters. Reception and shared spaces do not display internal information, customer names or schedules.
8. Secure areas contain no unnecessary combustibles, food or drink, are kept locked when unoccupied, and are not signposted on floor plans visible to the public.

### 4.3 Equipment

9. Network and server equipment is in a locked room or cabinet, on a rack or shelf rather than the floor, with cables tidy and labelled, and power through a surge protector and an uninterruptible power supply that gives time to shut down cleanly. Equipment that must be in open areas (switches, access points, printers) is mounted out of casual reach and its management interfaces are password protected.
10. Equipment rooms have a smoke detector, a temperature that stays in the manufacturer's range, no water pipes overhead, and nothing stored that would block ventilation or exits. Office equipment is protected from fire, flood, theft and power failure to the standard the building and the insurer expect; for a small company this is usually the landlord's fire systems plus the company's own power protection and locks.
11. Equipment is maintained as the manufacturer recommends, by staff or suppliers approved by {{IT Lead}}. A device sent for repair has its data encrypted and, where possible, removed or wiped first; repairs by outside parties are recorded in the asset register. Warranty, support and end-of-life dates are tracked so that equipment is replaced before it fails or stops receiving security updates.
12. No equipment, media or paper records leave the premises without the knowledge of the asset owner and, for anything that holds confidential data, a record in the asset register under the Asset Management Policy. Equipment that leaves regularly (laptops, phones) is encrypted and tracked under the Remote Work and Personal Devices Policy.
13. Equipment and media being retired are wiped or destroyed under the Data Retention and Disposal Policy before leaving the company's control, with a certificate from the disposal supplier where one is used.

### 4.4 Environment and continuity

14. Physical threats to the premises (fire, flood, storm, power loss, break-in, civil disturbance) are assessed in the risk register, and the continuity plan says how the business keeps working if the office is unavailable, under the Business Continuity and Disaster Recovery Policy. Nothing essential exists only in the office: documents are in the cloud tenant and backed up under the Backup and Recovery Policy.
15. Supporting utilities (power, internet, heating and cooling for equipment rooms) have the redundancy their importance justifies, typically a second internet line or mobile hotspots and the uninterruptible power supply in statement 9.

### 4.5 Where health or other regulated records are handled

16. Where {{Company}} holds protected health information or similar regulated records on paper or on workstations, the workstations are in staff or secure areas, positioned so that screens are not visible to the public, locked when unattended, and the paper is in locked cabinets inside a secure area with access limited to the people whose role needs it. A record of who has physical access to those areas is kept and reviewed at least every six months.

## 5. Exceptions

Follow the Information Security Policy. A shared building where the company cannot control the outer door, or a secure area without a lock, is a recorded risk with compensating measures (locked cabinets, encryption, no paper records) accepted by {{CEO}}.

## 6. Enforcement

Propped doors, lost keys not reported, visitors left unescorted and confidential paper left out are raised with the person and their manager; repeated or deliberate breaches follow the Acceptable Use Policy.

## 7. Review

{{Security Lead}} reviews this policy yearly, before and after any office move, after any break-in, loss or environmental event, and when the company starts handling a new kind of regulated data.

## 8. Related documents

POL-05 Asset Management · POL-11 Backup and Recovery · POL-12 Business Continuity and Disaster Recovery · POL-16 Human Resources Security · POL-18 Remote Work and Personal Devices · POL-20 Data Retention and Disposal · the key and badge register · the visitor log.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
