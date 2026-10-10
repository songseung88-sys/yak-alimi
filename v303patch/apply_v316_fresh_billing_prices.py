from pathlib import Path

root=Path("yak_alimi_v21_work")
build_file=root/"app/build.gradle"
billing_file=root/"app/src/main/java/com/yakalimi/app/BillingManager.java"
main_file=root/"app/src/main/java/com/yakalimi/app/MainActivity.java"

# Keep Play product IDs and purchase-option IDs as separate constants.
build=build_file.read_text(encoding="utf-8")
anchor='''        buildConfigField "String", "SUPPORT_MEAL_PRODUCT_ID", "\\"support_meal_10000\\""
'''
if anchor not in build:
    raise SystemExit("support product ID anchor missing")
insert=anchor+'''        buildConfigField "String", "PREMIUM_PURCHASE_OPTION_ID", "\\"premium-lifetime\\""
        buildConfigField "String", "SUPPORT_COFFEE_PURCHASE_OPTION_ID", "\\"support-coffee-5000\\""
        buildConfigField "String", "SUPPORT_MEAL_PURCHASE_OPTION_ID", "\\"support-meal-10000\\""
'''
if "PREMIUM_PURCHASE_OPTION_ID" not in build:
    build=build.replace(anchor,insert,1)
build_file.write_text(build,encoding="utf-8")

s=billing_file.read_text(encoding="utf-8")

# Queue one catalog refresh callback if Billing is still connecting.
field_anchor='''    private ProductDetails mealDetails;
'''
if field_anchor not in s:
    raise SystemExit("BillingManager field anchor missing")
if "pendingProductDetailsCallback" not in s:
    s=s.replace(field_anchor,field_anchor+"    private Runnable pendingProductDetailsCallback;\n",1)

# Make start() deliver a pending fresh-catalog callback after Billing connects.
old_ready='''        if (client.isReady()) {
            refreshPurchases();
            queryProductDetails();
            return;
        }
'''
new_ready='''        if (client.isReady()) {
            refreshPurchases();
            Runnable pending = pendingProductDetailsCallback;
            pendingProductDetailsCallback = null;
            queryProductDetails(pending);
            return;
        }
'''
if old_ready not in s:
    raise SystemExit("BillingManager ready block missing")
s=s.replace(old_ready,new_ready,1)

old_setup='''                if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    refreshPurchases();
                    queryProductDetails();
                }
'''
new_setup='''                if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    refreshPurchases();
                    Runnable pending = pendingProductDetailsCallback;
                    pendingProductDetailsCallback = null;
                    queryProductDetails(pending);
                } else {
                    Runnable pending = pendingProductDetailsCallback;
                    pendingProductDetailsCallback = null;
                    runProductDetailsCallback(pending);
                }
'''
if old_setup not in s:
    raise SystemExit("BillingManager setup block missing")
s=s.replace(old_setup,new_setup,1)

# Replace cached-only catalog querying with explicit fresh query + completion callback.
start=s.find("    private void queryProductDetails() {")
end=s.find("    private QueryProductDetailsParams.Product product(String id) {",start)
if start<0 or end<0:
    raise SystemExit("queryProductDetails section missing")
new_query='''    private void queryProductDetails() {
        queryProductDetails(null);
    }

    public void refreshProductDetails(Runnable onComplete) {
        if (client.isReady()) {
            queryProductDetails(onComplete);
            return;
        }
        pendingProductDetailsCallback = onComplete;
        start();
    }

    private void queryProductDetails(Runnable onComplete) {
        if (!client.isReady()) {
            pendingProductDetailsCallback = onComplete;
            return;
        }
        QueryProductDetailsParams.Product premium = product(BuildConfig.PREMIUM_PRODUCT_ID);
        QueryProductDetailsParams.Product coffee = product(BuildConfig.SUPPORT_COFFEE_PRODUCT_ID);
        QueryProductDetailsParams.Product meal = product(BuildConfig.SUPPORT_MEAL_PRODUCT_ID);
        QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
                .setProductList(Arrays.asList(premium, coffee, meal)).build();
        client.queryProductDetailsAsync(params, (result, queryResult) -> {
            if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                List<ProductDetails> list = queryResult.getProductDetailsList();
                if (list != null) {
                    for (ProductDetails d : list) {
                        if (BuildConfig.PREMIUM_PRODUCT_ID.equals(d.getProductId())) premiumDetails = d;
                        else if (BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(d.getProductId())) coffeeDetails = d;
                        else if (BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(d.getProductId())) mealDetails = d;
                    }
                }
            }
            runProductDetailsCallback(onComplete);
        });
    }

    private void runProductDetailsCallback(Runnable callback) {
        if (callback != null) activity.runOnUiThread(callback);
    }

'''
s=s[:start]+new_query+s[end:]

