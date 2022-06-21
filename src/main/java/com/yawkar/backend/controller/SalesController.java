package com.yawkar.backend.controller;

import com.google.gson.JsonElement;
import com.yawkar.backend.entity.ShopUnitEntity;
import com.yawkar.backend.service.ShopUnitService;
import com.yawkar.backend.utils.GsonUtils;
import com.yawkar.backend.utils.SalesUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@RestController
public class SalesController {

    @Autowired
    private ShopUnitService shopUnitService;

    @GetMapping("sales")
    public ResponseEntity<String> getSales(@RequestParam(name = "date") String dateEnd) {
        try {
            LocalDateTime date = LocalDateTime.parse(dateEnd, DateTimeFormatter.ISO_DATE_TIME);
            LocalDateTime date24HourAgo = date.minusHours(24);
            List<ShopUnitEntity> soldOffers = shopUnitService.findShopUnitEntitiesByLastUpdateDateTimeBetweenAndType(
                    date24HourAgo,
                    date,
                    ShopUnitEntity.ShopUnitType.OFFER
            );
            JsonElement salesJson = SalesUtils.serializeOffers(soldOffers);
            return ResponseEntity
                    .ok()
                    .body(GsonUtils.gson.toJson(salesJson));
        } catch (Exception e) {
            System.out.println(e);
            return ResponseEntity
                    .status(HttpStatus.BAD_REQUEST)
                    .body("{\"code\": 400, \"message\": \"Validation Failed\"}");
        }
    }
}
