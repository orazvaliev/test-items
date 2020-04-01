import abc
import sqlite3
from typing import Sequence


class AbstractCursor(abc.ABC):
    @abc.abstractmethod
    def close(self) -> None:
        pass

    @abc.abstractmethod
    def fetchone(self) -> Sequence:
        pass

    @abc.abstractmethod
    def fetchall(self) -> Sequence[Sequence]:
        pass

    @abc.abstractmethod
    def execute(self, query: str, *args, **kwargs) -> None:
        pass


class DatabaseConnection(abc.ABC):
    @abc.abstractmethod
    def commit(self) -> None:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass

    @abc.abstractmethod
    def cursor(self) -> AbstractCursor:
        pass

    @abc.abstractmethod
    def create_backup(self, *args, **kwargs) -> "DatabaseConnection":
        pass


class SqlLiteCursor(AbstractCursor):
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self._cursor.close()

    def fetchone(self) -> Sequence:
        return self._cursor.fetchone()

    def fetchall(self) -> Sequence[Sequence]:
        return self._cursor.fetchall()

    def execute(self, query: str, **parameters) -> None:
        self._cursor.execute(query, parameters)


class SqlLiteConnection(DatabaseConnection):
    def __init__(self, database: str):
        self._conn = sqlite3.connect(database)
        self._db = database

    def close(self) -> None:
        self._conn.close()

    def cursor(self) -> AbstractCursor:
        return SqlLiteCursor(self._conn.cursor())

    def commit(self) -> None:
        self._conn.commit()

    def create_backup(self, name="backup.db") -> "SqlLiteConnection":
        backup = SqlLiteConnection(name)
        self._conn.backup(backup._conn)
        return backup

    def __repr__(self):
        return "%s(database=%s)" % (type(self).__name__, self._db)
