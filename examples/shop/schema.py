import json

import click
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from pgsync.base import create_database, pg_engine
from pgsync.helper import teardown
from pgsync.utils import get_config

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class ContactItem(Base):
    __tablename__ = 'contact_items'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    contactID = sa.Column(sa.Integer, sa.ForeignKey(Contact.id), nullable=False)
    contact = sa.orm.relationship(
        Contact,
        backref=sa.orm.backref('contact_item_contact')
    )


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    contactID = sa.Column(sa.Integer, sa.ForeignKey(Contact.id), nullable=False)
    contact = sa.orm.relationship(
        Contact,
        backref=sa.orm.backref('user_contact')
    )


class Product(Base):
    __tablename__ = 'products'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    sellerID = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)
    seller = sa.orm.relationship(
        User,
        backref=sa.orm.backref('product_seller'),
        foreign_keys=[sellerID]
    )
    renterID = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=True)
    renter = sa.orm.relationship(
        User,
        backref=sa.orm.backref('product_renter'),
        foreign_keys=[renterID]
    )


def setup(config=None):
    for document in json.load(open(config)):
        database = document.get('database', document['index'])
        create_database(database)
        engine = pg_engine(database=database)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


@click.command()
@click.option(
    '--config',
    '-c',
    help='Schema config',
    type=click.Path(exists=True),
)
def main(config):

    config = get_config(config)
    teardown(config=config)
    setup(config)


if __name__ == '__main__':
    main()
