from pathlib import Path

root=Path("yak_alimi_v21_work")
java_dir=root/"app/src/main/java/com/yakalimi/app"
store=java_dir/"SupportRewardStore.java"

store.write_text(r'''package com.yakalimi.app;

import android.content.Context;
import android.content.SharedPreferences;

public final class SupportRewardStore {
    private static final String PREFS = "yak_alimi_support_cards";
    private static final String KEY_COFFEE = "coffee_cards";
    private static final String KEY_MEAL = "meal_cards";

    private SupportRewardStore() {}

    public static void add(Context context, String productId) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (BuildConfig.SUPPORT_COFFEE_PRODUCT_ID.equals(productId)) {
            p.edit().putInt(KEY_COFFEE, p.getInt(KEY_COFFEE, 0) + 1).apply();
        } else if (BuildConfig.SUPPORT_MEAL_PRODUCT_ID.equals(productId)) {
            p.edit().putInt(KEY_MEAL, p.getInt(KEY_MEAL, 0) + 1).apply();
        }
    }

    public static int coffee(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getInt(KEY_COFFEE, 0);
    }

    public static int meal(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getInt(KEY_MEAL, 0);
    }

    public static int total(Context context) {
        return coffee(context) + meal(context);
    }
}
''',encoding="utf-8")

print("SupportRewardStore added")
