import random
import logging
from typing import Callable, Type, NamedTuple, Sequence, Optional, Tuple

from populating import DataBaseEntity, Hull, Engine, Weapon, Ship


class Rule(NamedTuple):
    entity_t: Type
    attr: str
    callback: Callable


class Randomizer:
    def __init__(self, rules: Optional[Sequence[Rule]] = None):
        self._rules = [*rules] if rules is not None else []

    def add_rule(self, entity_t: Type[DataBaseEntity], attr: str, call: Callable):
        assert attr in entity_t._fields, entity_t._fields
        self._rules.append(Rule(entity_t, attr, call))

    def pop_rule(self) -> None:
        self._rules.pop()

    def generate(self, entity_t: Type[DataBaseEntity], **values):
        assert len(values.keys()) < len(entity_t._fields)
        entity_items = {}
        for rule in self._rules:
            if rule.entity_t == entity_t:
                value = rule.callback()
                entity_items.update({rule.attr: value})

        entity_items.update(**values)
        try:
            return entity_t(*entity_items.values())
        except TypeError:
            logging.error("Something went wrong while generating new entity.")
            raise

    def modify_with_probability(
            self, entity: DataBaseEntity, probability: float,
            constant_fields: Optional[Sequence[str]] = None
    ) -> DataBaseEntity:

        def choose_attrs_to_change():
            count_fields_to_change = len(entity._fields) * probability
            attrs = set()
            while len(attrs) < count_fields_to_change - len(constant_fields):
                random_field = random.choice(entity._fields)
                if random_field in constant_fields:
                    continue
                attrs.add(random_field)
            return attrs

        constant_fields = [] if constant_fields is None else constant_fields
        assert 0 < probability <= 1, probability
        attrs_to_change = choose_attrs_to_change()
        modified = entity
        for rule in self._rules:
            if rule.entity_t == type(entity) and rule.attr in attrs_to_change:
                modified = self._apply_rule(modified, rule)
        return modified

    def modify_field(
            self, entity: DataBaseEntity, field_to_change: str
    ) -> DataBaseEntity:
        for rule in self._rules:
            if rule.entity_t == type(entity) and rule.attr == field_to_change:
                return self._apply_rule(entity, rule)

    def _apply_rule(self, entity: DataBaseEntity, rule: Rule):
        return entity._replace(**{rule.attr: rule.callback()})


RULES = [
    Rule(Hull, 'hull', lambda: "hull_" + str(random.randrange(1, 900000))),
    Rule(Hull, 'armor', lambda: random.randrange(30, 500, 10)),
    Rule(Hull, 'type', lambda: random.randrange(1, 10)),
    Rule(Hull, 'capacity', lambda: random.randrange(100, 800, 10)),
    Rule(Engine, "engine", lambda: "engine_" + str(random.randrange(1, 900000))),
    Rule(Engine, "power", lambda: random.randrange(4000, 10000, 100)),
    Rule(Engine, "type", lambda: random.randrange(1, 10)),
    Rule(Weapon, "weapon", lambda: "weapon_" + str(random.randrange(1, 900000))),
    Rule(Weapon, "reload_speed", lambda: random.randrange(3, 30)),
    Rule(Weapon, "rotational_speed", lambda: random.randrange(15, 60, 3)),
    Rule(Weapon, "diameter", lambda: random.randrange(3, 30)),
    Rule(Weapon, "power_volley", lambda: random.randrange(100, 2000, 30)),
    Rule(Weapon, "count", lambda: random.randrange(1, 4)),
    Rule(Ship, "ship", lambda: "ship_" + str(random.randrange(1, 900000)))
]

default_randomizer = Randomizer(RULES)