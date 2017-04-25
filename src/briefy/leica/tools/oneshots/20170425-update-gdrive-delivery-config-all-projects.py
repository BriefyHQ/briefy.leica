"""Make sure all Projects have the gdrive delivery config in the database."""
from briefy.leica.db import Session
from briefy.leica.models import Project
from briefy.leica.sync.db import configure
from pprint import pprint

import transaction


PROJECT_FOLDERS = {
    '648cb92d-6f14-4d7b-98e6-d0f7c65a99b9': {
        'name': 'Leisure Group Belvilla IT',
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg',
        'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    'daae8dc3-b8b8-49b4-8c09-6e5dd64c29de': {
        'name': 'Leisure Group Belvilla ES',
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg',
        'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '18f2d83f-b124-4825-a967-43fb031868ed': {
        'name': 'Leisure Group Belvilla FR',
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg',
        'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '674e1d10-4989-4600-b082-acd30dc0d5a4': {
        'name': 'Leisure Group Belvilla DE',
        'archive': '0B2QYuPa8WdDseW11UkwyOWlpUzg',
        'delivery': '0B2QYuPa8WdDsSXU5RHRXMHZvcVU'
    },
    '0f3accec-946c-43d7-8935-44223cbd3553': {
        'name': 'Agoda Re-shoot / New shoot',
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU',
        'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '4e7976d5-1a7f-4cfa-b6ba-08356bc7f162': {
        'name': 'Agoda Phuket',
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU',
        'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '6bc29461-8a6e-4d10-bd54-f48d498f7776': {
        'name': 'Agoda Pattaya',
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU',
        'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c': {
        'name': 'Agoda Bangkok',
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU',
        'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    '1dafb433-9431-4295-a349-92c4ad61c59e': {
        'name': 'Agoda Bali',
        'archive': '0BwrdIL719n7wSnVKX05iOUlCdlU',
        'delivery': '0BwrdIL719n7wVURQUC1VS2VKY0E'
    },
    'd1f38481-597a-4223-b059-37f13603eb09': {
        'name': 'Aladinia Spa Project (Pilot)',
        'archive': '0BwrdIL719n7wajZqMkp6TVFNRjA',
        'delivery': '0BwrdIL719n7wV2h5MVFBNnViaWc'
    },
    'ff9e8a4b-27ae-474f-94b5-148316ebd0c9': {
        'name': 'Auctionata',
        'archive': '0BwrdIL719n7wb3U2cm9uZENmRFU',
        'delivery': '0BwrdIL719n7wU3U2dkZGdFVvRkE'
    },
    '49f8b115-00f2-415e-a417-c4ecd5395be6': {
        'name': 'Beauty Spotter Clinics',
        'archive': '0B2QYuPa8WdDsY01uYl9ESVhsMkE',
        'delivery': '0B2QYuPa8WdDsWU5sT3d6TGNqOW8'
    },
    '6875b534-67ac-469d-979a-e5d7f4d147e5': {
        'name': 'Classic Driver Pilot',
        'archive': '0B2QYuPa8WdDsX2JQUlpNamRmcVU',
        'delivery': '0B2QYuPa8WdDsdVdDYXZiUTdyUUE'
    },
    'd53f54fe-580e-4ab1-8f0e-abda90eff210': {
        'name': 'Deliveroo Behind the Scene',
        'archive': '0BwrdIL719n7wZmZuMzNWbFRWbjg',
        'delivery': '0BwrdIL719n7wZWtCLTZ0Mk5oMWM'
    },
    '1c44a368-ee9b-4289-ae20-6a28c28149c0': {
        'name': 'eH Visio Clinics',
        'archive': '0BwrdIL719n7waGRibl90Y0luU2c',
        'delivery': '0BwrdIL719n7wMC1CN25QUnZndWc'
    },
    '92c4cf14-f4bf-4747-9661-3008d4210ad3': {
        'name': 'Erento',
        'archive': '0BwrdIL719n7wRDVCUzIyMjdJb28',
        'delivery': '0BwrdIL719n7wYndhRzZBUTQ4ZXM'
    },
    '957decc9-4136-43d0-9695-ed130ad610e1': {
        'name': 'Everphone Business Portrait',
        'archive': 'None',
        'delivery': 'None'
    },
    'ac219357-0273-4e54-ab57-470cbf2467e3': {
        'name': 'ezCater USA',
        'archive': '0B2QYuPa8WdDsY2Y0WjN5M1NTaTQ',
        'delivery': '0B1Cpa54F2k6vOWdLXzZqenZhSXM'
    },
    '7348609b-23a3-43b2-a9c6-9db698c25cf7': {
        'name': 'Foodora Wien',
        'archive': '0BwrdIL719n7wZUhyaXdvek85bzA',
        'delivery': '0BwrdIL719n7wQ1pxN2xlWDB0SHc'
    },
    'e9dfde01-52f6-47b1-866a-b1cdade1baed': {
        'name': 'Homeday Properties',
        'archive': 'None',
        'delivery': 'None'
    },
    '93e0dc8f-1d12-4821-884c-72040c7e2e82': {
        'name': 'Homeday Portraits',
        'archive': '0BwrdIL719n7waVRIVjRhQ0FtSVk',
        'delivery': '0BwrdIL719n7wQUc5ZW9hNXBfU1k'
    },
    '445f0569-ddf5-4b18-860a-ff29db3d220a': {
        'name': 'Just Eat finalists UK',
        'archive': '0BwrdIL719n7wTXN3VGNycktPenc',
        'delivery': '0BwrdIL719n7wMERDZExxREwyQ28'
    },
    '79fbb63a-77a0-456b-160f-41070bd816e9': {
        'name': 'JustEat Test shoots for order pad',
        'archive': '0BzvG5TCRc3cbVlBfTEp6S3c2Nzg',
        'delivery': '0BzvG5TCRc3cbUkNsOXVoY1RIcUE'
    },
    '532c6775-3431-4af4-8448-6978e8d76185': {
        'name': 'Love Home Swap',
        'archive': '0BwrdIL719n7wVkVERC1pYkNCZk0',
        'delivery': '0BwrdIL719n7wSmUwLWhSM0p1bUU'
    },
    'a130b920-6269-4f5e-ae1d-b73e0fce95ff': {
        'name': 'Stayz Australia',
        'archive': '0B2QYuPa8WdDsdld6aktydV9JU2c',
        'delivery': '0B2QYuPa8WdDsaHVJeWdIdWdZYjg'
    },
    '1df6f838-1fcb-48ac-9034-40126f469a18': {
        'name': 'WeTravel Yoga',
        'archive': '0BwrdIL719n7wVks2RmtwRjdIUkU',
        'delivery': '0BwrdIL719n7wWTRzVWRKdFV2TXc'
    },
    'd347be4c-eddc-4d9d-9fd8-4bbd24d3e13b': {
        'name': 'Wolt',
        'archive': '0BwrdIL719n7wYWxNN0F4QnBXbHc',
        'delivery': '0BwrdIL719n7wMkpXMmhfWDY4bkU'
    },
    '0e0dd21a-d948-4212-aaae-dedb5f8efb8d': {
        'name': 'Delivery Hero Munich',
        'archive': '0B6bhERF4B_DpaG5pVEQ4QkZab3c',
        'delivery': '0B6bhERF4B_DpYUo2MUhFR3ZjOHc'
    },
    '51549a8e-918e-4cc3-ad21-ffd4ead0a74e': {
        'name': 'Delivery Hero Hamburg',
        'archive': '0B6bhERF4B_DpM0ozRjhXX3E5UHM',
        'delivery': '0B6bhERF4B_DpNTJZRFJJQWZJWnM'
    },
    '78246086-ae6d-424c-b77e-aa7a8cb81035': {
        'name': 'Delivery Hero Cologne',
        'archive': '0B6bhERF4B_DpWGdCdmFhRVFrNGM',
        'delivery': '0B6bhERF4B_DpdTBOMW95TlFDeFE'
    },
    '76034e1e-e0f6-44c4-d829-6523303de29e': {
        'name': 'Parting - funeral homes',
        'archive': '0B6bhERF4B_Dpa0V4MmtSMkt0bk0',
        'delivery': '0B6bhERF4B_DpTDBDdFdlbVFXWms'
    },
}

APPROVE_TEMPLATE = {
    'archive': {
        'driver': 'gdrive',
        'images': True,
        'name': 'order.customer_order_id',
        'other': True,
        'parentId': None,
        'resize': [],
        'subfolders': True
    },
    'gdrive': {
        'driver': 'gdrive',
        'images': True,
        'name': 'order.customer_order_id',
        'other': False,
        'parentId': None,
        'resize': [],
        'subfolders': False
    }
}


def main():
    """Update Projects delivery config."""
    for project_id, project_folders in PROJECT_FOLDERS.items():
        folder_gdrive = project_folders.get('delivery')
        folder_archive = project_folders.get('archive')
        project = Project.get(project_id)
        print(project.title)
        if project.delivery:
            delivery_config = project.delivery.copy()
            pprint(delivery_config)
            approve_config = delivery_config.get('approve')
            if approve_config:
                archive_config = approve_config.get('archive')
                if archive_config.get('parentId') != folder_archive:
                    print('Different config for archive.')
                gdrive_config = approve_config.get('gdrive')
                if gdrive_config.get('parentId') != folder_gdrive:
                    print('Different config for gdrive.')
            else:
                print('No config for approve. Status: {status}'.format(status=project.state))
                approve_config = APPROVE_TEMPLATE.copy()
                approve_config['archive']['parentId'] = folder_archive
                approve_config['gdrive']['parentId'] = folder_gdrive
                delivery_config['approve'] = approve_config
                project.delivery = delivery_config
        else:
            print('No delivery config. Status: {status}'.format(status=project.state))


if __name__ == '__main__':
    configure(Session)
    with transaction.manager:
        main()
