// Synthetic fixture. Two callers can redeem the same coupon.
export async function redeem(userId: string, code: string) {
  const coupon = await db.coupon.findUnique({ where: { code } });
  if (!coupon || coupon.redeemed) {
    throw new Error("unavailable");
  }
  await db.coupon.update({ where: { code }, data: { redeemed: true, userId } });
}
