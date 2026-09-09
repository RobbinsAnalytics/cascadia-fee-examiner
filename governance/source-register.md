# Source register — Cascadia Fee Examiner

*Stage 1 artifact. Owner: Aaron Robbins. Established 2026-09-09.*

The authoritative record of **what was pulled, from where, when, what it hashes
to, and on what terms.** Nothing downstream re-downloads. `src/validate.py`
recomputes every hash below on every run and fails the build if one has moved.

**Two as-of dates, and they are different claims.** The spine is frozen at the
publisher's own release date. The cost layer is retrieved from a live archive
and carries its own retrieval date per document. `governance/freeze.toml`
carries the first; `data/raw/recap/manifest.csv` carries the second.

---

## S-01 · Florida-UCLA-LoPucki Bankruptcy Research Database — Cases table

| | |
|---|---|
| **Publisher** | University of Florida Levin College of Law, UCLA School of Law, and Lynn M. LoPucki |
| **Dataset page** | `https://lopucki.law.ufl.edu/index.php` |
| **Retrieved from** | `https://lopucki.law.ufl.edu/download_cases_table.php` |
| **Redirects to** | `https://lopucki.law.ufl.edu/Florida-UCLA-LoPucki%20Bankruptcy%20Research%20Database%201-12-2023.zip` |
| **Retrieved** | 2026-09-09 |
| **Bytes** | 2,938,544 |
| **SHA-256** | `03a17b10802b26eefce1d30a4dd45e774b3a252a16ad8fae60116185d97dfe70` |
| **Committed** | Yes, outright, at `data/raw/brd/brd_cases_table.zip` |
| **Members** | the Cases table as `.csv` (1,678,230 bytes) and `.xlsx`, `Protocols.pdf` (41 pp, release 2023-01-12), `User's manual.pdf` (16 pp, release 2021-02-04), `Read Me First.pdf`, two Stata `.do` files |
| **Rows / fields** | 1,218 cases × 217 fields |
| **As-of** | **2023-01-12, the publisher's release date** |

**The database is closed, and that is the publisher's decision rather than a
limitation of this pull.** The site states: *"We will no longer update the
Florida-UCLA-LoPucki Bankruptcy Research Database (BRD) after the December 2022
update."* It also states that the Cases table *"is now available free"* and that
the download link *"will remain active indefinitely."* Coverage is every public
company with assets of $100M or more in 1980 dollars that filed under Chapter 7
or Chapter 11 since 1 October 1979.

**Use conditions, quoted.** The publishers *"claim a copyright in (1) the
selection and organization of the BRD data and (2) both the protocols for data
collection and the data items generated according to creative protocols,"* and
each user *"agrees to acknowledge the 'Florida-UCLA-LoPucki Bankruptcy Research
Database,' by that or equivalent language, as the source of the data on any
manuscript, document, or transmission based on BRD data."* **That acknowledgement
is discharged in `README.md` and must appear on any published page.**

**The download is reproducible.** The same URL returned the same 2,938,544 bytes
and the same SHA-256 on two independent pulls, hours apart, on 2026-09-09.

## S-02 · U.S. Trustee Appendix B fee guidelines

| | |
|---|---|
| **Citation** | 78 FR 36248, Monday 17 June 2013, Notices, document 2013-14323 |
| **Retrieved from** | `https://www.govinfo.gov/content/pkg/FR-2013-06-17/pdf/2013-14323.pdf` |
| **Retrieved** | 2026-09-09 · **Bytes** 367,508 · 29 pages |
| **SHA-256** | `adc9a465d1dba1801f22dd0e9a41b816e348ab84bb66934e7c1725620dfe3512` |
| **Licence** | United States federal government work |

Source of the **project-category vocabulary** loaded in stage 2, and of the
population boundary in stage 1. Findings F-01 and F-02 below are quoted from it.

*Fetched from govinfo rather than federalregister.gov: that host redirected an
automated request to an `unblock.` interstitial. The govinfo PDF is the same
document from the same publisher and is the citable one.*

## S-03 · ABA UTBMS bankruptcy code set

