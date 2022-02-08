import json

import click
from schema import Product, User, Contact, ContactItem
from sqlalchemy.orm import sessionmaker

from pgsync.base import pg_engine, subtransactions
from pgsync.helper import teardown
from pgsync.utils import get_config


@click.command()
@click.option(
    '--config',
    '-c',
    help='Schema config',
    type=click.Path(exists=True),
)
def main(config):

    config = get_config(config)
    teardown(drop_db=False, config=config)
    documents = json.load(open(config))
    engine = pg_engine(
        database=documents[0].get('database', documents[0]['index'])
    )
    Session = sessionmaker(bind=engine, autoflush=True)
    session = Session()

    contacts = {
        'contact1': Contact(id=1, name='contact1'),
    }
    with subtransactions(session):
        session.add_all(contacts.values())

    users = {
        'seller1': User(id=1, name='seller1', contact=contacts['contact1']),
    }
    with subtransactions(session):
        session.add_all(users.values())

    products = [
        Product(id=1, name='product1', seller=users['seller1']),
    ]
    with subtransactions(session):
        session.add_all(products)


if __name__ == '__main__':
    main()
