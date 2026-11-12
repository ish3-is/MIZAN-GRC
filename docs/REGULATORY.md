# Regulatory source plan and mapping methodology

Verification date: 2026-10-18, Asia/Riyadh. Canonical machine-readable register: `regulatory/sources.json`.

## Phase 0 plan

Gather official Saudi sources first; inspect source version and exact references; record access failures; classify legal nature; document organization applicability; have a Saudi regulatory specialist review Arabic interpretation; publish only reviewed scope. Source access is not a legal opinion. Effective dates remain null unless positively established.

### Source register decisions

| Source | Evidence available | Initial decision |
|---|---|---|
| NCA ECC 2:2024 | Official English PDF inspected; official Arabic PDF located | Five exact references checked; English-reference verification only; Arabic specialist review pending |
| NCA ECC implementation guide | Official guide URL identified | UNVERIFIED; no guide-derived requirements |
| SDAIA PDPL | Official portal reached | UNVERIFIED at article level; no statutory timers |
| PDPL implementing regulation | Official source located; partial portal material accessible | UNVERIFIED at article level |
| Transfers outside Kingdom regulation | Official portal and PDF located | UNVERIFIED at article level; no transfer validity inference |
| NDMO policy collection | Historical official document located | Currency and supersession UNVERIFIED |
| ISO/IEC 27701:2025 | Official ISO catalogue confirms edition 2 | Metadata verified; no licensed clauses copied |
| ISO 27001:2022, ISO 31000:2018, COBIT 2019 | Not reviewed for this build | Excluded from catalogue and scoring |
| NIST CSF 2.0 | Not reviewed for this build | Deferred; no invented mappings |

ECC starter IDs: `1-3-1`, `1-5-1`, `2-1-1`, `2-1-5`, `2.2.3.5`. The English PDF uses dotted sub-control IDs for the latter. Display the exact observed ID rather than silently rewriting it. English PDF page indices are stored with each record. Implementation advice and requested evidence are MIZAN organizational interpretations, not quoted regulator instructions. Arabic text governs meaning according to the official English document disclaimer.

## Source states

* UNVERIFIED: insufficient authoritative text or currency review. Never counted as legal fact.
* SOURCE_ACCESSED: source reached, without exhaustive requirement verification.
* METADATA_VERIFIED: publication metadata verified, not normative clauses.
* REFERENCE_VERIFIED: selected exact reference inspected in the identified source. Applicability and specialist interpretation remain separate.

Every source/control document carries framework ID, publisher, official URL, title, version, effective date (nullable), verification date, applicability, exact reference, nullable excerpt, summary, interpretation, implementation guidance, evidence requirements and verification status. Excerpts are null in the starter catalogue. No full proprietary standard text is bundled. Public availability is not assumed to grant unrestricted reuse rights.

## Applicability

The demonstration entity is synthetic and private. It has no documented critical national infrastructure designation, regulator direction or governmental status. Selected ECC controls are adopted as an organizational benchmark pending specialist scope approval; the platform does not assert every Saudi private organization is legally required to comply with ECC. PDPL applicability requires actual processing facts and legal review. Do not infer lawful basis, DPO appointment requirements, transfer conditions or incident deadlines from fictional seed data.

## Version-controlled update workflow

1. Create a branch; record previous source URL/version and review date in the register.
2. Retrieve the current publication from the official publisher. Record retrieval timestamp, hash of reviewed source in the review record (do not commit full copyrighted documents), access result and version differences.
3. Compare exact references and scope. Record withdrawn and new controls without overwriting previous assessment history.
4. Propose new summaries/interpretations and affected mappings. List linked assessments, evidence requests, policies, risks and privacy decisions using identifiers.
5. Obtain an independent specialist review of meaning, applicability, licensing and date rules. Capture reviewer/date and rationale in a source-review document.
6. Review the Git diff, run provenance checks and workflow tests, merge only approved material; reassess affected controls. UNVERIFIED records remain excluded from legal assertions.

The register is version-controlled. Automated source ingestion, in-app source approval, regulatory change impact calculation and GitHub approval enforcement are planned, not implemented. A Git reviewer must enforce this workflow manually for v0.1.

## Cross-framework mapping policy

No cross-framework equivalence is seeded. Future mapping records must specify source and target versions, exact IDs, relationship (partial overlap/support/equivalent), intent rationale, scope differences, implementation differences, evidence overlap, author, independent reviewer and approval. Suggestions must be pending until reviewed. An overlap never transfers a compliant rating automatically.

Official references:

* [NCA ECC official English PDF](https://cdn.nca.gov.sa/api/files/public/upload/86e09090-44e4-481f-bc28-355673607654_ECC--2024-EN.pdf)
* [NCA ECC Arabic source index](https://nca.gov.sa/ar/regulatory-documents/controls-list/ecc/)
* [NCA implementation guide](https://cdn.nca.gov.sa/api/files/public/upload/11bb8f2d-706a-4f18-80f1-40d620ebd845_GECC-.pdf)
* [SDAIA knowledge centre](https://dgp.sdaia.gov.sa/wps/portal/pdp/knowledgecenter/)
* [SDAIA regulations index](https://sdaia.gov.sa/en/SDAIA/about/Pages/RegulationsAndPolicies.aspx)
* [Historical NDMO policies](https://sdaia.gov.sa/ndmo/Files/PoliciesEn001.pdf)
* [ISO/IEC 27701 catalogue](https://www.iso.org/standard/27701)

## حدود الاستخدام

المنصة تدعم إدارة الامتثال ولا تمنح شهادة أو اعتماداً أو موافقة تنظيمية ولا تقدم مشورة قانونية. التحقق من مرجع إنجليزي لا يغني عن مراجعة النص العربي والانطباق القانوني. لم تُفعّل مهل نظامية أو مواد غير متحقق منها. بيانات المنشأة والأصول والأشخاص والموردين اصطناعية بالكامل.
