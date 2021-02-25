#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:03:23
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:03:29

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from server import app, db

migrate = Migrate(app, db)

manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
