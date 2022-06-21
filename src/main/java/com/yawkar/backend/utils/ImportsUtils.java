package com.yawkar.backend.utils;

import org.everit.json.schema.PrimitiveValidationStrategy;
import org.everit.json.schema.Schema;
import org.everit.json.schema.Validator;
import org.everit.json.schema.loader.SchemaLoader;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.FileReader;

public class ImportsUtils {

    public static boolean isValidImports(String importsJson) {
        try {
            JSONObject jsonSchema = new JSONObject(
                    new JSONTokener(new FileReader("src/main/resources/schemas/imports.json"))
            );
            JSONObject jsonSubject = new JSONObject(
                    new JSONTokener(importsJson)
            );
            Schema schema = SchemaLoader.load(jsonSchema);
            Validator validator = Validator.builder()
                    .primitiveValidationStrategy(PrimitiveValidationStrategy.STRICT)
                    .failEarly()
                    .build();
            try {
                validator.performValidation(schema, jsonSubject);
                return true;
            } catch (Exception e) {
                return false;
            }
        }catch (Exception e) {
            System.out.println(e);
            return false;
        }
    }
}
