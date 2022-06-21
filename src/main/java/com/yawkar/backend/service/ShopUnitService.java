package com.yawkar.backend.service;

import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.repository.ShopUnitRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
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
        ShopUnitEntity shopUnitEntity = shopUnitRepository.findById(uuid).orElseGet(() -> null);
        if (shopUnitEntity != null && shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.CATEGORY) {
            shopUnitEntity.setChildren(new ArrayList<>());
            for (var child : findAllByParentUuid(uuid)) {
                shopUnitEntity.getChildren().add(findById(child.getUuid()));
            }
        }
        return shopUnitEntity;
    }

    public List<ShopUnitEntity> findAllByParentUuid(UUID parentUuid) {
        List<ShopUnitEntity> children = new ArrayList<>();
        for (var shopUnit : shopUnitRepository.findAllByParentUuid(parentUuid)) {
            children.add(shopUnit);
        }
        return children;
    }

    public List<ShopUnitEntity> findShopUnitEntitiesByLastUpdateDateTimeBetweenAndType(LocalDateTime timeStart, LocalDateTime timeEnd, ShopUnitEntity.ShopUnitType type) {
        List<ShopUnitEntity> found = new ArrayList<>();
        for (var shopUnit : shopUnitRepository.findShopUnitEntitiesByLastUpdateDateTimeBetweenAndType(timeStart, timeEnd, type)) {
            found.add(shopUnit);
        }
        return found;
    }

    private void save(ShopUnitEntity shopUnitEntity) {
        shopUnitRepository.save(shopUnitEntity);
    }

    public void saveWithUpdateTree(ShopUnitEntity shopUnitEntity) {
        boolean updatePrice = false;
        boolean isNewOffer = false;
        int priceDelta = 0;
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            priceDelta = shopUnitEntity.getPrice();
            if (existsById(shopUnitEntity.getUuid())) {
                priceDelta -= findById(shopUnitEntity.getUuid()).getPrice();
            } else {
                isNewOffer = true;
            }
            updatePrice = true;
        } else {
            if (existsById(shopUnitEntity.getUuid())) {
                shopUnitEntity.setPrice(findById(shopUnitEntity.getUuid()).getPrice());
                shopUnitEntity.setSize(findById(shopUnitEntity.getUuid()).getSize());
            }
        }
        save(shopUnitEntity);
        if (shopUnitEntity.getParentUuid() == null) {
            return;
        }
        ShopUnitEntity parent = findById(shopUnitEntity.getParentUuid());
        while (parent.getParentUuid() != null) {
            parent.setLastUpdateDateTime(shopUnitEntity.getLastUpdateDateTime());
            if (updatePrice) {
                parent.setPrice((parent.getPrice() == null ? 0 : parent.getPrice()) + priceDelta);
            }
            if (isNewOffer) {
                parent.setSize(parent.getSize() + 1);
            }
            save(parent);
            parent = findById(parent.getParentUuid());
        }
        parent.setLastUpdateDateTime(shopUnitEntity.getLastUpdateDateTime());
        if (updatePrice) {
            parent.setPrice((parent.getPrice() == null ? 0 : parent.getPrice()) + priceDelta);
        }
        if (isNewOffer) {
            parent.setSize(parent.getSize() + 1);
        }
        save(parent);
    }

    private void deleteOffer(UUID offerUuid) {
        ShopUnitEntity offer = findById(offerUuid);
        shopUnitRepository.deleteById(offerUuid);
        if (offer.getParentUuid() == null) {
            return;
        }
        int priceDelta = -offer.getPrice();
        ShopUnitEntity parent = findById(offer.getParentUuid());
        while (parent.getParentUuid() != null) {
            parent.setSize(parent.getSize() - 1);
            if (parent.getSize() == 0) {
                parent.setPrice(null);
            } else {
                parent.setPrice(parent.getPrice() + priceDelta);
            }
            save(parent);
            parent = findById(parent.getParentUuid());
        }
        parent.setSize(parent.getSize() - 1);
        if (parent.getSize() == 0) {
            parent.setPrice(null);
        } else {
            parent.setPrice(parent.getPrice() + priceDelta);
        }
        save(parent);
    }

    private void deleteSubTreeWithRoot(ShopUnitEntity shopUnitEntity) {
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            shopUnitRepository.deleteById(shopUnitEntity.getUuid());
        } else {
            for (var child : shopUnitEntity.getChildren()) {
                deleteSubTreeWithRoot(child);
            }
            shopUnitRepository.deleteById(shopUnitEntity.getUuid());
        }
    }

    private void deleteCategory(UUID categoryUuid) {
        ShopUnitEntity category = findById(categoryUuid);
        boolean isPriceChanging = false;
        int priceDelta = 0;
        int sizeDelta = -category.getSize();
        if (category.getPrice() != null) {
            isPriceChanging = true;
            priceDelta = -category.getPrice();
        }
        deleteSubTreeWithRoot(category);
        if (category.getParentUuid() == null) {
            return;
        }
        ShopUnitEntity parent = findById(category.getParentUuid());
        while (true) {
            parent.setSize(parent.getSize() + sizeDelta);
            if (isPriceChanging) {
                if (parent.getSize() == 0) {
                    parent.setPrice(null);
                } else {
                    parent.setPrice(parent.getPrice() + priceDelta);
                }
            }
            save(parent);
            if (parent.getParentUuid() == null) {
                break;
            }
            parent = findById(parent.getParentUuid());
        }
    }

    public void deleteById(UUID uuid) {
        if (findById(uuid).getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            deleteOffer(uuid);
        } else {
            deleteCategory(uuid);
        }
    }
}
