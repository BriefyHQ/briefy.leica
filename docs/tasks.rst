Tasks
--------

Agoda SFTP delivery
+++++++++++++++++++

To run the agoda SFTP delivery is necessary first to obtain an export of the orders -- `orders.csv` file.

After this, copy the `orders.csv` file to the `delivery` server::

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

After the script finish the processing of the orders to be delivered we need to get the output on::

    /data/output

And the output will be a python list with the data to be updated on the database.
We need to go to the Leica console on production, load the python list on the console and run the following code::

    from briefy.leica.models import Order
    import transaction

    for link in sftp_links:
        id, sftp = link
        order = Order.get(id)
        # necessary to copy so new instance will trigger sqlalchemy update
        delivery = order.delivery.copy()
        delivery['sftp'] = sftp
        order.delivery = delivery

    transaction.commit()

The above example assume the list in the output file will look like this::

    sftp_links = [
        ('00dc0f1b-db77-48b3-b1e2-736ebae14e22', 'sftp://agoda@delivery.briefy.co/agoda_phuket/779219'),
        ('020a8d72-6f18-42b5-8dad-d31692859e34', 'sftp://agoda@delivery.briefy.co/agoda_phuket/337256'),
        ('0328c4de-2c40-42b2-9548-f5e70f9c98c0', 'sftp://agoda@delivery.briefy.co/agoda_phuket/85645'),
        ('04a493a0-64a4-4bc7-8828-bd4241a4d091', 'sftp://agoda@delivery.briefy.co/agoda_bangkok/287269'),
        ('05a1ad7c-ae46-4d7f-8bc2-41c4686900ed', 'sftp://agoda@delivery.briefy.co/agoda_phuket/295801'),
    ]