# Select the exact purchase option rather than assuming the first returned offer.
start=s.find("    private ProductDetails.OneTimePurchaseOfferDetails firstOffer(ProductDetails d) {")
end=s.find("    public String getPremiumFormattedPrice()",start)
if start<0 or end<0:
    raise SystemExit("firstOffer section missing")
offer_block='''    private String purchaseOptionIdFor(String productId) {
        if (BuildConfig.PREMIUM_PRODUCT_ID.equals(productId))
            return BuildConfig.PREMIUM_PURCHASE_OPTION_ID;
        if (BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(productId))
            return BuildConfig.SUPPORT_COFFEE_PURCHASE_OPTION_ID;
        if (BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(productId))
            return BuildConfig.SUPPORT_MEAL_PURCHASE_OPTION_ID;
        return null;
    }

    private ProductDetails.OneTimePurchaseOfferDetails offerFor(String productId, ProductDetails d) {
        if (d == null) return null;
        List<ProductDetails.OneTimePurchaseOfferDetails> offers = d.getOneTimePurchaseOfferDetailsList();
        String wanted = purchaseOptionIdFor(productId);
        if (offers != null && !offers.isEmpty()) {
            if (wanted != null) {
                for (ProductDetails.OneTimePurchaseOfferDetails offer : offers) {
                    if (wanted.equals(offer.getPurchaseOptionId())) return offer;
                }
            }
            return offers.get(0);
        }
        return d.getOneTimePurchaseOfferDetails();
    }

'''
s=s[:start]+offer_block+s[end:]

s=s.replace(
'''        ProductDetails.OneTimePurchaseOfferDetails offer = firstOffer(detailsFor(productId));
''',
'''        ProductDetails.OneTimePurchaseOfferDetails offer = offerFor(productId, detailsFor(productId));
''',1)

s=s.replace(
'''        ProductDetails.OneTimePurchaseOfferDetails offer = firstOffer(details);
''',
'''        ProductDetails.OneTimePurchaseOfferDetails offer = offerFor(productId, details);
''',1)

# Always re-query the catalog immediately before starting a support purchase.
old_purchase='''    public void purchaseSupport(String productId) {
        if (!BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(productId)
                && !BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(productId)) return;
        launchOneTimePurchase(productId);
    }
'''
new_purchase='''    public void purchaseSupport(String productId) {
        if (!BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(productId)
                && !BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(productId)) return;
        refreshProductDetails(() -> launchOneTimePurchase(productId));
    }
'''
if old_purchase not in s:
    raise SystemExit("purchaseSupport block missing")
s=s.replace(old_purchase,new_purchase,1)

billing_file.write_text(s,encoding="utf-8")

# Refresh Play catalog immediately before drawing the support dialog.
m=main_file.read_text(encoding="utf-8")
old_sig='''    private void supportDeveloper(){
        LinearLayout box=new LinearLayout(this);
'''
new_sig='''    private void supportDeveloper(){
        billingManager.refreshProductDetails(this::showSupportDeveloperDialog);
    }

    private void showSupportDeveloperDialog(){
        LinearLayout box=new LinearLayout(this);
'''
if old_sig not in m:
    raise SystemExit("supportDeveloper UI anchor missing")
m=m.replace(old_sig,new_sig,1)
main_file.write_text(m,encoding="utf-8")

print("v3.0.16 fresh Play pricing + purchase-option selection patch applied")
