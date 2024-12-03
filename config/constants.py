import os

# Application Metadata (These could be user-defined at runtime)
COMPANY = "Bentraining"  # Default value
APP_NAME = "FleetManager"  # Default value
VERSION = "v1"  # Default value

def set_app_metadata(varname, varvalue):
    """
    Sets or updates an application constant value dynamically.

    :param varname: The name of the variable to set or update.
    :param varvalue: The value to assign to the variable.
    """
    globals()[varname] = varvalue