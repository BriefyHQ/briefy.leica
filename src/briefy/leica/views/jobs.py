"""Views to handle Job handling"""
from briefy.leica.config import EXTRA_BACKEND
from briefy.leica.models import Asset
# from briefy.leica.validators import AssetSchema
from briefy.ws import CORS_POLICY
from cornice import Service
# from sqlalchemy import event
# from sqlalchemy import func as sa_func

import transaction

asset = Service(
    name='job_qa',
    path='/job_qa/{id:.*}',
    cors_policy=CORS_POLICY
)


def backend_job(id):
    try:
        job = Jobs.query.get(id)
    except ValueError:
        if not 'knack' not in EXTRA_BACKEND:
            raise
        knack_job = knack.job.query.get(id)

        job = knacl
        # Try to fetch Job from alternate backend
    return {"id":"54353453453543", "jobname": "Amazing Job",
 "project_brief": "http://www.nikonsupport.eu/europe/Manuals/2UjJ8GNWcr/D700_de.pdf",
 "info": "Information about the job",
 "job_requirements": {"non-tech": {"Kitchen": 2,
                                   "Bedroom": 2,
                                   "Living room": 2,
                                   "Dinning room": 2},
                      "tech": {"Resolution": "Awaiting for approval",
                               "ISO": "01-10-2016 02:30PM",
                               "Aperture": "2.8",
                               "Shutter speed": "1/1000",
                               "Number of photos": "34/30"}},
  "images": [
      {
          "id": 1,
          "name": "Portugal",
          "filename": "portugal.jpg",
          "sizes": {
                "thumb": {"size": [150,150], "url": "https://farm1.staticflickr.com/597/21275434659_a44c44a76f_q_d.jpg"},
                "medium": {"size": [640,427], "url": "https://farm1.staticflickr.com/597/21275434659_a44c44a76f_z_d.jpg"},
                "original": {"size": [6000,4000], "url": "https://farm1.staticflickr.com/597/21275434659_eb4eda4d6b_o_d.jpg"}
          },
          "state": "Approved"
      },
          ]

}

@asset.get()
def get_job(request):
    """Get information about a Job as needed by the UI"""
    id = request.matchdict.get('id', '')
    job =  backend_get_job()
    #import pdb; pdb.set_trace()

    return job


