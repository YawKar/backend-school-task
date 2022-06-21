package com.yawkar.backend.utils;

import com.yawkar.backend.entity.ShopUnitEntity;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class Imports {

    private List<ShopUnitEntity> items;

    private LocalDateTime updateTime;

    public Imports() {
        this.items = new ArrayList<>();
    }

    public List<ShopUnitEntity> getItems() {
        return items;
    }

    public void setItems(List<ShopUnitEntity> items) {
        this.items = items;
    }

    public LocalDateTime getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }
}
