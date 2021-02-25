# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:07:49
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:07:51
import os

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

POSTGRES = {
    "user": os.environ.get("DB_USER", None),
    "pw": os.environ.get("DB_PASSWORD", None),
    "db": os.environ.get("DB_SCHEMA", None),
    "host": os.environ.get("DB_HOST", None),
    "port": os.environ.get("DB_PORT", None),
}

engine = create_engine("postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
