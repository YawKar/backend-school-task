package com.yawkar.backend.utils;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.yawkar.backend.entity.ShopUnitEntity;

import java.util.List;

public class SalesUtils {

    public static JsonElement serializeOffers(List<ShopUnitEntity> offers) {
        JsonObject jsonObject = new JsonObject();
        JsonArray items = new JsonArray();
        for (var offer : offers) {
            items.add(GsonUtils.gson.toJsonTree(offer));
        }
        jsonObject.add("items", items);
        return jsonObject;
    }
}
