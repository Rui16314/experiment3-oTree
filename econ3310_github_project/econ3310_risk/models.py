from otree.api import *
import random
import statistics

doc = """
ECON 3310 Risky Investment experiment.
10 rounds. Endowment 100 points each round.
Risky asset pays 2.5x with probability 1/2, else 0.
One round is randomly selected for payment at the end.
"""

class C(BaseConstants):
    NAME_IN_URL = 'econ3310_risk'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    ENDOWMENT = cu(100)
    MULTIPLIER = 2.5
    DECISION_TIMEOUT = 60

class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            for p in self.get_players():
                p.participant.vars['paying_round'] = random.randint(1, C.NUM_ROUNDS)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Demographics (round 1 only)
    name = models.StringField(blank=True, label='Your name (optional)')
    gender = models.StringField(
        blank=True,
        choices=[('Man','Man'),('Woman','Woman'),('Other','Other')],
        widget=widgets.RadioSelect, label='Gender'
    )
    age = models.IntegerField(blank=True, min=16, max=120, label='Age')
    race = models.StringField(blank=True, label='Race/ethnicity (optional)')

    # Decision each round
    x = models.IntegerField(min=0, max=int(C.ENDOWMENT),
        label='How many of your 100 points do you invest in the risky asset?')

    # Outcomes
    win = models.BooleanField()
    wealth = models.CurrencyField()

    def set_outcome(self):
        self.win = random.choice([True, False])
        return_amount = C.MULTIPLIER * self.x if self.win else 0
        self.wealth = C.ENDOWMENT - self.x + return_amount

    def set_payoff_if_paying_round(self):
        paying_round = self.participant.vars['paying_round']
        self.payoff = self.wealth if self.round_number == paying_round else cu(0)

    def average_x(self):
        xs = [r.x for r in self.in_all_rounds() if r.x is not None]
        return statistics.mean(xs) if xs else 0
