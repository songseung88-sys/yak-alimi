from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/BillingManager.java")
s=p.read_text(encoding="utf-8")
old='''    private void consumeSupportPurchase(Purchase p, boolean notifyUser) {
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
new='''    private void consumeSupportPurchase(Purchase p, boolean notifyUser) {
        String rewardProductId = null;
        if (p.getProducts().contains(BuildConfig.SUPPORT_COFFEE_PRODUCT_ID))
            rewardProductId = BuildConfig.SUPPORT_COFFEE_PRODUCT_ID;
        else if (p.getProducts().contains(BuildConfig.SUPPORT_MEAL_PRODUCT_ID))
            rewardProductId = BuildConfig.SUPPORT_MEAL_PRODUCT_ID;
        final String rewardId = rewardProductId;

        ConsumeParams params = ConsumeParams.newBuilder()
                .setPurchaseToken(p.getPurchaseToken()).build();
        client.consumeAsync(params, (result, token) -> {
            if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                if (rewardId != null) SupportRewardStore.add(activity, rewardId);
                if (notifyUser && listener != null)
                    listener.onBillingMessage("support_card_added");
            } else if (notifyUser && listener != null) {
                listener.onBillingMessage("billing_unavailable");
            }
        });
    }
'''
if old not in s:
    raise SystemExit("support consume block missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("Support purchases now grant support cards")
