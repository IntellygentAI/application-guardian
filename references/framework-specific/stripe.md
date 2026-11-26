# Stripe

Payment behaviour is specified in [payment-security.md](../payment-security.md).

- Checkout Sessions and PaymentIntents are created on the server from catalogue prices. The client does not send the amount the server should charge.
- The success URL is a page. Fulfilment happens in a webhook handler after `constructEvent` verifies the signature.
- The webhook secret is a server environment variable. A missing or skipped signature check is a high finding.
- The handler stores the event ID and ignores a duplicate delivery.
- Amount and currency on the event are compared with the order. A mismatch does not grant the entitlement.
- Refunds and cancellations revoke the entitlement the business rules require.
- Test with the provider's test keys. Do not create a live charge. Do not print the secret key.
