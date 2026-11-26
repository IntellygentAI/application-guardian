// Synthetic fixture. The server charges the client-supplied amount.
export async function POST(request: Request) {
  const body = await request.json();
  return stripe.paymentIntents.create({
    amount: body.amount,
    currency: body.currency,
  });
}
