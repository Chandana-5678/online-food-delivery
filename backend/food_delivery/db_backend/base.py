from functools import cached_property
from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures as MySQLDatabaseFeatures


class DatabaseFeatures(MySQLDatabaseFeatures):
    """Allow the MariaDB 10.4 bundled with XAMPP for this project's conservative schema."""
    @cached_property
    def minimum_database_version(self):
        return (10, 4) if self.connection.mysql_is_mariadb else super().minimum_database_version

    @cached_property
    def can_return_columns_from_insert(self):
        # INSERT ... RETURNING arrived in MariaDB after the 10.4 XAMPP release.
        return False if self.connection.mysql_is_mariadb else super().can_return_columns_from_insert


class DatabaseWrapper(MySQLDatabaseWrapper):
    features_class = DatabaseFeatures
