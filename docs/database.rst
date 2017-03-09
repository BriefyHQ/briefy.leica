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


Financial Reports
+++++++++++++++++

After restore the production database to the local machine, one you can rum the report using the command::

    cd briefy.leica
    source env/bin/activate
    source .env_dist
    python src/briefy/leica/tools/finance_csv_export.py

Two files will be exported to the `/tmp` folder::

    orders.csv
    assignments.csv


Agoda SFTP delivery
+++++++++++++++++++

To run the agoda SFTP delivery is necessary first to do the procedure above.
Backup and restore of the production database and export the `orders.csv` file.

After this is necessary to copy the `orders.csv` file to the `delivery` server::

    scp /tmp/orders.csv delivery:/tmp

And next connect via ssh to the `delivery` server::

    ssh delivery

Again, `delivery` is the ssh config alias to `delivery.briefy.co`.
Inside the server fisrt is necessary to became `root` user::

    sudo su

And them copy the `orders.csv` to the /data/input directory::

    cp /tmp/orders.csv /data/input/

Finally go to the virtualenv for scripts and run the delivery script::

    cd /data/scripts/
    source env/bin/activate
    source .env
    python delivery_sftp_agoda.py

ER diagram
++++++++++

Complete database models ER diagram.


.. sadisplay::
    :module: briefy.leica.models
    :link:
    :alt: Briefy Leica database models diagram.
    :render: graphviz
