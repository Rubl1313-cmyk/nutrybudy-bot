import sys
print('Python version:', sys.version)

try:
    import aiogram
    print('aiogram version:', aiogram.__version__)
except Exception as e:
    print('aiogram error:', e)

try:
    import sqlalchemy
    print('sqlalchemy version:', sqlalchemy.__version__)
except Exception as e:
    print('sqlalchemy error:', e)

try:
    from database.db import engine, Base
    print('Database engine: OK')
except Exception as e:
    print('Database engine error:', e)

try:
    from database.models import User, WeightEntry
    print('Models: OK')
except Exception as e:
    print('Models error:', e)

try:
    from database.migrations import run_migrations
    print('Migrations: OK')
except Exception as e:
    print('Migrations error:', e)

try:
    from utils.error_middleware import ErrorHandlingMiddleware
    print('Error middleware: OK')
except Exception as e:
    print('Error middleware error:', e)

print('All imports checked successfully!')
