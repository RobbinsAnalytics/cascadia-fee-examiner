# Cascadia Fee Examiner

A governed conformed spine over U.S. large-corporate Chapter 11 professional
fees, built to demonstrate **entity resolution across sources and owners that do
not share a key**.

## Why "Fee Examiner"

A fee examiner is the officer a bankruptcy court appoints to review what the
professionals billed the estate. The name states the posture: this module
examines a cost record it did not produce, against vocabularies it did not
write, and publishes what it could not resolve.

## The three sources, and the joins that are hard

| Source | Publisher | What it contributes |
|---|---|---|
| Bankruptcy Research Database, Cases table | Florida Levin College of Law, UCLA School of Law, Lynn M. LoPucki | The frozen case spine: 1,218 large public-company bankruptcies, 1980 to 2022 |
| Fee applications and fee orders | The federal bankruptcy courts, via the RECAP archive | Hours, rates and fees by professional role and project category |
| UTBMS bankruptcy code set; U.S. Trustee Appendix B project categories | American Bar Association; Executive Office for U.S. Trustees | The conformed task vocabulary |

Within one case the docket number is a shared key, and that join is easy. The
resolution problems are one level down: the same law firm named three ways
across three systems, and one billing concept named differently by every firm
that files.

## Data attribution

This module uses data from the **Florida-UCLA-LoPucki Bankruptcy Research
Database**, as its use conditions require. The UTBMS bankruptcy code set is the
intellectual property of the American Bar Association, reproduced by the LEDES
Oversight Committee with the ABA's permission. Court filings are public records.
Full provenance, retrieval dates, hashes and terms are in
`governance/source-register.md`.

## Repository and folder names match

Local `cascadia-fee-examiner`, remote `cascadia-fee-examiner`. This is the first
repository under the estate's one-name convention; the older modules keep their
`-analytics` local suffix and are not renamed.
