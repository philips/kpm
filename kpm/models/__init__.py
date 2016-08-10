import sys
import kpm


class Package(object):
    pass


class Channel(object):
    pass


kpm.setup_models(sys.modules[__name__], kpm.models_path, kpm.models_module)
