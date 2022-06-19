package com.yawkar.backend.entity;

import org.hibernate.annotations.Type;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "shopunits")
public class ShopUnitEntity {

    public enum ShopUnitType {
        OFFER,
        CATEGORY
    }

    @Id
    @Column(name = "uuid")
    @Type(type="uuid-char")
    private UUID uuid;

    @Column(name = "parent_uuid")
    private UUID parentUuid;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "price")
    private Integer price;

    @Column(name = "last_update")
    private LocalDateTime lastUpdateDateTime;

    @Column(name = "type")
    private ShopUnitType type;

    public List<ShopUnitEntity> getChildren() {
        return children;
    }

    public void setChildren(List<ShopUnitEntity> children) {
        this.children = children;
    }

    @OneToMany
    private List<ShopUnitEntity> children;

    public UUID getUuid() {
        return uuid;
    }

    public void setUuid(UUID uuid) {
        this.uuid = uuid;
    }

    public UUID getParentUuid() {
        return parentUuid;
    }

    public void setParentUuid(UUID parentUuid) {
        this.parentUuid = parentUuid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getPrice() {
        return price;
    }

    public void setPrice(Integer price) {
        this.price = price;
    }

    public LocalDateTime getLastUpdateDateTime() {
        return lastUpdateDateTime;
    }

    public void setLastUpdateDateTime(LocalDateTime lastUpdateDateTime) {
        this.lastUpdateDateTime = lastUpdateDateTime;
    }

    public ShopUnitType getType() {
        return type;
    }

    public void setType(ShopUnitType type) {
        this.type = type;
    }
}
