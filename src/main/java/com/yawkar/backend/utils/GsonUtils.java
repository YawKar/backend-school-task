package com.yawkar.backend.utils;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.serializer.ShopUnitSerializer;

public class GsonUtils {
    public static final Gson gson = new GsonBuilder()
            .registerTypeAdapter(ShopUnitEntity.class, new ShopUnitSerializer())
            .setPrettyPrinting()
            .serializeNulls()
            .create();
}
