from django.core.management.base import BaseCommand
from django.db import connection
import MySQLdb

class Command(BaseCommand):
    """
    Custom Django management command to assign the 'admin' role to a specified user in the database.

    This command updates the 'role' field of a specified user in the 'user' table of your database to 'admin'.
    It ensures the query is safely parameterized to prevent SQL injection.

    Usage:
        python manage.py gives_admin_role <username>

    Args:
        username (str): The username of the user to which the admin role will be assigned.
    """

    help = 'Gives Admin Role'
    def add_arguments(self, parser):
        # Adding a named (optional) argument
        parser.add_argument('username', type=str, help='The username to grant admin role')

    def handle(self, *args, **options):
        # Retrieve the username argument
        username = options['username']
        # Retrieve db connection info
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_pass = connection.settings_dict['PASSWORD']
        db_host = connection.settings_dict['HOST']

        try:
            db = MySQLdb.connect(db_host, db_user, db_pass, db_name)
            cursor = db.cursor()
            # Properly parameterize the query to prevent SQL injection
            query = "UPDATE user SET role = 'admin' WHERE Username = %s"
            cursor.execute(query, (username,))
            db.commit()
            cursor.close()
            db.close()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated role for user {username}'))
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f'Failed to update role: {str(e)}'))
