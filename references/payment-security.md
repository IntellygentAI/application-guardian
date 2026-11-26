# Payment and business-logic security

Treat every client-supplied financial value as untrusted. Use the provider's sandbox or an authorised test environment. Do not create real charges.

If the application takes no payment, coupons, credits, or entitlements, mark this domain NOT APPLICABLE.

## Price and quantity manipulation

Test changing the displayed price, submitting a price other than the catalogue price, ordering negative one items, submitting a quantity of zero, submitting a fractional quantity where integers are required, exceeding purchase limits, changing currency, shipping, or tax, applying an expired discount, and discounting an ineligible product.

Prices come from trusted server-side records. Discounts are validated on the server. Quantities, currency, tax, and shipping are verified. Money math does not use unsafe floating-point rounding. The server computes the final total. The stored order matches the verified payment.

## Payment verification

For Stripe or any other provider, test:

- Opening the success page without a payment
- Cancellation, failure, and delayed payment
- Duplicate notifications, the wrong amount, and the wrong currency
- An order reference that belongs to another user
- An invalid webhook signature, repeated deliveries, and out-of-order events
- Partial refunds, full refunds, chargebacks, and subscription cancellation

Payment status comes from the provider, not from the browser. Webhook signatures are verified. Duplicate events are safe. Fulfilment is idempotent. Order ownership is validated. Amount and currency match. Entitlements are granted only after the required payment state. Failures and refunds follow the business rules.

A success message or redirect is not proof of payment.

Webhook replay, timestamp tolerance, and signing-secret rotation are specified in [api-security.md](api-security.md). Stripe's handler shape is specified in [framework-specific/stripe.md](framework-specific/stripe.md) when Stripe is present.

## Coupons, credits, and rewards

Test repeated redemption of the same coupon, 100 redemptions in a bounded local concurrency test, simultaneous redemption from two devices, an expired coupon, a coupon for another account, a consumed reward, repeated referral rewards, self-referral, reuse of a free trial, and a refund that would keep an incompatible reward.

Redemption is atomic. Uniqueness constraints exist. Per-user and global limits and expiry are enforced. Eligibility is checked. The transaction history stays consistent. Concurrent requests must not duplicate a redemption.

## Subscriptions and entitlements

Test a free account calling a premium feature, a client-side subscription flag, access after expiry, cancellation during use, downgrade, quota bypass, multiple sessions, and direct calls to premium APIs.

Subscriptions, entitlements, quotas, and usage limits are enforced on the backend. Hiding a control in the interface does not protect a paid feature.
