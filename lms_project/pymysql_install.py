# PyMySQL adapter for Django MySQL backend
# This allows PyMySQL to work with django.db.backends.mysql

import pymysql
pymysql.install_as_MySQLdb()
