# Legal exposure

Compare the running product with the published rules below. This file does not decide that a statute applies, that a name is free to use, or that the product is lawful. Record a finding when the behaviour is present. Record NOT APPLICABLE, with the reason, when the product has none of that behaviour. A lawyer reviews the conclusion. An audit does not give one.

Ownership tests, secret handling, account deletion, and AI quotas already have mandatory checks. Use those IDs. The other items here are findings. An open high finding still blocks a GO.

## Notice matches the data flow

List every place personal data leaves the application: identity provider, database host, email, payments, error tracking, product analytics, advertising tags, session replay, AI provider, file storage, and support tools. Compare that list with the privacy notice.

[GDPR Article 13(1)(e)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) requires the recipients or categories of recipients. The [EDPB consent guidelines](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en) say the Article 13 and 14 information includes processors. A notice that names no recipient, while the code sends account data to several vendors, is a finding. A category is acceptable when a reader can tell which kind of company receives the data. A vendor that receives data and fits no stated category is a finding.

When the California Consumer Privacy Act applies, the notice at collection in [Civil Code section 1798.100](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1798.100) is the matching duty. Do not treat it as universal.

## Erasure

A delete control removes or irreversibly anonymises the private data the notice names, including files, search indexes, and copies held for product features. Setting a hidden flag while the row, object, or export remains readable is a failure. [GDPR Article 17](https://eur-lex.europa.eu/eli/reg/2016/679/oj) requires erasure in the cases it lists, and Article 17(2) requires the controller to inform recipients unless that is impossible or disproportionate. Legal duties to keep a record, such as tax or a dispute, are exceptions: name the data that is kept and why.

Backups that cannot be edited immediately stay a residual risk, as in [data-privacy.md](data-privacy.md). The mandatory check is `account-deletion`.

## Another person's data

A public client key, a logged-out browser, or one user's token is not a privacy control. With synthetic accounts, request another user's profile, messages, files, and invoices, including by calling the API directly. [OWASP API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) is the failure. A pass needs an executed request on the current commit. The method is in [security-testing.md](security-testing.md). The mandatory check is `ownership`.

## Data minimisation

[GDPR Article 5(1)(c)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) limits personal data to what is adequate, relevant, and necessary. A field the product collects and no feature reads is a finding. Government ID images, selfies processed to identify a person, and precise location are the high-severity cases. [Article 9](https://eur-lex.europa.eu/eli/reg/2016/679/oj) covers biometric data used for unique identification. Removing the field from the form leaves a finding while old rows, buckets, or logs still store it.

## Children

Keep the US rule and the European rule apart.

The [COPPA Rule, 16 CFR Part 312](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312), applies to an operator of a site or service directed to children under 13, and to an operator with actual knowledge that it collects personal information from a child under 13. The [April 2025 amendments](https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm) took effect on 23 June 2025, and most new duties had a compliance date of 22 April 2026. Those duties include a separate verifiable parental consent before children's personal information is disclosed to third parties for targeted advertising, and a ban on conditioning access on that consent. Behavioural advertising to children is off unless a parent has given that separate consent.

[GDPR Article 8](https://eur-lex.europa.eu/eli/reg/2016/679/oj) applies when consent is the lawful basis for an information-society service offered directly to a child. The regulation's age is 16. A Member State may set a lower age, not below 13. The UK age is 13. Do not copy the US age into a European product.

If a child under the applicable age can open an account, check three things: advertising and analytics do not share that child's data before the required parental consent; the consent step is the verifiable method the rule requires, which a self-reported "I am a parent" checkbox is not; and a parent can review and delete the data. If the product is a general-audience tool with no age signal, record whether under-13 signup is possible. Do not label every such product a COPPA violation.

The public enforcement figure for a game studio is the FTC's December 2022 Epic Games order: a [$275 million COPPA civil penalty](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-275-million-coppa-violations). A separate Epic order required [$245 million in refunds](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-than-half-billion-over-ftc-allegations) for billing practices. Do not replace either figure with a round number from a video.

## Cancellation

When a charge starts as a trial or renews until the customer stops it, [15 USC 8403](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title15-section8403&num=0&edition=prelim) requires the material terms before billing data is taken, express informed consent before the charge, and simple mechanisms to stop recurring charges. The FTC's 2024 Negative Option Rule was vacated by the Eighth Circuit on 8 July 2025 in Custom Communications, Inc. v. FTC, No. 24-3137. Audit against ROSCA and the state automatic-renewal statute that applies. One state example, when the customer is in California and signed up online, is [Business and Professions Code section 17602](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=17602): cancellation is online as well.

The same class of user who can subscribe can cancel without a phone call, a chat queue, or a buried form. Cancellation stops the next charge. The entitlement ends on the schedule the product states. A cancel path that is harder than the subscribe path is a finding. Payment mechanics stay in [payment-security.md](payment-security.md).

## Tracking before agreement

An analytics tag, advertising pixel, or session replay that identifies a person or sends personal data to a third party waits for the notice and, where the law requires it, for consent. The [ICO's PECR cookie guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/) requires consent before non-essential cookies, including analytics. Strictly necessary cookies are the narrow exception. A banner that appears after the request has already been sent is not consent.

A claim that a game studio paid $1.4 million for loading analytics before consent does not match the FTC orders checked for this file. [United States v. GoodRx Holdings, Inc.](https://www.ftc.gov/news-events/news/press-releases/2023/02/ftc-enforcement-action-bar-goodrx-sharing-consumers-sensitive-health-info-advertising) (February 2023) is a $1.5 million civil penalty. The FTC's complaint describes health information shared with advertising platforms through tracking pixels. GoodRx is not a game studio. The game-studio orders are the Epic figures in the children section.

## Product names

Before a product name is treated as available, search the registers for the countries where it will be offered. The public registers are [USPTO Trademark Search](https://tmsearch.uspto.gov/) and [EUIPO eSearch](https://euipo.europa.eu/eSearch/). Record the query, the date, and whether a live identical or close mark appeared in the relevant class. A hit is not an infringement finding. An empty result is not permission to use the name. This is a launch record, not a security vulnerability.

## Client secrets and provider spend

A provider secret in frontend source, a public environment variable, a built bundle, or a shipped mobile binary is the defect. Putting the key in the browser does not move it to safety. The client calls a server the user does not control, and that server holds the key. Handling is in [data-privacy.md](data-privacy.md). The mandatory check is `secrets`. [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) is the reference.

An AI key also needs a ceiling the provider enforces. OpenAI documents [spend limits](https://platform.openai.com/docs/guides/production-best-practices) for the organization or project. Anthropic documents a [monthly spend limit](https://docs.anthropic.com/en/api/rate-limits). A quota the client can omit is not that ceiling. Application-side limits are in [ai-security.md](ai-security.md). The mandatory check is `ai-permissions`. Unbounded model consumption is OWASP GenAI LLM10.

## Licenses of shipped code, fonts, and media

For each dependency, font, icon, image, and audio file that ships, record the license identifier from the package or the file.

[GPL-3.0 section 5](https://www.gnu.org/licenses/gpl-3.0.html) requires a modified GPL work that you convey to be licensed, as a whole, under GPL-3.0. Conveying means giving someone a copy. Running the program on a server, without giving users that copy, is not by itself conveying. [AGPL-3.0 section 13](https://www.gnu.org/licenses/agpl-3.0.html) adds a source offer for users who interact with the program over a network.

A font under the [SIL Open Font License](https://openfontlicense.org/) may be embedded, with the conditions in that license, including the ban on selling the font alone. A file downloaded from a font site may carry a different license. Music and stock images need a license that covers the actual use. A download with no license terms is unresolved.

Record the component, the license, whether the product distributes that component, and the obligation the license text states. Do not conclude that the application must be published as open source. A missing license for shipped media, or a copyleft component that is distributed with no source offer, is a finding. Dependency review stays in [supply-chain-security.md](supply-chain-security.md).
