package com.yawkar.backend.repository;

import com.yawkar.backend.entity.ShopUnitEntity;
import org.springframework.data.repository.CrudRepository;

import java.time.LocalDateTime;
import java.util.UUID;

public interface ShopUnitRepository extends CrudRepository<ShopUnitEntity, UUID> {

    Iterable<ShopUnitEntity> findAllByParentUuid(UUID parentUuid);

    Iterable<ShopUnitEntity> findShopUnitEntitiesByLastUpdateDateTimeBetweenAndType(LocalDateTime timeStart, LocalDateTime timeEnd, ShopUnitEntity.ShopUnitType type);
}
