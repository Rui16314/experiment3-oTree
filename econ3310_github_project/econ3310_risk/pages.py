from otree.api import *
from .models import C, Subsession, Group, Player
import statistics

class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Demographics(Page):
    form_model = 'player'
    form_fields = ['name','gender','age','race']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Decision(Page):
    form_model = 'player'
    form_fields = ['x']
    timeout_seconds = C.DECISION_TIMEOUT

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.x is None:
            player.x = 0
        player.set_outcome()
        player.set_payoff_if_paying_round()

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            outcome_text='Heads (WIN)' if player.win else 'Tails (LOSE)',
            avg_x=round(player.average_x(), 1),
        )

class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        R = player.participant.vars.get('paying_round')
        selected = player.in_round(R)
        history = [dict(round=r.round_number, x=r.x, win=r.win, wealth=r.wealth)
                   for r in player.in_all_rounds()]
        return dict(paying_round=R, selected_wealth=selected.wealth,
                    avg_x=round(player.average_x(), 2), history=history)

# Admin report (table-based summaries usable for copy/paste to Excel)
def vars_for_admin_report(subsession: Subsession):
    players = subsession.get_players()
    seen, rows = set(), []
    for p in players:
        code = p.participant.code
        if code in seen:
            continue
        seen.add(code)
        rows.append(dict(
            code=code,
            name=p.name or '',
            gender=p.gender or '',
            age=p.age if p.age is not None else '',
            race=p.race or '',
            avg_x=round(p.average_x(), 2),
        ))

    def make_hist(rows, bin_size, gender=None):
        labels, counts, names = [], [], []
        for lo in range(0, 100, bin_size):
            hi = lo + bin_size
            label = f'{lo}-{hi}' if hi <= 100 else f'{lo}-100'
            w = [r for r in rows if (gender is None or r['gender']==gender)
                 and r['avg_x'] is not None
                 and r['avg_x'] >= lo and (r['avg_x'] < hi or (hi>=100 and r['avg_x']<=100))]
            labels.append(label)
            counts.append(len(w))
            names.append(', '.join([rr['name'] or rr['code'] for rr in w]) or '—')
        return labels, counts, names

    labels5, counts5, names5 = make_hist(rows, 5)
    labels10, counts10, names10 = make_hist(rows, 10)
    labels20, counts20, names20 = make_hist(rows, 20)

    genders = sorted(set([r['gender'] for r in rows if r['gender']]))
    avg_by_gender = []
    for g in genders:
        vals = [r['avg_x'] for r in rows if r['gender']==g]
        avg_by_gender.append((g, round(statistics.mean(vals),2) if vals else 0))

    ages = sorted(set([r['age'] for r in rows if r['age'] not in ['', None]]))
    avg_by_age = []
    for a in ages:
        vals = [r['avg_x'] for r in rows if r['age']==a]
        avg_by_age.append((a, round(statistics.mean(vals),2) if vals else 0))

    races = sorted(set([r['race'] for r in rows if r['race']]))
    avg_by_race = []
    for rc in races:
        vals = [r['avg_x'] for r in rows if r['race']==rc]
        avg_by_race.append((rc, round(statistics.mean(vals),2) if vals else 0))

    return dict(
        rows=rows,
        labels5=labels5, counts5=counts5, names5=names5,
        labels10=labels10, counts10=counts10, names10=names10,
        labels20=labels20, counts20=counts20, names20=names20,
        avg_by_gender=avg_by_gender,
        avg_by_age=avg_by_age,
        avg_by_race=avg_by_race,
    )

# Optional extra: Charts page for admins
class Charts(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        by_code = {}
        for p in player.subsession.get_players():
            code = p.participant.code
            if code in by_code: 
                continue
            xs = [r.x for r in p.in_all_rounds() if r.x is not None]
            avg_x = statistics.mean(xs) if xs else None
            by_code[code] = dict(name=p.name or code, gender=p.gender or 'Unknown',
                                 age=p.age, race=p.race or 'Unknown', avg_x=avg_x)
        rows = list(by_code.values())

        def hist(rows, bin_size):
            labels, counts = [], []
            lo = 0
            while True:
                hi = lo + bin_size
                if hi >= 100:
                    hi = 100
                label = f"{lo}-{hi}"
                cnt = 0
                for r in rows:
                    v = r['avg_x']
                    if v is None: 
                        continue
                    if v >= lo and ((v < hi) or (hi == 100 and v <= 100)):
                        cnt += 1
                labels.append(label); counts.append(cnt)
                if hi == 100:
                    break
                lo = hi
            return labels, counts

        labels5, counts5 = hist(rows, 5)
        labels10, counts10 = hist(rows, 10)
        labels20, counts20 = hist(rows, 20)

        gvals = {}
        for r in rows:
            v = r['avg_x']
            if v is None: 
                continue
            g = r['gender']
            gvals.setdefault(g, []).append(v)
        labels_gender = sorted(gvals.keys())
        values_gender = [round(sum(gvals[g])/len(gvals[g]),2) for g in labels_gender]

        avals = {}
        for r in rows:
            v = r['avg_x']; a = r['age']
            if v is None or a in [None, '']:
                continue
            avals.setdefault(a, []).append(v)
        labels_age = sorted(avals.keys())
        values_age = [round(sum(avals[a])/len(avals[a]),2) for a in labels_age]

        rvals = {}
        for r in rows:
            v = r['avg_x']; rc = r['race']
            if v is None or not rc:
                continue
            rvals.setdefault(rc, []).append(v)
        labels_race = sorted(rvals.keys())
        values_race = [round(sum(rvals[rc])/len(rvals[rc]),2) for rc in labels_race]

        return dict(
            labels5=labels5, counts5=counts5,
            labels10=labels10, counts10=counts10,
            labels20=labels20, counts20=counts20,
            labels_gender=labels_gender, values_gender=values_gender,
            labels_age=labels_age, values_age=values_age,
            labels_race=labels_race, values_race=values_race,
        )

page_sequence = [Instructions, Demographics, Decision, Results, FinalResults, Charts]
