Database
--------

Backup and Restore
++++++++++++++++++

Todo the backup of the production database you can run the following command::

    ssh live
    sudo su - admin
    pg_dump -Fc -h briefy-services.cbpyycv8xvtn.eu-central-1.rds.amazonaws.com \
    -p 5432 -U leica_usr --exclude-schema=tiger --exclude-schema=topology \
    -d leica > /tmp/production-leica.dump
    sudo chmod 0644 /tmp/production-leica.dump


You need to inform the `leica_usr` password to dump the database to file, look in the path::

    /home/admin/BriefyHQ/briefy.leica/.env

Next step is download de database from your local machine::

    scp live:/tmp/production-leica.dump /tmp/production-leica.dump


Where `live` is the ssh config alias for `bastion.live.briefy.co`.

To restore the database in to the postgresql docker running in your local machine
you can use the following command and inform the `briefy` usr password::

    pg_restore --no-owner -x -h localhost -p 9999 -U briefy -W -d briefy-leica /tmp/production-leica.dump

ER diagram
++++++++++

Complete database models ER diagram.


.. sadisplay::
    :module: briefy.leica.models
    :link:
    :alt: Briefy Leica database models diagram.
    :render: graphviz
