from typing import NamedTuple, Union, Any, Type, List

from db import DatabaseConnection
from sql_scripts import (
    INSERT_INTO_TABLE,
    SELECT_FROM,
    UPDATE_ENTITY,
    CREATE_SHIP_TABLE,
    CREATE_WEAPON_TABLE,
    CREATE_HULL_TABLE,
    CREATE_ENGINE_TABLE
)


class Ship(NamedTuple):
    ship: str
    weapon: str
    hull: str
    engine: str


class Hull(NamedTuple):
    hull: str
    armor: int
    type: int
    capacity: int


class Engine(NamedTuple):
    engine: str
    power: int
    type: int


class Weapon(NamedTuple):
    weapon: str
    reload_speed: int
    rotational_speed: int
    diameter: int
    power_volley: int
    count: int


DataBaseEntity = Union[Ship, Weapon, Hull, Engine]

_TABLE_NAMES_MAP = {
    Ship: "ships",
    Weapon: "weapons",
    Hull: "hulls",
    Engine: "engines"
}


class DBInteractor:
    def __init__(self, connection: DatabaseConnection):
        self._conn = connection
        self._cursor = self._conn.cursor()
        self._create_tables()

    def update_weapon(self, entity: Weapon):
        self._update_entity(entity, 'weapon', entity.weapon)

    def update_hull(self, entity: Hull):
        self._update_entity(entity, 'hull', entity.hull)

    def update_engine(self, entity: Engine):
        self._update_entity(entity, 'engine', entity.engine)

    def update_ship(self, entity: Ship):
        self._update_entity(entity, 'ship', entity.ship)

    def _create_tables(self):
        self._cursor.execute(CREATE_ENGINE_TABLE)
        self._cursor.execute(CREATE_HULL_TABLE)
        self._cursor.execute(CREATE_WEAPON_TABLE)
        self._cursor.execute(CREATE_SHIP_TABLE)
        self._conn.commit()

    def _update_entity(self, entity: DataBaseEntity, key: str, value: Any) -> None:
        def format_pair(col: str, v: str) -> str:
            return "%s=%s" % (col, repr(v))

        entity_items = zip(entity._fields, list(entity))
        query = UPDATE_ENTITY.format(
            table=_TABLE_NAMES_MAP[type(entity)],
            values=','.join(format_pair(c, v) for c, v in entity_items),
            where=format_pair(key, value)
            )
        self._cursor.execute(query)
        self._conn.commit()

    def insert_entity(self, entity: DataBaseEntity):
        query = INSERT_INTO_TABLE.format(
            table=_TABLE_NAMES_MAP[type(entity)],
            columns=','.join(entity._fields),
            values=','.join(repr(v) for v in entity)
        )
        self._cursor.execute(query)
        self._conn.commit()

    def select(self, entity_t: Type[DataBaseEntity]) -> List[DataBaseEntity]:
        """
        Provides simple interface for selecting rows with all columns for
        specified entity type.
        """
        self._cursor.execute(SELECT_FROM.format(table=_TABLE_NAMES_MAP[entity_t]))
        return [entity_t(*values) for values in self._cursor.fetchall()]
