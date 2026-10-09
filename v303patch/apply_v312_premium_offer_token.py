from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/BillingManager.java")
s=p.read_text(encoding="utf-8")
anchor='''    public String getPremiumFormattedPrice() {
'''
helper='''    private ProductDetails.OneTimePurchaseOfferDetails firstPremiumOffer() {
        if (premiumDetails == null) return null;
        List<ProductDetails.OneTimePurchaseOfferDetails> offers =
                premiumDetails.getOneTimePurchaseOfferDetailsList();
        if (offers != null && !offers.isEmpty()) return offers.get(0);
        return premiumDetails.getOneTimePurchaseOfferDetails();
    }

'''
if helper not in s:
    if anchor not in s: raise SystemExit("price anchor missing")
    s=s.replace(anchor,helper+anchor,1)

old='''    public void purchasePremium() {
        if (!client.isReady()) {
            start();
            if (listener != null) listener.onBillingMessage("billing_unavailable");
            return;
        }
        if (premiumDetails == null) {
            queryPremiumDetails();
            if (listener != null) listener.onBillingMessage("billing_play_required");
            return;
        }
        BillingFlowParams.ProductDetailsParams pd = BillingFlowParams.ProductDetailsParams
                .newBuilder().setProductDetails(premiumDetails).build();
        BillingFlowParams params = BillingFlowParams.newBuilder()
                .setProductDetailsParamsList(Collections.singletonList(pd))
                .build();
        BillingResult result = client.launchBillingFlow(activity, params);
        if (result.getResponseCode() != BillingClient.BillingResponseCode.OK && listener != null) {
            listener.onBillingMessage("billing_unavailable");
        }
    }
'''
new='''    public void purchasePremium() {
        if (!client.isReady()) {
            start();
            if (listener != null) listener.onBillingMessage("billing_unavailable");
            return;
        }
        ProductDetails.OneTimePurchaseOfferDetails offer = firstPremiumOffer();
        if (premiumDetails == null || offer == null) {
            queryPremiumDetails();
            if (listener != null) listener.onBillingMessage("billing_play_required");
            return;
        }
        BillingFlowParams.ProductDetailsParams pd = BillingFlowParams.ProductDetailsParams
                .newBuilder()
                .setProductDetails(premiumDetails)
                .setOfferToken(offer.getOfferToken())
                .build();
        BillingFlowParams params = BillingFlowParams.newBuilder()
                .setProductDetailsParamsList(Collections.singletonList(pd))
                .build();
        BillingResult result = client.launchBillingFlow(activity, params);
        if (result.getResponseCode() != BillingClient.BillingResponseCode.OK && listener != null) {
            listener.onBillingMessage("billing_unavailable");
        }
    }
'''
if old not in s: raise SystemExit("purchase block missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("v312 premium offer token applied")
