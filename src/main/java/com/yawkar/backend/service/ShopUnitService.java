package com.yawkar.backend.service;

import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.repository.ShopUnitRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@Scope("singleton")
public class ShopUnitService {

    private final ShopUnitRepository shopUnitRepository;

    private ShopUnitService(@Autowired ShopUnitRepository shopUnitRepository) {
        this.shopUnitRepository = shopUnitRepository;
    }
    public boolean existsById(UUID uuid) {
        return shopUnitRepository.existsById(uuid);
    }

    public ShopUnitEntity findById(UUID uuid) {
        return shopUnitRepository.findById(uuid).orElseGet(() -> null);
    }

    public void save(ShopUnitEntity shopUnitEntity) {
        shopUnitRepository.save(shopUnitEntity);
    }

    public void deleteById(UUID uuid) {
        shopUnitRepository.deleteById(uuid);
    }
}
