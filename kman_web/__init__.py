import logging

from flask_debugtoolbar import DebugToolbarExtension


# Create the top-level logger. This is required because Flask's built-in method
# results in loggers with the incorrect level.
_log = logging.getLogger(__name__)

toolbar = DebugToolbarExtension()
