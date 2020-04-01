import nose
from itertools import chain
import os

from typing import Type, List, Iterable, NamedTuple, Sequence
import random

from populating import DataBaseEntity, Weapon, Hull, Engine, Ship
from db import DatabaseConnection, SqlLiteConnection
from populating import DBInteractor
from randomizer import default_randomizer, Randomizer, RULES

import config


def create_sqlite_backup(from_db: str, backup_name: str) -> DatabaseConnection:
    conn = SqlLiteConnection(from_db)
    backup = conn.create_backup(backup_name)
    conn.close()
    return backup


def insert_values_into_database(db: DatabaseConnection):
    def generate_entities(
            entity_t: Type[DataBaseEntity], amount: int) -> List[DataBaseEntity]:
        entities = []
        for _ in range(0, amount):
            entity = default_randomizer.generate(entity_t)
            entities.append(entity)
        return entities

    def generate_ships(
            amount: int, weapons: List[Weapon], engines: List[Engine],
            hulls: List[Hull]
    ) -> List[Ship]:
        ships = []
        for _ in range(0, amount):
            ship = default_randomizer.generate(
                Ship,
                weapon=random.choice(weapons).weapon,
                hull=random.choice(hulls).hull,
                engine=random.choice(engines).engine
            )
            ships.append(ship)
        return ships

    interactor = DBInteractor(db)
    hulls = generate_entities(Hull, config.HULLS_AMOUNT)
    weapons = generate_entities(Weapon, config.WEAPONS_AMOUNT)
    engines = generate_entities(Engine, config.ENGINES_AMOUNT)
    ships = generate_ships(config.SHIPS_AMOUNT, weapons, engines, hulls)
    _ = [_ for _ in chain(
        map(interactor.insert_entity, weapons),
        map(interactor.insert_entity, engines),
        map(interactor.insert_entity, hulls),
        map(interactor.insert_entity, ships)
    )]


def modify_values_in_database(interactor: DBInteractor, randomizer: Randomizer):
    def get_field_values(field: str, entities: Iterable[DataBaseEntity]):
        return [getattr(e, field) for e in entities]

    def get_modified_entities(
            amount: int, choose_from: Iterable, probability: float,
            constant_fields: Sequence
    ) -> List[DataBaseEntity]:
        modified_entities = []
        for _ in range(0, amount):
            modified_entities.append(
                randomizer.modify_with_probability(
                    entity=random.choice(choose_from),
                    probability=probability,
                    constant_fields=constant_fields
                )
            )
        return modified_entities

    def get_modified_ships(amount: int, engines, hulls, weapons) -> List[Ship]:
        randomizer.add_rule(
            Ship,
            'engine',
            lambda: random.choice(get_field_values('engine', engines))
        )
        randomizer.add_rule(
            Ship,
            'hull',
            lambda: random.choice(get_field_values('hull', hulls))
        )
        randomizer.add_rule(
            Ship,
            'weapon',
            lambda: random.choice(get_field_values('weapon', weapons))
        )
        mod_ships = get_modified_entities(amount, ships, 0.3, ("ship", ))
        randomizer.pop_rule()
        randomizer.pop_rule()
        randomizer.pop_rule()
        return mod_ships

    ships = interactor.select(Ship)
    modified_weapons = get_modified_entities(
        amount=config.WEAPONS_AMOUNT // 3,
        choose_from=interactor.select(Weapon),
        probability=0.5,
        constant_fields=('weapon', )
    )
    modified_hulls = get_modified_entities(
        amount=config.HULLS_AMOUNT // 3,
        choose_from=interactor.select(Hull),
        probability=0.5,
        constant_fields=('hull', ))
    modified_engines = get_modified_entities(
        amount=config.ENGINES_AMOUNT // 3,
        choose_from=interactor.select(Engine),
        probability=0.5,
        constant_fields=('engine', ))

    for engine in modified_engines:
        interactor.update_engine(engine)
    for weapon in modified_weapons:
        interactor.update_weapon(weapon)
    for hull in modified_hulls:
        interactor.update_hull(hull)

    modified_ships = get_modified_ships(
        amount=config.SHIPS_AMOUNT // 10,
        hulls=interactor.select(Hull),
        engines=interactor.select(Engine),
        weapons=interactor.select(Weapon)
    )
    for e in modified_ships:
        interactor.update_ship(e)


def compare_ships(ship: Ship, other: Ship) -> None:
    class Mismatch(NamedTuple):
        entity: DataBaseEntity
        compared: DataBaseEntity
        field_name: str

    def format_mismatches(mismatches: List[Mismatch]):
        result = []
        for mis in mismatches:
            result.append("\n%s->%s:\n\texpected: %s\n\treceive:  %s" % (
                mis.entity[0],
                mis.field_name,
                getattr(mis.entity, mis.field_name),
                getattr(mis.compared, mis.field_name)
            ))
        return '\n'.join(result)

    mismatches: List[Mismatch] = []
    for i, value in enumerate(ship):
        if value != other[i]:
            field = ship._fields[i]
            mismatches.append(Mismatch(ship, other, field))

    assert not mismatches, format_mismatches(mismatches)


class TestDataBase:
    _errors = []
    _backup = None

    @classmethod
    def setupClass(cls) -> None:
        cls._randomizer = Randomizer(RULES)
        cls._backup = create_sqlite_backup(
                config.SQLITE_DB_PATH, config.SQLITE_BACKUP_DB_NAME
            )
        cls._interactor = DBInteractor(cls._backup)
        modify_values_in_database(cls._interactor, cls._randomizer)

    @classmethod
    def teardownClass(cls) -> None:
        cls._backup.close()
        os.remove(config.SQLITE_BACKUP_DB_NAME)

    def test_database(self):
        source_interactor = DBInteractor(SqlLiteConnection(config.SQLITE_DB_PATH))
        target_ships = self._interactor.select(Ship)
        source_ships = source_interactor.select(Ship)
        for source_ship, target_ship in zip(source_ships, target_ships):
            yield compare_ships, source_ship, target_ship


if __name__ == '__main__':
    nose.run()