from django.core.management.base import BaseCommand
from django.db import connection
import MySQLdb


class Command(BaseCommand):
    """
    Custom Django management command to create a MySQL database as specified in the Django settings.

    This command establishes a connection to the MySQL server using credentials from Django's settings
    and attempts to create a new database with the name specified in those settings. If the database
    creation is successful, it prints a success message; otherwise, it catches and reports any MySQL
    errors.

    Usage:
        python manage.py create_database

    Exceptions:
        MySQLdb.Error: Handles general MySQL errors related to connectivity issues, permissions, or
                       SQL syntax errors in the database creation command.
    """

    help = 'Creates the database'
    def handle(self, *args, **options):
        #fetch db credentials
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_pass = connection.settings_dict['PASSWORD']
        db_host = connection.settings_dict['HOST']

        try:
            db = MySQLdb.connect(db_host, db_user, db_pass)
            cursor = db.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.close()
            db.commit()
            db.close()
            self.stdout.write(self.style.SUCCESS(f'Successfully created database {db_name}'))
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f'Failed to create database: {str(e)}'))
