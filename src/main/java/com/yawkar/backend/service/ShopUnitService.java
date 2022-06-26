package com.yawkar.backend.service;

import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.repository.ShopUnitRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
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

    /**
     * Grabs shop unit with all sub-shopunits together (very expensive request)
     * @param uuid {@code UUID} of shop unit
     * @return {@link ShopUnitEntity} with all data
     */
    public ShopUnitEntity findById(UUID uuid) {
        return shopUnitRepository.findById(uuid).orElse(null);
    }

    public ShopUnitEntity findByIdFull(UUID uuid) {
        ShopUnitEntity shopUnitEntity = shopUnitRepository.findById(uuid).orElse(null);
        if (shopUnitEntity != null && shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.CATEGORY) {
            shopUnitEntity.setChildren(new ArrayList<>());
            for (var child : findAllByParentUuid(uuid)) {
                shopUnitEntity.getChildren().add(findByIdFull(child.getUuid()));
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

    private void updateCategory(ShopUnitEntity category) {
        ShopUnitEntity oldCategory = findById(category.getUuid());
        category.setPrice(oldCategory.getPrice());
        category.setSize(oldCategory.getSize());
        if (category.getParentUuid() != oldCategory.getParentUuid()) {
            if (oldCategory.getParentUuid() == null) {
                save(category);
                if (existsById(category.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(category.getParentUuid()), category.getPrice(), category.getSize(), category.getLastUpdateDateTime());
                }
            } else {
                save(category);
                if (existsById(oldCategory.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(oldCategory.getParentUuid()), -category.getPrice(), -category.getSize(), category.getLastUpdateDateTime());
                }
                if (category.getParentUuid() != null && existsById(category.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(category.getParentUuid()), category.getPrice(), category.getSize(), category.getLastUpdateDateTime());
                }
            }
        } else {
            save(category);
        }
    }

    private void saveNewCategory(ShopUnitEntity category) {
        List<ShopUnitEntity> childrenThatMayExist = findAllByParentUuid(category.getUuid());
        for (var child : childrenThatMayExist) {
            category.setSize(category.getSize() + child.getSize());
            if (child.getPrice() != null) {
                category.setPrice((category.getPrice() == null ? 0 : category.getPrice()) + child.getPrice());
            }
        }
        save(category);
        if (category.getParentUuid() == null || !existsById(category.getParentUuid())) {
            return;
        }
        ShopUnitEntity parent = findById(category.getParentUuid());
        while (true) {
            parent.setLastUpdateDateTime(category.getLastUpdateDateTime());
            parent.setSize(parent.getSize() + category.getSize());
            if (category.getPrice() != null) {
                parent.setPrice((parent.getPrice() == null ? 0 : parent.getPrice()) + category.getPrice());
            }
            save(parent);
            if (parent.getParentUuid() == null || !existsById(parent.getParentUuid())) {
                break;
            }
            parent = findById(parent.getParentUuid());
        }
    }

    private void updatePriceSizeAndDateUpToTheRootFrom(ShopUnitEntity startNode, Integer priceDelta, int sizeDelta, LocalDateTime newDate) {
        while (true) {
            if (newDate != null) {
                startNode.setLastUpdateDateTime(newDate);
            }
            if (priceDelta != null) {
                startNode.setPrice((startNode.getPrice() == null ? 0 : startNode.getPrice()) + priceDelta);
            }
            startNode.setSize(startNode.getSize() + sizeDelta);
            if (startNode.getSize() == 0) {
                // It's possible only inside an empty category
                startNode.setPrice(null);
            }
            save(startNode);
            if (startNode.getParentUuid() == null || !existsById(startNode.getParentUuid())) {
                break;
            }
            startNode = findById(startNode.getParentUuid());
        }
    }

    private void updateOffer(ShopUnitEntity offer) {
        ShopUnitEntity oldOffer = findById(offer.getUuid());
        if (offer.getParentUuid() != oldOffer.getParentUuid()) {
            if (oldOffer.getParentUuid() == null) {
                save(offer);
                if (existsById(offer.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(offer.getParentUuid()), offer.getPrice(), 1, offer.getLastUpdateDateTime());
                }
            } else {
                save(offer);
                if (existsById(oldOffer.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(oldOffer.getParentUuid()), -offer.getPrice(), -1, offer.getLastUpdateDateTime());
                }
                if (offer.getParentUuid() != null && existsById(offer.getParentUuid())) {
                    updatePriceSizeAndDateUpToTheRootFrom(findById(offer.getParentUuid()), offer.getPrice(), 1, offer.getLastUpdateDateTime());
                }
            }
        } else if (!Objects.equals(offer.getPrice(), oldOffer.getPrice())) {
            save(offer);
            if (offer.getParentUuid() != null && existsById(offer.getParentUuid())) {
                updatePriceSizeAndDateUpToTheRootFrom(findById(offer.getParentUuid()), offer.getPrice() - oldOffer.getPrice(), 0, offer.getLastUpdateDateTime());
            }
        } else {
            save(offer);
        }
    }

    private void saveNewOffer(ShopUnitEntity offer) {
        save(offer);
        if (offer.getParentUuid() == null || !existsById(offer.getParentUuid())) {
            return;
        }
        ShopUnitEntity parent = findById(offer.getParentUuid());
        while (true) {
            parent.setLastUpdateDateTime(offer.getLastUpdateDateTime());
            parent.setSize(parent.getSize() + 1);
            parent.setPrice((parent.getPrice() == null ? 0 : parent.getPrice()) + offer.getPrice());
            save(parent);
            if (parent.getParentUuid() == null || !existsById(parent.getParentUuid())) {
                break;
            }
            parent = findById(parent.getParentUuid());
        }
    }

    /**
     * Saves (or updates) given shop unit with updating parent categories (if exist)
     * @param shopUnitEntity given shop unit that needs to be saved
     */
    public void saveWithUpdateTree(ShopUnitEntity shopUnitEntity) {
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.CATEGORY) {
            if (existsById(shopUnitEntity.getUuid())) {
                updateCategory(shopUnitEntity);
            } else {
                saveNewCategory(shopUnitEntity);
            }
        } else {
            if (existsById(shopUnitEntity.getUuid())) {
                updateOffer(shopUnitEntity);
            } else {
                saveNewOffer(shopUnitEntity);
            }
        }
    }

    /**
     * Deletes offer and updates data of parent categories
     * @param offerUuid {@code UUID} of the offer that needs to be deleted
     */
    private void deleteOffer(UUID offerUuid) {
        ShopUnitEntity offer = findById(offerUuid);
        shopUnitRepository.deleteById(offerUuid);
        if (offer.getParentUuid() == null || !existsById(offer.getParentUuid())) {
            return;
        }
        updatePriceSizeAndDateUpToTheRootFrom(findById(offer.getParentUuid()), -offer.getPrice(), -1, null);
    }

    /**
     * Deletes sub-shopunits and itself
     * @param shopUnitEntity root
     */
    private void deleteSubTreeWithRoot(ShopUnitEntity shopUnitEntity) {
        if (shopUnitEntity.getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            shopUnitRepository.deleteById(shopUnitEntity.getUuid());
        } else {
            for (var child : findAllByParentUuid(shopUnitEntity.getUuid())) {
                deleteSubTreeWithRoot(child);
            }
            shopUnitRepository.deleteById(shopUnitEntity.getUuid());
        }
    }

    /**
     * Deletes category with given {@code UUID}<br>
     * Perhaps, deletes subcategories and suboffers, after that goes up and updates
     * data of parent categories
     * @param categoryUuid {@code UUID} of the category that should be deleted
     */
    private void deleteCategory(UUID categoryUuid) {
        ShopUnitEntity category = findById(categoryUuid);
        deleteSubTreeWithRoot(category);
        if (category.getParentUuid() == null || !existsById(category.getParentUuid())) {
            return;
        }
        updatePriceSizeAndDateUpToTheRootFrom(findById(category.getParentUuid()), category.getPrice() == null ? null : -category.getPrice(), -category.getSize(), null);
    }

    /**
     * Deletes shop unit with given {@code UUID}<br>
     * If type of the shop unit is {@code OFFER} : {@link #deleteOffer(UUID)}<br>
     * Otherwise : {@link #deleteCategory(UUID)}
     * @param uuid {@code UUID} of the shop unit that should be deleted
     */
    public void deleteById(UUID uuid) {
        if (findById(uuid).getType() == ShopUnitEntity.ShopUnitType.OFFER) {
            deleteOffer(uuid);
        } else {
            deleteCategory(uuid);
        }
    }
}
