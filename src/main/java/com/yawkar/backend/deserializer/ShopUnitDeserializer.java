package com.yawkar.backend.deserializer;

import com.google.gson.*;
import com.yawkar.backend.entity.ShopUnitEntity;

import java.lang.reflect.Type;
import java.util.UUID;

public class ShopUnitDeserializer implements JsonDeserializer<ShopUnitEntity> {

    @Override
    public ShopUnitEntity deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        JsonObject shopUnitNode = jsonElement.getAsJsonObject();
        ShopUnitEntity shopUnitEntity = new ShopUnitEntity();
        shopUnitEntity.setName(shopUnitNode.get("name").getAsString());
        shopUnitEntity.setUuid(UUID.fromString(shopUnitNode.get("id").getAsString()));
        shopUnitEntity.setType(ShopUnitEntity.ShopUnitType.valueOf(shopUnitNode.get("type").getAsString()));
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            shopUnitEntity.setSize(1);
        } else {
            shopUnitEntity.setSize(0);
        }
        if (shopUnitNode.has("price")) {
            if (shopUnitNode.get("price").isJsonNull()) {
                shopUnitEntity.setPrice(null);
            } else {
                shopUnitEntity.setPrice(shopUnitNode.get("price").getAsInt());
            }
        } else {
            shopUnitEntity.setPrice(null);
        }
        if (shopUnitNode.has("parentId")) {
            if (shopUnitNode.get("parentId").isJsonNull()) {
                shopUnitEntity.setParentUuid(null);
            } else {
                shopUnitEntity.setParentUuid(UUID.fromString(shopUnitNode.get("parentId").getAsString()));
            }
        } else {
            shopUnitEntity.setParentUuid(null);
        }
        return shopUnitEntity;
    }
}
