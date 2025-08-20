from os import environ

SESSION_CONFIGS = [
    dict(
        name='econ3310_risk',
        display_name='ECON 3310 Risky Investment',
        app_sequence=['econ3310_risk'],
        num_demo_participants=4,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'changeme')
OTREE_AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL', 'STUDY')

DEMO_PAGE_INTRO_HTML = """
<p>ECON 3310 Risky Investment experiment (10 rounds, one paying round).</p>
"""
