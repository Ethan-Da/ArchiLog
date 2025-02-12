from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import Uuid
from sqlalchemy import String
from sqlalchemy import Float

import uuid

from dataclasses import dataclass

@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(
            id,
            name,
            amount,
            category,
        )


engine = None
metadata = MetaData()
budget_table = Table(
            "budget",
            metadata,
            Column("id", Uuid, primary_key=True, default=uuid.uuid4),
            Column("name", String, unique=True, nullable=False),
            Column("amount", Float, nullable=False),
            Column("category", String, nullable=True),
        )

def get_engine():
    global engine
    if engine is None:
        engine = create_engine("sqlite:///data.db", echo=True)
    return engine


def init_db():
    metadata.create_all(get_engine())




def create_entry(name: str, amount: float, category: str | None = None) -> None:
    stmt = budget_table.insert()
    if category is None:
        stmt = stmt.values(name=name, amount=amount)
    else:
        stmt = stmt.values(name=name, amount=amount, category=category)
    with get_engine().begin() as conn:
        conn.execute(stmt)


def get_entry(id: uuid.UUID) -> Entry:

    stmt = select(budget_table).where(budget_table.c.id == id)

    with get_engine().begin() as conn:
        result = conn.execute(stmt)
        if result:

            return Entry.from_db(*result.fetchone())
        else:
            raise Exception(f"No entry with id {id}")



def get_all_entries() -> list[Entry]:

    stmt = select(budget_table)

    with get_engine().begin() as conn:
        result = conn.execute(stmt)
        if result:
            return [Entry.from_db(*r) for r in result]
        else:
            raise Exception("No entry in the database")


def update_entry(id: uuid.UUID, name: str | None, amount: float | None, category: str | None) -> None:
    stmt = budget_table.update().where(budget_table.c.id == id)
    if name:
        stmt = stmt.values(name=name)
    if category:
        stmt = stmt.values(category=category)
    if amount:
        stmt = stmt.values(amount=amount)
    
    with get_engine().begin() as conn:
        conn.execute(stmt)


def delete_entry(id: uuid.UUID) -> None:

    stmt = delete(budget_table).where(budget_table.c.id == id)

    with get_engine().begin() as conn:
        conn.execute(stmt)
