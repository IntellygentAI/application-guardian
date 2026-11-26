// Synthetic fixture. The success page grants premium access with no provider check.
export function SuccessPage() {
  unlockPremium();
  return "Payment complete";
}
