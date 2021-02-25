# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:05:55
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:05:56

from flask_sqlalchemy import SQLAlchemy

from models import metadata

db = SQLAlchemy(metadata=metadata)