| | |
|---|---|
| **Publisher** | American Bar Association; hosted by the LEDES Oversight Committee |
| **Retrieved from** | `https://utbms.com/wp-content/uploads/2023/11/ABA-UTBMS-Bankruptcy-Codes-1997.xlsx` |
| **Retrieved** | 2026-09-09 · **Bytes** 16,827 |
| **SHA-256** | `8df6fad5bdaa6d01aede8f5bb5c76232481fbd5f4e448c63d748cfff18de3f7e` |
| **Version** | **1997, and it is the only version.** See F-04 |

**Rights, quoted from the workbook itself:** *"This is the intellectual property
of the American Bar Association. Reproduced by LEDES Oversight Committee with
the permission of the ABA."* The site's terms state: *"You may download
materials displayed on this website."* The code set is loaded as a dimension and
its text is reproduced only as code definitions, with attribution.

## S-04 · CourtListener RECAP archive — *stage 3a*

| | |
|---|---|
| **Root** | `https://www.courtlistener.com/api/rest/v4/` |
| **Endpoint used** | `/search/?type=rd` (document-level), then `https://storage.courtlistener.com/<filepath_local>` |
| **Authentication** | **Not required** for `/search/` or for the storage PDFs; both serve anonymously. **Used anyway**, because the limit is six times higher with it. Token read from the `COURTLISTENER_TOKEN` user-scope environment variable, never from a file |
| **Rate limit, as the server states it** | Anonymous: *"Rate limit exceeded: 50/hour"*. Authenticated: *"Rate limit exceeded: 5/min"*. Both quoted from HTTP 429 bodies on 2026-09-09. The documented 5/min · 50/hour · 125/day describes the **authenticated** tier |
| **A measurement that was wrong** | A burst of 14 requests at 3-second spacing returned no 429, and spacing was set to 4 s on that basis. The run stopped itself after 86 requests in 25 minutes. A burst measurement says nothing about an hourly window; recorded here so it is not re-derived |
| **Publisher** | Free Law Project. Bulk data files are marked as free of known copyright restrictions |

**Retrieval date is per document**, recorded in `data/raw/recap/manifest.csv`.

## S-05 · Claims-agent case sites — **considered and excluded**

Recorded because the exclusion is a build constraint, not an oversight, and
because a later session will otherwise rediscover these sites as an obvious
alternative to RECAP's partial coverage.

Kroll Restructuring Administration's terms of use
(`https://media.ra.kroll.com/sitecontent/TermsOfUse/TermOfUse.html`) state that
the copying restrictions *"do not apply to any paper filed in a case under Title
11 of the United States Code (including proofs of claim and claim information)
and the docket(s) of such case, which are public records and open to examination
by an entity without charge."* The same document states: *"Any use of direct or
indirect automated searches or data queries with respect to this Site or the
Materials is strictly prohibited without Kroll's prior written consent."*

Epiq's terms carry the identical prohibition. Stretto's terms page returned 404
at two candidate URLs and was not established either way.

**So the documents are free to read and closed to us.** No retrieval script is
written against any claims agent. This is the reason RECAP's coverage rate is a
published measure rather than a problem to be routed around.

---

## Findings established at acquisition

**F-01 · The Appendix B population boundary is a filing date, and it is not the
guidelines' effective date.** The notice states the guidelines apply to
applications by attorneys in chapter 11 cases *"where the debtor's petition lists
$50 million or more in assets and $50 million or more in liabilities, aggregated
for jointly administered cases and excluding single asset real estate cases,"*
and that United States Trustees will use them in all qualifying cases *"that are
filed on or after October 1, 2013."* The Federal Register's own **Effective
Date is November 1, 2013** — the date the USTP began applying them, which is a
different fact. `src/build_spine.py` uses **1 October 2013** as the population
boundary and says so.

