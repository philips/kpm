import sys
import kpm


kpm.setup_models(sys.modules[__name__], kpm.models_path, kpm.models_module)
