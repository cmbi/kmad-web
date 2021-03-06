import logging
from logging.handlers import SMTPHandler

from celery import Celery
from flask import Flask, render_template


_log = logging.getLogger(__name__)


def create_app(settings=None):
    _log.info("Creating app")

    app = Flask(__name__, static_folder='frontend/static',
                template_folder='frontend/templates')
    app.config.from_object('kmad_web.default_settings')
    if settings:
        app.config.update(settings)
    else:  # pragma: no cover
        app.config.from_envvar('KMAD_WEB_SETTINGS')  # pragma: no cover

    # Set the maximum content length to 150MB. This is to allow large PDB files
    # to be sent in post requests. The largest PDB file found to date is 109MB
    # in size.
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 150

    # Ignore Flask's built-in logging
    # app.logger is accessed here so Flask tries to create it
    app.logger_name = "nowhere"
    app.logger

    # Configure logging.
    #
    # It is somewhat dubious to get _log from the root package, but I can't see
    # a better way. Having the email handler configured at the root means all
    # child loggers inherit it.
    from kmad_web import _log as root_logger
    from kmad_web.services.helpers.cache import cache_manager as cm

    cm.load_config(app.config['CACHE_CONFIG'])


    # Only log to email during production.
    if not app.debug and not app.testing:  # pragma: no cover
        mail_handler = SMTPHandler((app.config["MAIL_SERVER"],
                                   app.config["MAIL_SMTP_PORT"]),
                                   app.config["MAIL_FROM"],
                                   app.config["MAIL_TO"],
                                   "kmad_web failed")
        mail_handler.setLevel(logging.ERROR)
        root_logger.addHandler(mail_handler)
        mail_handler.setFormatter(
            logging.Formatter("Message type: %(levelname)s\n" +
                              "Location: %(pathname)s:%(lineno)d\n" +
                              "Module: %(module)s\n" +
                              "Function: %(funcName)s\n" +
                              "Time: %(asctime)s\n" +
                              "Message:\n" +
                              "%(message)s"))

    # Only log debug messages during development
    if not app.testing:
        # Only log to the console during development and production, but not
        # during testing.
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        if app.debug:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
        root_logger.propagate = False
    else:
        root_logger.setLevel(logging.DEBUG)

    # Use ProxyFix to correct URL's when redirecting.
    from kmad_web.middleware import ReverseProxied
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Register jinja2 filters
    from kmad_web.frontend.filters import beautify_docstring
    app.jinja_env.filters['beautify_docstring'] = beautify_docstring

    # Register blueprints
    from kmad_web.frontend.api.endpoints import bp as api_bp
    from kmad_web.frontend.dashboard.views import bp as dashboard_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('dashboard/404.html'), 404

    return app


def create_celery_app(app):  # pragma: no cover
    _log.info("Creating celery app")

    app = app or create_app()

    celery = Celery(__name__,
                    backend='amqp',
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    import kmad_web.tasks

    return celery
