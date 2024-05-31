from __future__ import annotations as _annotations

from typing import NewType, TYPE_CHECKING

import pydantic_core
from pydantic.json_schema import GenerateJsonSchema
from pydantic.types import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from pydantic._internal import (
    _core_metadata,
    _core_utils,
    _schema_generation_shared,
)

from pydantic.annotated_handlers import GetJsonSchemaHandler

if TYPE_CHECKING:
    from pydantic._internal._core_utils import CoreSchemaOrField
    from pydantic._internal._schema_generation_shared import GetJsonSchemaFunction

JsonRef = NewType('JsonRef', str)
CoreRef = NewType('CoreRef', str)


class CustomGenerateJsonSchema(GenerateJsonSchema):
    def nullable_schema(self, schema: core_schema.NullableSchema) -> JsonSchemaValue:
        """Generates a JSON schema that matches a schema that allows null values.

        Args:
            schema: The core schema.

        Returns:
            The generated JSON schema.
        """
        null_schema = {'type': 'null'}
        inner_json_schema = self.generate_inner(schema['schema'])

        if inner_json_schema == null_schema:
            return null_schema
        else:
            # Thanks to the equality check against `null_schema` above, I think 'oneOf' would also be valid here;
            # I'll use 'anyOf' for now, but it could be changed it if it would work better with some external tooling
            return self.get_flattened_anyof([inner_json_schema, ])

    def handle_ref_overrides(self, json_schema: JsonSchemaValue) -> JsonSchemaValue:
        """It is not valid for a schema with a top-level $ref to have sibling keys.

        During our own schema generation, we treat sibling keys as overrides to the referenced schema,
        but this is not how the official JSON schema spec works.

        Because of this, we first remove any sibling keys that are redundant with the referenced schema, then if
        any remain, we transform the schema from a top-level '$ref' to use allOf to move the $ref out of the top level.
        (See bottom of https://swagger.io/docs/specification/using-ref/ for a reference about this behavior)
        """
        if '$ref' in json_schema:
            # prevent modifications to the input; this copy may be safe to drop if there is significant overhead
            json_schema = json_schema.copy()

            referenced_json_schema = self.get_schema_from_definitions(
                JsonRef(json_schema['$ref']))
            if referenced_json_schema is None:
                # This can happen when building schemas for models with not-yet-defined references.
                # It may be a good idea to do a recursive pass at the end of the generation to remove
                # any redundant override keys.
                # if len(json_schema) > 1:
                #     # Make it an allOf to at least resolve the sibling keys issue
                #     json_schema = json_schema.copy()
                #     json_schema.setdefault('allOf', [])
                #     json_schema['allOf'].append({'$ref': json_schema['$ref']})
                #     del json_schema['$ref']

                return json_schema
            for k, v in list(json_schema.items()):
                if k == '$ref':
                    continue
                if k in referenced_json_schema and referenced_json_schema[k] == v:
                    del json_schema[k]  # redundant key
            # if len(json_schema) > 1:
            #     # There is a remaining "override" key, so we need to move $ref out of the top level
            #     json_ref = JsonRef(json_schema['$ref'])
            #     del json_schema['$ref']
            #     assert 'allOf' not in json_schema  # this should never happen, but just in case
            #     json_schema['allOf'] = [{'$ref': json_ref}]

        return json_schema

    def default_schema(self, schema: core_schema.WithDefaultSchema) -> JsonSchemaValue:
        """Generates a JSON schema that matches a schema with a default value.

        Args:
            schema: The core schema.

        Returns:
            The generated JSON schema.
        """
        json_schema = self.generate_inner(schema['schema'])

        if 'default' not in schema:
            return json_schema
        default = schema['default']
        # Note: if you want to include the value returned by the default_factory,
        # override this method and replace the code above with:
        # if 'default' in schema:
        #     default = schema['default']
        # elif 'default_factory' in schema:
        #     default = schema['default_factory']()
        # else:
        #     return json_schema

        try:
            encoded_default = self.encode_default(default)
        except pydantic_core.PydanticSerializationError:
            self.emit_warning(
                'non-serializable-default',
                f'Default value {default} is not JSON serializable; excluding default from JSON schema',
            )
            # Return the inner schema, as though there was no default
            return json_schema

        # if '$ref' in json_schema:
        #     # Since reference schemas do not support child keys, we wrap the reference schema in a single-case allOf:
        #     return {'allOf': [json_schema], 'default': encoded_default}
        # else:
        json_schema['default'] = encoded_default
        return json_schema

    def generate_inner(self, schema: CoreSchemaOrField) -> JsonSchemaValue:  # noqa: C901
        """Generates a JSON schema for a given core schema.

        Args:
            schema: The given core schema.

        Returns:
            The generated JSON schema.
        """
        # If a schema with the same CoreRef has been handled, just return a reference to it
        # Note that this assumes that it will _never_ be the case that the same CoreRef is used
        # on types that should have different JSON schemas
        if 'ref' in schema:
            core_ref = CoreRef(schema['ref'])  # type: ignore[typeddict-item]
            core_mode_ref = (core_ref, self.mode)
            if core_mode_ref in self.core_to_defs_refs and self.core_to_defs_refs[core_mode_ref] in self.definitions:
                return {'$ref': self.core_to_json_refs[core_mode_ref]}

        # Generate the JSON schema, accounting for the json_schema_override and core_schema_override
        metadata_handler = _core_metadata.CoreMetadataHandler(schema)

        def populate_defs(core_schema: CoreSchema, json_schema: JsonSchemaValue) -> JsonSchemaValue:
            if 'ref' in core_schema:
                # type: ignore[typeddict-item]
                core_ref = CoreRef(core_schema['ref'])
                defs_ref, ref_json_schema = self.get_cache_defs_ref_schema(
                    core_ref)
                json_ref = JsonRef(ref_json_schema['$ref'])
                self.json_to_defs_refs[json_ref] = defs_ref
                # Replace the schema if it's not a reference to itself
                # What we want to avoid is having the def be just a ref to itself
                # which is what would happen if we blindly assigned any
                if json_schema.get('$ref', None) != json_ref:
                    self.definitions[defs_ref] = json_schema
                    self._core_defs_invalid_for_json_schema.pop(defs_ref, None)
                json_schema = ref_json_schema
            return json_schema

        def convert_to_all_of(json_schema: JsonSchemaValue) -> JsonSchemaValue:
            # if '$ref' in json_schema and len(json_schema.keys()) > 1:
            #     # technically you can't have any other keys next to a "$ref"
            #     # but it's an easy mistake to make and not hard to correct automatically here
            #     json_schema = json_schema.copy()
            #     ref = json_schema.pop('$ref')
            #     json_schema = {'allOf': [{'$ref': ref}], **json_schema}
            return json_schema

        def handler_func(schema_or_field: CoreSchemaOrField) -> JsonSchemaValue:
            """Generate a JSON schema based on the input schema.

            Args:
                schema_or_field: The core schema to generate a JSON schema from.

            Returns:
                The generated JSON schema.

            Raises:
                TypeError: If an unexpected schema type is encountered.
            """
            # Generate the core-schema-type-specific bits of the schema generation:
            json_schema: JsonSchemaValue | None = None
            if self.mode == 'serialization' and 'serialization' in schema_or_field:
                ser_schema = schema_or_field['serialization']  # type: ignore
                json_schema = self.ser_schema(ser_schema)
            if json_schema is None:
                if _core_utils.is_core_schema(schema_or_field) or _core_utils.is_core_schema_field(schema_or_field):
                    generate_for_schema_type = self._schema_type_to_method[schema_or_field['type']]
                    json_schema = generate_for_schema_type(schema_or_field)
                else:
                    raise TypeError(
                        f'Unexpected schema type: schema={schema_or_field}')
            if _core_utils.is_core_schema(schema_or_field):
                json_schema = populate_defs(schema_or_field, json_schema)
                json_schema = convert_to_all_of(json_schema)
            return json_schema

        current_handler = _schema_generation_shared.GenerateJsonSchemaHandler(
            self, handler_func)

        for js_modify_function in metadata_handler.metadata.get('pydantic_js_functions', ()):

            def new_handler_func(
                schema_or_field: CoreSchemaOrField,
                current_handler: GetJsonSchemaHandler = current_handler,
                js_modify_function: GetJsonSchemaFunction = js_modify_function,
            ) -> JsonSchemaValue:
                json_schema = js_modify_function(
                    schema_or_field, current_handler)
                if _core_utils.is_core_schema(schema_or_field):
                    json_schema = populate_defs(schema_or_field, json_schema)
                original_schema = current_handler.resolve_ref_schema(
                    json_schema)
                ref = json_schema.pop('$ref', None)
                if ref and json_schema:
                    original_schema.update(json_schema)
                return original_schema

            current_handler = _schema_generation_shared.GenerateJsonSchemaHandler(
                self, new_handler_func)

        for js_modify_function in metadata_handler.metadata.get('pydantic_js_annotation_functions', ()):

            def new_handler_func(
                schema_or_field: CoreSchemaOrField,
                current_handler: GetJsonSchemaHandler = current_handler,
                js_modify_function: GetJsonSchemaFunction = js_modify_function,
            ) -> JsonSchemaValue:
                json_schema = js_modify_function(
                    schema_or_field, current_handler)
                if _core_utils.is_core_schema(schema_or_field):
                    json_schema = populate_defs(schema_or_field, json_schema)
                    json_schema = convert_to_all_of(json_schema)
                return json_schema

            current_handler = _schema_generation_shared.GenerateJsonSchemaHandler(
                self, new_handler_func)

        json_schema = current_handler(schema)
        if _core_utils.is_core_schema(schema):
            json_schema = populate_defs(schema, json_schema)
            json_schema = convert_to_all_of(json_schema)
        return json_schema
