# Flask
DEBUG = True
SECRET_KEY = 'development_key'

# Debug toolbar
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
WTF_CSRF_ENABLED = False
CSRF_ENABLED = False

# Email logging settings
MAIL_SERVER = "smtp.umcn.nl"
MAIL_SMTP_PORT = 25
MAIL_FROM = "kmad-web@cmbi.umcn.nl"
MAIL_TO = ["Coos.Baakman@radboudumc.nl", "Jon.Black@radboudumc.nl",
           "jlange@bio-prodict.nl"]
