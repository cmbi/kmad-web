# Flask
DEBUG = False
SECRET_KEY = 'development_key'

# Debug toolbar
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
WTF_CSRF_ENABLED = False
CSRF_ENABLED = False

# Email logging settings
MAIL_SERVER = "131.174.165.22"
MAIL_SMTP_PORT = 25
MAIL_FROM = "kmad-web@cmbi.umcn.nl"
MAIL_TO = ["j.lange@radboudumc.nl"]
