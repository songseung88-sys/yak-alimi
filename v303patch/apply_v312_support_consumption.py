from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/BillingManager.java")
s=p.read_text(encoding="utf-8")
if "import com.android.billingclient.api.ConsumeParams;" not in s:
    s=s.replace("import com.android.billingclient.api.BillingResult;\n","import com.android.billingclient.api.BillingResult;\nimport com.android.billingclient.api.ConsumeParams;\n",1)

old='''            boolean owned = false;
            for (Purchase purchase : purchases) {
                if (purchase.getProducts().contains(BuildConfig.PREMIUM_PRODUCT_ID)
                        && purchase.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                    owned = true;
                    acknowledgeIfNeeded(purchase);
                }
            }
'''
new='''            boolean owned = false;
            for (Purchase purchase : purchases) {
                if (purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                if (purchase.getProducts().contains(BuildConfig.PREMIUM_PRODUCT_ID)) {
                    owned = true;
                    acknowledgeIfNeeded(purchase);
                } else if (containsSupportProduct(purchase)) {
                    consumeSupportPurchase(purchase, false);
                }
            }
'''
if old not in s: raise SystemExit("refresh loop missing")
s=s.replace(old,new,1)

old2='''            for (Purchase p : purchases) {
                if (p.getProducts().contains(BuildConfig.PREMIUM_PRODUCT_ID)
                        && p.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                    setPremium(activity, true);
                    acknowledgeIfNeeded(p);
                    if (listener != null) listener.onPremiumChanged(true);
                }
            }
'''
new2='''            for (Purchase p : purchases) {
                if (p.getPurchaseState() != Purchase.PurchaseState.PURCHASED) continue;
                if (p.getProducts().contains(BuildConfig.PREMIUM_PRODUCT_ID)) {
                    setPremium(activity, true);
                    acknowledgeIfNeeded(p);
                    if (listener != null) listener.onPremiumChanged(true);
                } else if (containsSupportProduct(p)) {
                    consumeSupportPurchase(p, true);
                }
            }
'''
if old2 not in s: raise SystemExit("updated loop missing")
s=s.replace(old2,new2,1)

anchor='''    private void acknowledgeIfNeeded(Purchase p) {
'''
helpers='''    private boolean containsSupportProduct(Purchase p) {
        return p.getProducts().contains(BuildConfig.SUPPORT_COFFEE_PRODUCT_ID)
                || p.getProducts().contains(BuildConfig.SUPPORT_MEAL_PRODUCT_ID);
    }

    private void consumeSupportPurchase(Purchase p, boolean notifyUser) {
        ConsumeParams params = ConsumeParams.newBuilder()
                .setPurchaseToken(p.getPurchaseToken()).build();
        client.consumeAsync(params, (result, token) -> {
            if (!notifyUser || listener == null) return;
            if (result.getResponseCode() == BillingClient.BillingResponseCode.OK)
                listener.onBillingMessage("support_thanks");
            else
                listener.onBillingMessage("billing_unavailable");
        });
    }

'''
if anchor not in s: raise SystemExit("ack anchor missing")
s=s.replace(anchor,helpers+anchor,1)
p.write_text(s,encoding="utf-8")
print("v312 support consumption applied")
