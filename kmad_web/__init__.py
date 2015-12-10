import logging

from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail


# Create the top-level logger. This is required because Flask's built-in method
# results in loggers with the incorrect level.
_log = logging.getLogger(__name__)

toolbar = DebugToolbarExtension()
mail = Mail()
