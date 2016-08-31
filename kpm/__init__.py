# -*- coding: utf-8 -*-
import os
from kpm.utils import symbol_by_name

__author__ = 'Antoine Legrand'
__email__ = '2t.antoine@gmail.com'
__version__ = '0.21.1'


def version(registry_host=None):
    import requests
    from kpm.registry import Registry
    api_version = None
    ctl_version = __version__
    try:
        r = Registry(registry_host)
        response = r.version()
        api_version = response
    except requests.exceptions.RequestException:
        api_version = ".. Connection error"

    return {'api-version': api_version,
            "client-version": ctl_version}

models_path = {
    'Package': '{models_module}.package:Package',
    'Channel': '{models_module}.channel:Channel',
}

models_module = os.getenv('KPM_MODELS_MODULE', "kpm.models.etcd")


def setup_models(importlib, models=None, module=None):
    """Attach all model classes given by `models_path` to `importlib`."""
    if models is None:
        models = models_path
    if module is not None:
        models = {k: v.format(models_module=models_module) for k, v in models.iteritems()}
    importlib.__all__ = []
    for class_name, path in models.iteritems():
        orm_cls = symbol_by_name(path)
        setattr(importlib, class_name, orm_cls)
        importlib.__all__.append(class_name)
