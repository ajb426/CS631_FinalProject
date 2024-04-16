from django.core.management.base import BaseCommand
from django.db import connection
import MySQLdb


class Command(BaseCommand):
    """
    Custom Django management command to drop a MySQL database as specified in the Django settings.

    This command connects to the MySQL server using the credentials provided in Django's settings and
    executes a SQL command to safely drop the database if it exists. It handles all MySQL errors
    associated with the database drop operation, providing feedback on success or failure.

    Usage:
        python manage.py drop_database

    Exceptions:
        MySQLdb.Error: Handles MySQL errors related to connectivity issues, permissions, or SQL syntax errors
                       during the database drop command.
       """

    help = 'Drops the database'

    def handle(self, *args, **options):
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_pass = connection.settings_dict['PASSWORD']
        db_host = connection.settings_dict['HOST']

        try:
            db = MySQLdb.connect(db_host, db_user, db_pass)
            cursor = db.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            cursor.close()
            db.commit()
            db.close()
            self.stdout.write(self.style.SUCCESS(f'Successfully dropped database {db_name}'))
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f'Failed to drop database: {str(e)}'))
