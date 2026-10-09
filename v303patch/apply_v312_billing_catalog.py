from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/BillingManager.java")
s=p.read_text(encoding="utf-8")
if "import java.util.Arrays;" not in s:
    s=s.replace("import java.util.Collections;\n","import java.util.Arrays;\nimport java.util.Collections;\n",1)
s=s.replace("    private ProductDetails premiumDetails;\n","    private ProductDetails premiumDetails;\n    private ProductDetails coffeeDetails;\n    private ProductDetails mealDetails;\n",1)
s=s.replace("queryPremiumDetails();","queryProductDetails();")
a=s.index("    private void queryPremiumDetails() {")
b=s.index("    public String getPremiumFormattedPrice()",a)
new='''    private void queryProductDetails() {
        if (!client.isReady()) return;
        QueryProductDetailsParams.Product premium = product(BuildConfig.PREMIUM_PRODUCT_ID);
        QueryProductDetailsParams.Product coffee = product(BuildConfig.SUPPORT_COFFEE_PRODUCT_ID);
        QueryProductDetailsParams.Product meal = product(BuildConfig.SUPPORT_MEAL_PRODUCT_ID);
        QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
                .setProductList(Arrays.asList(premium, coffee, meal)).build();
        client.queryProductDetailsAsync(params, (result, queryResult) -> {
            if (result.getResponseCode() != BillingClient.BillingResponseCode.OK) return;
            List<ProductDetails> list = queryResult.getProductDetailsList();
            if (list == null) return;
            for (ProductDetails d : list) {
                if (BuildConfig.PREMIUM_PRODUCT_ID.equals(d.getProductId())) premiumDetails = d;
                else if (BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(d.getProductId())) coffeeDetails = d;
                else if (BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(d.getProductId())) mealDetails = d;
            }
        });
    }

    private QueryProductDetailsParams.Product product(String id) {
        return QueryProductDetailsParams.Product.newBuilder()
                .setProductId(id).setProductType(BillingClient.ProductType.INAPP).build();
    }

    private ProductDetails detailsFor(String id) {
        if (BuildConfig.PREMIUM_PRODUCT_ID.equals(id)) return premiumDetails;
        if (BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(id)) return coffeeDetails;
        if (BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(id)) return mealDetails;
        return null;
    }

    private ProductDetails.OneTimePurchaseOfferDetails firstOffer(ProductDetails d) {
        if (d == null) return null;
        List<ProductDetails.OneTimePurchaseOfferDetails> offers = d.getOneTimePurchaseOfferDetailsList();
        if (offers != null && !offers.isEmpty()) return offers.get(0);
        return d.getOneTimePurchaseOfferDetails();
    }

'''
s=s[:a]+new+s[b:]
p.write_text(s,encoding="utf-8")
print("v312 billing catalog applied")
