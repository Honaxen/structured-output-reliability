"""
A dataset of JSON schemas at increasing levels of structural complexity,
each paired with a natural-language prompt that asks the model to
produce data conforming to that schema.

Complexity is defined here by concrete structural properties -- number
of fields, presence of nesting, presence of arrays, presence of nested
arrays-of-objects -- not by subjective difficulty. That's what lets the
evaluation stage make a real claim like "success rate drops as nesting
depth increases" instead of an impressionistic one.

Each entry includes a jsonschema-compatible schema (for validation in
retry/validate.py) and a task_prompt (what the model is actually asked
to do -- deliberately does NOT mention "JSON" or "schema" by itself,
since that instruction is exactly what strategies/ varies across
conditions).

Usage:
    from schema_dataset import SCHEMA_DATASET
    for entry in SCHEMA_DATASET:
        print(entry["name"], entry["complexity"])
"""

SCHEMA_DATASET = [
    {
        "name": "flat_simple",
        "complexity": "simple",
        "description": "Flat object, 3 scalar fields, no nesting or arrays.",
        "task_prompt": "Describe a person named Alex who is 29 years old and works as a graphic designer.",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "occupation": {"type": "string"},
            },
            "required": ["name", "age", "occupation"],
            "additionalProperties": False,
        },
    },
    {
        "name": "flat_medium",
        "complexity": "simple",
        "description": "Flat object, 6 scalar fields including a boolean and a float.",
        "task_prompt": "Describe a laptop: model name 'ProBook X14', price $1299.99, 16GB RAM, "
                        "512GB storage, currently in stock, released in 2024.",
        "schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string"},
                "price": {"type": "number"},
                "ram_gb": {"type": "integer"},
                "storage_gb": {"type": "integer"},
                "in_stock": {"type": "boolean"},
                "release_year": {"type": "integer"},
            },
            "required": ["model_name", "price", "ram_gb", "storage_gb", "in_stock", "release_year"],
            "additionalProperties": False,
        },
    },
    {
        "name": "nested_object",
        "complexity": "nested",
        "description": "One level of object nesting (address inside person).",
        "task_prompt": "Describe a person named Jordan Lee, 34 years old, who lives at "
                        "123 Maple Street, Springfield, in the state of Illinois, zip code 62704.",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "state": {"type": "string"},
                        "zip": {"type": "string"},
                    },
                    "required": ["street", "city", "state", "zip"],
                    "additionalProperties": False,
                },
            },
            "required": ["name", "age", "address"],
            "additionalProperties": False,
        },
    },
    {
        "name": "flat_array",
        "complexity": "array",
        "description": "Flat object with one array-of-strings field.",
        "task_prompt": "Describe a recipe called 'Simple Pancakes' with these ingredients: "
                        "flour, milk, eggs, sugar, and baking powder.",
        "schema": {
            "type": "object",
            "properties": {
                "recipe_name": {"type": "string"},
                "ingredients": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["recipe_name", "ingredients"],
            "additionalProperties": False,
        },
    },
    {
        "name": "array_of_objects",
        "complexity": "array_of_objects",
        "description": "Array where each element is itself a multi-field object.",
        "task_prompt": "List three team members: Sam (role: Engineer, years experience: 5), "
                        "Priya (role: Designer, years experience: 3), and Chen (role: Product Manager, years experience: 7).",
        "schema": {
            "type": "object",
            "properties": {
                "team_members": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "years_experience": {"type": "integer"},
                        },
                        "required": ["name", "role", "years_experience"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["team_members"],
            "additionalProperties": False,
        },
    },
    {
        "name": "deeply_nested",
        "complexity": "deeply_nested",
        "description": "Two levels of nesting plus a nested array-of-objects -- the most structurally complex schema in the set.",
        "task_prompt": "Describe an order: order ID 'ORD-4471', customer named Taylor Morgan whose "
                        "shipping address is 88 Birch Ave, Denver, Colorado, zip 80202. The order contains "
                        "two items: 'Wireless Mouse' (quantity 1, price $24.99) and 'USB-C Cable' (quantity 3, price $9.99 each).",
        "schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "customer": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "shipping_address": {
                            "type": "object",
                            "properties": {
                                "street": {"type": "string"},
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                                "zip": {"type": "string"},
                            },
                            "required": ["street", "city", "state", "zip"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["name", "shipping_address"],
                    "additionalProperties": False,
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "unit_price": {"type": "number"},
                        },
                        "required": ["item_name", "quantity", "unit_price"],
                    },
                },
            },
            "required": ["order_id", "customer", "items"],
        },
    },
]


def get_by_complexity(complexity: str) -> list:
    return [entry for entry in SCHEMA_DATASET if entry["complexity"] == complexity]


def get_by_name(name: str) -> dict | None:
    for entry in SCHEMA_DATASET:
        if entry["name"] == name:
            return entry
    return None
