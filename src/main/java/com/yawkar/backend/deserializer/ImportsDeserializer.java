package com.yawkar.backend.deserializer;

import com.google.gson.*;
import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.utils.GsonUtils;
import com.yawkar.backend.utils.Imports;

import java.lang.reflect.Type;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class ImportsDeserializer implements JsonDeserializer<Imports> {
    @Override
    public Imports deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        JsonObject root = jsonElement.getAsJsonObject();
        Imports imports = new Imports();
        imports.setUpdateTime(LocalDateTime.parse(root.get("updateDate").getAsString(), DateTimeFormatter.ISO_DATE_TIME));
        List<ShopUnitEntity> shopUnits = new ArrayList<>();
        for (JsonElement shopUnitNode : root.get("items").getAsJsonArray()) {
            shopUnits.add(GsonUtils.gson.fromJson(shopUnitNode, ShopUnitEntity.class));
        }
        imports.setItems(shopUnits);
        return imports;
    }
}
