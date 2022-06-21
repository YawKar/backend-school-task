package com.yawkar.backend.serializer;

import com.google.gson.*;
import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.utils.GsonUtils;
import org.springframework.stereotype.Component;

import java.lang.reflect.Type;
import java.time.format.DateTimeFormatter;

@Component
public class ShopUnitSerializer implements JsonSerializer<ShopUnitEntity> {

    @Override
    public JsonElement serialize(ShopUnitEntity shopUnitEntity, Type type, JsonSerializationContext jsonSerializationContext) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("id", shopUnitEntity.getUuid().toString());
        jsonObject.addProperty("name", shopUnitEntity.getName());
        jsonObject.addProperty("type", shopUnitEntity.getType().toString());
        if (shopUnitEntity.getParentUuid() == null) {
            jsonObject.add("parentId", JsonNull.INSTANCE);
        } else {
            jsonObject.addProperty("parentId", shopUnitEntity.getParentUuid().toString());
        }
        jsonObject.addProperty("date", shopUnitEntity.getLastUpdateDateTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")));
        if (shopUnitEntity.getSize() > 0) {
            jsonObject.addProperty("price", shopUnitEntity.getPrice() / shopUnitEntity.getSize());
        } else {
            jsonObject.addProperty("price", shopUnitEntity.getPrice());
        }
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            jsonObject.add("children", JsonNull.INSTANCE);
        } else {
            JsonArray childrenArray = new JsonArray();
            for (var child : shopUnitEntity.getChildren()) {
                childrenArray.add(GsonUtils.gson.toJsonTree(child));
            }
            jsonObject.add("children", childrenArray);
        }
        return jsonObject;
    }
}
