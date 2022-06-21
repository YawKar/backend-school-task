package com.yawkar.backend.controller;

import com.yawkar.backend.service.ShopUnitService;
import com.yawkar.backend.utils.GsonUtils;
import com.yawkar.backend.utils.Imports;
import com.yawkar.backend.utils.ImportsUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;
import java.util.regex.Pattern;

@RestController
public class NodesController {

    public static final String UUID_STRING =
            "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}";

    public static final Pattern UUID_PATTERN = Pattern.compile(UUID_STRING);

    @Autowired
    private ShopUnitService shopUnitService;

    @GetMapping(value = "nodes/{id}")
    public ResponseEntity<String> getNode(@PathVariable("id") String uuidString) {
        if (UUID_PATTERN.matcher(uuidString).matches()) {
            UUID uuid = UUID.fromString(uuidString);
            if (shopUnitService.existsById(uuid)) {
                return ResponseEntity
                        .ok()
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(GsonUtils.gson.toJson(shopUnitService.findById(uuid)));
            } else {
                return ResponseEntity
                        .status(HttpStatus.NOT_FOUND)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{\"code\": 404, \"message\": \"Item not found\"}");
            }
        } else {
            return ResponseEntity
                    .badRequest()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"code\": 400, \"message\": \"Validation Failed\"}");
        }
    }

    @DeleteMapping(value = "delete/{id}")
    public ResponseEntity<String> deleteNode(@PathVariable("id") String uuidString) {
        if (UUID_PATTERN.matcher(uuidString).matches()) {
            UUID uuid = UUID.fromString(uuidString);
            if (shopUnitService.existsById(uuid)) {
                shopUnitService.deleteById(uuid);
                return ResponseEntity
                        .ok()
                        .build();
            } else {
                return ResponseEntity
                        .status(HttpStatus.NOT_FOUND)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{\"code\": 404, \"message\": \"Item not found\"}");
            }
        } else {
            return ResponseEntity
                    .badRequest()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"code\": 400, \"message\": \"Validation Failed\"}");
        }
    }

    @PostMapping(value = "imports", consumes = "application/json")
    public ResponseEntity<String> imports(@RequestBody String payload) {
        if (ImportsUtils.isValidImports(payload)) {
            Imports imports = GsonUtils.gson.fromJson(payload, Imports.class);
            for (var shopUnit : imports.getItems()) {
                shopUnit.setLastUpdateDateTime(imports.getUpdateTime());
                shopUnitService.saveWithUpdateTree(shopUnit);
            }
            return ResponseEntity
                    .ok()
                    .build();
        } else {
            return ResponseEntity
                    .badRequest()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"code\": 400, \"message\": \"Validation Failed\"}");
        }
    }
}
