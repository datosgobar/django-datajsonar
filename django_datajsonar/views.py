from django.contrib.auth.decorators import login_required

from .models import Dataset
from .utils import download_config_csv


@login_required(login_url='/admin/login')
def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)
