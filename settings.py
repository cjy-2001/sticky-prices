from os import environ


SESSION_CONFIGS = [
    dict(
        name='sticky_prices',
        display_name="Sticky Prices Experiment",
        app_sequence=['sticky_prices'],
        num_demo_participants=5
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ Experiment',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Real Experiment (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here is a behavior experiment for studying the sticky prices theory.
"""


SECRET_KEY = '9155047638033'

INSTALLED_APPS = ['otree']
