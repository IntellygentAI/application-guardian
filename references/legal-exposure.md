# Legal exposure

Compare the running product with the published rules below. This file does not decide that a statute applies, that a name is free to use, or that the product is lawful. Record a finding when the behaviour is present. Record NOT APPLICABLE, with the reason, when the product has none of that behaviour. A lawyer reviews the conclusion. An audit does not give one.

Ownership tests, secret handling, account deletion, and AI quotas already have mandatory checks. Use those IDs. The other items here are findings. An open high finding still blocks a GO.

## Notice matches the data flow

List every place personal data leaves the application: identity provider, database host, email, payments, error tracking, product analytics, advertising tags, session replay, AI provider, file storage, and support tools. Compare that list with the privacy notice.

[GDPR Article 13(1)(e)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) requires the recipients or categories of recipients. The [EDPB consent guidelines](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en) say the Article 13 and 14 information includes processors. A notice that names no recipient, while the code sends account data to several vendors, is a finding. A category is acceptable when a reader can tell which kind of company receives the data. A vendor that receives data and fits no stated category is a finding.

When the California Consumer Privacy Act applies, the notice at collection in [Civil Code section 1798.100](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1798.100) is the matching duty. Do not treat it as universal.

A product that collects personal data and has no notice is a finding. Where the GDPR applies, [Article 13](https://eur-lex.europa.eu/eli/reg/2016/679/oj) also requires the controller's identity and contact details, the purposes and legal basis, the retention period or the criteria used to set it, and the person's rights, including erasure and complaint to a supervisory authority. A page titled "privacy" that omits those items is the same finding as a missing page.

## Erasure

A delete control removes or irreversibly anonymises the private data the notice names, including files, search indexes, and copies held for product features. Setting a hidden flag while the row, object, or export remains readable is a failure. [GDPR Article 17](https://eur-lex.europa.eu/eli/reg/2016/679/oj) requires erasure in the cases it lists, and Article 17(2) requires the controller to inform recipients unless that is impossible or disproportionate. Legal duties to keep a record, such as tax or a dispute, are exceptions: name the data that is kept and why.

Backups that cannot be edited immediately stay a residual risk, as in [data-privacy.md](data-privacy.md). The mandatory check is `account-deletion`.

People who cannot sign in still need a way to ask. A published form or address that reaches the same deletion path is that way. [GDPR Article 12(3)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) gives one month to act, extendable by two months when the request is complex, and the person must be told about an extension within the first month. Where the CCPA applies, [Civil Code section 1798.130](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1798.130) sets 45 days, extendable once by another 45. A mailbox that stores the request and does not delete, or name a lawful reason to keep the data, is a failure. Test it with a synthetic request in an authorised environment.

## Another person's data

A public client key, a logged-out browser, or one user's token is not a privacy control. With synthetic accounts, request another user's profile, messages, files, and invoices, including by calling the API directly. [OWASP API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) is the failure. A pass needs an executed request on the current commit. The method is in [security-testing.md](security-testing.md). The mandatory check is `ownership`.

## Data minimisation

[GDPR Article 5(1)(c)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) limits personal data to what is adequate, relevant, and necessary. A field the product collects and no feature reads is a finding. Government ID images, selfies processed to identify a person, and precise location are the high-severity cases. [Article 9](https://eur-lex.europa.eu/eli/reg/2016/679/oj) covers biometric data used for unique identification. Removing the field from the form leaves a finding while old rows, buckets, or logs still store it.

## Children

Keep the US rule and the European rule apart.

The [COPPA Rule, 16 CFR Part 312](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312), applies to an operator of a site or service directed to children under 13, and to an operator with actual knowledge that it collects personal information from a child under 13. The [April 2025 amendments](https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm) took effect on 23 June 2025, and most new duties had a compliance date of 22 April 2026. Those duties include a separate verifiable parental consent before children's personal information is disclosed to third parties for targeted advertising, and a ban on conditioning access on that consent. Behavioural advertising to children is off unless a parent has given that separate consent.

[GDPR Article 8](https://eur-lex.europa.eu/eli/reg/2016/679/oj) applies when consent is the lawful basis for an information-society service offered directly to a child. The regulation's age is 16. A Member State may set a lower age, not below 13. The UK age is 13. Do not copy the US age into a European product.

If a child under the applicable age can open an account, check three things: advertising and analytics do not share that child's data before the required parental consent; the consent step is the verifiable method the rule requires, which a self-reported "I am a parent" checkbox or an age the child picks is not; and a parent can review and delete the data. If the product is a general-audience tool with no age signal, record whether under-13 signup is possible. Do not label every such product a COPPA violation.

The public enforcement figure for a game studio is the FTC's December 2022 Epic Games order: a [$275 million COPPA civil penalty](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-275-million-coppa-violations). A separate Epic order required [$245 million in refunds](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-than-half-billion-over-ftc-allegations) for billing practices. Do not replace either figure with a round number from a video.

## Cancellation

When a charge starts as a trial or renews until the customer stops it, [15 USC 8403](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title15-section8403&num=0&edition=prelim) requires the material terms before billing data is taken, express informed consent before the charge, and simple mechanisms to stop recurring charges. The FTC's 2024 Negative Option Rule was vacated by the Eighth Circuit on 8 July 2025 in Custom Communications, Inc. v. FTC, No. 24-3137. Audit against ROSCA and the state automatic-renewal statute that applies. One state example, when the customer is in California and signed up online, is [Business and Professions Code section 17602](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=BPC&sectionNum=17602): cancellation is online as well.

The same class of user who can subscribe can cancel without a phone call, a chat queue, or a buried form. Cancellation stops the next charge. The entitlement ends on the schedule the product states. A cancel path that is harder than the subscribe path is a finding. Payment mechanics stay in [payment-security.md](payment-security.md).

## Terms, price, and refunds

A file named "terms" is not the duty. Where the [Consumer Rights Directive](https://eur-lex.europa.eu/eli/dir/2011/83/oj) applies, Article 6 requires the pre-contract information before the consumer is bound: who the trader is, the main characteristics, the total price, the duration, and the conditions for withdrawal. Article 6(1)(e) includes taxes and any other cost that can be calculated. A fee that first appears after the customer has entered payment details is a finding for those contracts.

Article 9 gives 14 days to withdraw from a distance contract without giving a reason, except the cases in Article 16. Digital content not supplied on a tangible medium loses that right only after performance has begun with the consumer's prior express consent and acknowledgement. A refund page that says "no refunds" over a right the directive still gives is a finding. Say which Article 16 exception, if any, the product actually meets.

The FTC [Rule on Unfair or Deceptive Fees, 16 CFR Part 464](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-464), covers live-event tickets and short-term lodging. It requires the total price, more prominent than other pricing, and a disclosure of excluded mandatory fees before payment. Do not apply that rule to ordinary software. For other US offers, a price that omits a mandatory fee can still be a deceptive display; record it as such and do not cite Part 464.

## Business identity

Where the [e-Commerce Directive](https://eur-lex.europa.eu/eli/dir/2000/31/oj) applies, Article 5 requires the service provider's name, geographic address, and email, plus the trade register and registration number where the provider is registered, and the VAT number when applicable. The same identity belongs in the privacy notice under GDPR Article 13. A contact form with no legal name and no postal address is a finding for those services.

Commercial email that is covered by [15 USC 7704](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title15-section7704&num=0&edition=prelim) includes the sender's valid physical postal address. The message also includes a working opt-out. [16 CFR 316.5](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-316/section-316.5) forbids a fee, extra personal data, or any step beyond a reply or a single web page. The statute requires the opt-out to be honoured within 10 business days. A marketing email with no unsubscribe link is a finding. UK PECR marketing email still needs consent or the soft opt-in, plus a simple way to refuse further messages. Consent-based marketing also follows GDPR Article 7(3): withdrawal as easy as the original consent.

## Tracking before agreement

An analytics tag, advertising pixel, or session replay that identifies a person or sends personal data to a third party waits for the notice and, where the law requires it, for consent. The [ICO's PECR cookie guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/) requires consent before non-essential cookies, including analytics. Strictly necessary cookies are the narrow exception. A banner that appears after the request has already been sent is not consent.

The cookie information can live in the privacy notice or in a separate cookie notice. It names each non-essential cookie or SDK, its purpose, and who receives the data. A banner is the choice, not the notice.

The [EDPB cookie-banner taskforce report](https://www.edpb.europa.eu/system/files/documents/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf) treats pre-ticked boxes as invalid and expects a refusal that does not take more steps than acceptance. [Planet49 (C-673/17)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A62017CJ0673) holds that a pre-ticked checkbox is not consent, and that agreeing to a promotion is not consent to analytics cookies. Withdrawal is as easy as the original consent, under GDPR Article 7(3). An Accept-only banner, a reject control buried in a second screen, or a script tag for analytics in the initial HTML is a finding where this consent rule applies.

On every form, consent for a further purpose is its own unticked control, with that purpose written beside it. Account creation, payment, and a marketing list are separate decisions. A single "I agree to the terms and to emails" box is a finding where consent is the lawful basis for the emails.

For each third-party SDK, record the vendor, the data it reads, and whether it loads before the choice. Compare that list with the notice. A SDK that is absent from the notice, or that runs before a required consent, is a finding. Strictly necessary infrastructure, such as the host that serves the page, is the exception and is named as such.

A claim that a game studio paid $1.4 million for loading analytics before consent does not match the FTC orders checked for this file. [United States v. GoodRx Holdings, Inc.](https://www.ftc.gov/news-events/news/press-releases/2023/02/ftc-enforcement-action-bar-goodrx-sharing-consumers-sensitive-health-info-advertising) (February 2023) is a $1.5 million civil penalty. The FTC's complaint describes health information shared with advertising platforms through tracking pixels. GoodRx is not a game studio. The game-studio orders are the Epic figures in the children section.

## Interface tricks, reviews, and claims

[EDPB Guidelines 03/2022](https://www.edpb.europa.eu/documents/guideline/guidelines-032022-on-deceptive-design-patterns-in-social-media-platform_en) describe deceptive patterns in social-media interfaces. Use the same GDPR duties, fairness in Article 5 and consent in Article 7, when another product uses the same trick: obstructing a refusal, confirming a choice the person did not make, or making withdrawal harder than consent. [Digital Services Act Article 25](https://eur-lex.europa.eu/eli/reg/2022/2065/oj) forbids manipulative interface design for online platforms as that regulation defines them. Article 25(2) leaves practices already covered by the Unfair Commercial Practices Directive or the GDPR to those laws. Do not apply Article 25 to a site that is not an online platform.

The FTC [Rule on the Use of Consumer Reviews and Testimonials, 16 CFR Part 465](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465), prohibits fake reviews, reviews bought for a particular sentiment, insider reviews that hide the relationship, and suppression of genuine negative reviews. A testimonial hardcoded in the interface, attributed to a person who did not use the product, is the same defect. The EU [Unfair Commercial Practices Directive](https://eur-lex.europa.eu/eli/dir/2005/29/oj), as amended by Directive 2019/2161, blacklists fake reviews and hosting reviews presented as consumer reviews without reasonable checks.

A concrete performance, income, or health claim needs the evidence the page asserts. Record the sentence and whether the repository contains that evidence. Obvious puffery is not a finding. A missing study for a measurable claim is. Do not invent the substantiation.

Alternative text, contrast, and keyboard access are tested in [accessibility.md](accessibility.md) against WCAG 2.2 AA. Do not close them from this file.

## Product names

Before a product name is treated as available, search the registers for the countries where it will be offered. The public registers are [USPTO Trademark Search](https://tmsearch.uspto.gov/) and [EUIPO eSearch](https://euipo.europa.eu/eSearch/). Record the query, the date, and whether a live identical or close mark appeared in the relevant class. A hit is not an infringement finding. An empty result is not permission to use the name. This is a launch record, not a security vulnerability.

## Client secrets and provider spend

A provider secret in frontend source, a public environment variable, a built bundle, or a shipped mobile binary is the defect. Putting the key in the browser does not move it to safety. The client calls a server the user does not control, and that server holds the key. Handling is in [data-privacy.md](data-privacy.md). The mandatory check is `secrets`. [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) is the reference.

An AI key also needs a ceiling the provider enforces. OpenAI documents [spend limits](https://platform.openai.com/docs/guides/production-best-practices) for the organization or project. Anthropic documents a [monthly spend limit](https://docs.anthropic.com/en/api/rate-limits). A quota the client can omit is not that ceiling. Application-side limits are in [ai-security.md](ai-security.md). The mandatory check is `ai-permissions`. Unbounded model consumption is OWASP GenAI LLM10.

## Licenses of shipped code, fonts, and media

For each dependency, font, icon, image, and audio file that ships, record the license identifier from the package or the file.

[GPL-3.0 section 5](https://www.gnu.org/licenses/gpl-3.0.html) requires a modified GPL work that you convey to be licensed, as a whole, under GPL-3.0. Conveying means giving someone a copy. Running the program on a server, without giving users that copy, is not by itself conveying. [AGPL-3.0 section 13](https://www.gnu.org/licenses/agpl-3.0.html) adds a source offer for users who interact with the program over a network.

A font under the [SIL Open Font License](https://openfontlicense.org/) may be embedded, with the conditions in that license, including the ban on selling the font alone. A file downloaded from a font site may carry a different license. Music and stock images need a license that covers the actual use, including a file placed in the bundle from a stock site. A download with no license terms is unresolved. "Free to view on a stock site" is not a license to ship the file.

Record the component, the license, whether the product distributes that component, and the obligation the license text states. Do not conclude that the application must be published as open source. A missing license for shipped media, or a copyleft component that is distributed with no source offer, is a finding. Dependency review stays in [supply-chain-security.md](supply-chain-security.md).
