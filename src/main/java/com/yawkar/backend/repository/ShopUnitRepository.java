package com.yawkar.backend.repository;

import com.yawkar.backend.entity.ShopUnitEntity;
import org.springframework.data.repository.CrudRepository;

import java.util.UUID;

public interface ShopUnitRepository extends CrudRepository<ShopUnitEntity, UUID> {
}