**F-02 · The electronic-billing requirement is weaker than a rule and stronger
than nothing, and the exact verb matters.** ¶C.10: *"The billing records
(detailed time and service entries) substantiating the application **should** be
provided in an open and searchable electronic data format: (i) With the
application to the court, the debtor-in-possession (or trustee), official
committees, the United States Trustee, and the fee review committee, fee
examiner, and fee auditor; and (ii) upon request, to any other party in
interest."* It adds that *"the applicant may provide the electronic data in the
manner in which it maintains it."* The notice's only reference to a named format
is a footnote pointing at LEDES for *"information regarding open electronic data
formats commonly used in legal e-billing"* — **it does not mandate LEDES.**
Guidelines express the USTP's policy positions and *"do not supersede local
rules, court orders, or other controlling authority."*

**This is why the module parses PDFs rather than reading LEDES files.** The
electronic data goes to the court and the parties; what reaches the public
docket is the application and its exhibits.

**F-03 · The mandated summary exhibits are the standardised layer, and they are
what stage 3b parses.** The notice prescribes model forms: Exhibit B, *"Summary
of Professionals Included in This Fee Application"*; Exhibit C, budget and
staffing plan; Exhibit D-1, *"Summary of Compensation Requested by Project
Category"*; Exhibit E, a summary cover sheet. ¶C.8 supplies 23 named project
categories that *"should be used to the extent applicable"*, noting the list *"is
not exclusive."* So the *summaries* are conformed by the guidelines while the
underlying time detail is formatted however each firm maintains it — which is
the opposite of the intuitive expectation and is the reason the parse degrades
in the direction it does.

**F-04 · The UTBMS bankruptcy code set has exactly one version, dated 1997.**
The brief's premise of annual revisions is false for this set: `utbms.com`
publishes one bankruptcy workbook and no change log. Revised sets exist for
*litigation* (DRI, 2007) and for activity, expense and project codes, but not for
bankruptcy. **Effective-dating in this module is therefore across vocabularies
rather than across years** — UTBMS-1997 against the USTP's 2013 categories
against whatever each firm actually uses.

**F-05 · The BRD's own fee fields do not reach the modern panel.** `ProfFees10k`
is populated on 151 of 1,218 cases and on **zero** of the 216 Appendix B-era
cases in the spine; `DateFeeRev` on 90 overall and zero in the era; and
`FeeReviewer` reads `pending` for every era case. The Protocols explain why:
`ProfFees10k` is *"as indicated on the debtor's 10-Ks … Amounts are reported only
if the debtor filed 10-Ks covering the period from filing through the
post-confirmation final fee applications,"* and *"for most cases in the BRD, no
total is available."*

**The consequence is structural: cost must come from the filings.** The
102-case LoPucki-Doherty professional-fees study is a separate artifact covering
1998–2007 with rich per-case fee variables, and its own archive of fee
applications and orders — advertised on the site as a 1.7 GB zip — **returns HTTP
404.** Neither is a substitute for the era population.

**F-06 · The Cases table is Latin-1 and the publisher documents no encoding.** A
UTF-8 read raises partway through. Recorded so a later session does not
rediscover it as a defect in this module's code.

**F-07 · Petition-size figures are missing on a fifth of the era population.**
`AssetsPetition` is null on 45 of the 224 era cases before the subject-matter
filter and `LiabPetition` on the same rows. So `meets_threshold` is a
three-state field — 168 true, 4 false, 44 unknown after the filter — and the
unknowns are counted rather than assumed into either bucket (PRINCIPLES rule 3).
The Protocols define `AssetsPetition` as *"Total assets of the debtors, as
indicated on 'Exhibit A' to the petition"*, so a missing value means the exhibit
was not filed or not captured, not that the debtor was small.

**F-08 · The forum-to-court mapping is a rule, and the rule is unverified until
it is exercised.** The BRD writes the forum as `DE`, `TX SD`, `NY SD`;
CourtListener's bankruptcy court ids are the lowercased state, the district
letter where one exists, then `b`. The rule produces 67 ids across the whole
spine and 18 across the era, and every one of them is plausible — but a rule can
be wrong for a forum this dataset has not shown us. **Stage 3a exercises each id
against the live archive and reports any that return no docket for any case.**
Until then this is a derivation, not a verified mapping.
