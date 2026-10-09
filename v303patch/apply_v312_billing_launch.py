from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/BillingManager.java")
s=p.read_text(encoding="utf-8")
a=s.index("    public String getPremiumFormattedPrice() {")
b=s.index("    @Override public void onPurchasesUpdated",a)
new='''    public String getPremiumFormattedPrice() {
        return getFormattedPrice(BuildConfig.PREMIUM_PRODUCT_ID);
    }

    public String getSupportFormattedPrice(String productId) {
        return getFormattedPrice(productId);
    }

    private String getFormattedPrice(String productId) {
        ProductDetails.OneTimePurchaseOfferDetails offer = firstOffer(detailsFor(productId));
        return offer == null ? null : offer.getFormattedPrice();
    }

    public void purchasePremium() {
        launchOneTimePurchase(BuildConfig.PREMIUM_PRODUCT_ID);
    }

    public void purchaseSupport(String productId) {
        if (!BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(productId)
                && !BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(productId)) return;
        launchOneTimePurchase(productId);
    }

    private void launchOneTimePurchase(String productId) {
        if (!client.isReady()) {
            start();
            if (listener != null) listener.onBillingMessage("billing_unavailable");
            return;
        }
        ProductDetails details = detailsFor(productId);
        ProductDetails.OneTimePurchaseOfferDetails offer = firstOffer(details);
        if (details == null || offer == null) {
            queryProductDetails();
            if (listener != null) listener.onBillingMessage("billing_play_required");
            return;
        }
        BillingFlowParams.ProductDetailsParams pd = BillingFlowParams.ProductDetailsParams
                .newBuilder()
                .setProductDetails(details)
                .setOfferToken(offer.getOfferToken())
                .build();
        BillingFlowParams params = BillingFlowParams.newBuilder()
                .setProductDetailsParamsList(Collections.singletonList(pd))
                .build();
        BillingResult result = client.launchBillingFlow(activity, params);
        if (result.getResponseCode() != BillingClient.BillingResponseCode.OK && listener != null)
            listener.onBillingMessage("billing_unavailable");
    }

'''
s=s[:a]+new+s[b:]
p.write_text(s,encoding="utf-8")
print("v312 billing launch applied")
