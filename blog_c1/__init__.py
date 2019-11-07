import pymysql
# 告诉django用pymysql代替默认的mysqldb
pymysql.install_as_MySQLdb()