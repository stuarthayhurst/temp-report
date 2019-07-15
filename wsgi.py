activate_this = '/apps/www/temp-report/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__ = activate_this))

import os, sys
sys.path.insert(0, '/apps/www/temp-report/web')
os.chdir("/apps/www/temp-report/web")

from tempweb import app as application

if __name__ == "__main__":
    application.run()

