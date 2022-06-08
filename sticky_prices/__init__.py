from otree.api import *


doc = """
Sticky prices experiment based on oTree.
Players will play as different firms and decide if they will change their prices given an upcoming cost shock; 
whoever gets the highest profit wins.
Served as a real-life experiment to test the Nominal Rigidity (or sticky prices) theory.
See https://www.nber.org/system/files/working_papers/w2327/w2327.pdf
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3
    NAME_IN_URL = 'sticky_prices'
    INSTRUCTIONS_TEMPLATE = 'sticky_prices/instructions.html'
    PRICE_MAX = cu(100)
    PAYMENT = 100

    INIT_PRICE = [cu(10)] * NUM_ROUNDS
    INIT_PRODUCT_COST = [cu(9.2)] * NUM_ROUNDS
    NEW_PRODUCT_COST = ([cu(8.7), cu(10.7), cu(8.7)])
    ALPHA = [cu(9)] * NUM_ROUNDS
    THETA = [cu(1.8)] * NUM_ROUNDS
    BETA = [cu(2.5)] * NUM_ROUNDS
    ADJUST_COST = [cu(3)] * NUM_ROUNDS


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    avg = models.CurrencyField()
    best_price = models.CurrencyField()
    best_profit = models.CurrencyField()
    num_winners = models.IntegerField()

    init_price = models.CurrencyField()
    cost = models.CurrencyField()
    alpha = models.CurrencyField()
    theta = models.CurrencyField()
    beta = models.CurrencyField()
    adjust_cost = models.CurrencyField()


class Player(BasePlayer):
    price = models.CurrencyField(
        min=cu(0), max=C.PRICE_MAX, label="Please enter your new price (you can keep the initial price):"
    )
    is_winner = models.BooleanField(initial=False)
    is_adjusted = models.BooleanField(initial=False)



# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    #Decide if the player adjusted
    for p in players:
        if not p.is_adjusted:
            p.price = p.group.init_price
    prices = [p.price for p in players]
    avg = sum(prices) / len(players)
    group.avg = round(avg, 2)
    #Calculate all profits
    profits = [calc_profit(p) for p in players]
    group.best_profit = max(profits)
    best_player = max(players, key=lambda player: calc_profit(player))
    group.best_price = best_player.price
    winners = [p for p in players if p.price == group.best_price]
    group.num_winners = len(winners)
    for p in winners:
        p.is_winner = True
        p.payoff = C.PAYMENT / group.num_winners


def avg_history(group: Group):
    return [g.avg for g in group.in_previous_rounds()]


def creating_session(subsession):
    for group in subsession.get_groups():
        group.cost = C.NEW_PRODUCT_COST[subsession.round_number - 1]
        group.alpha = C.ALPHA[subsession.round_number - 1]
        group.theta = C.THETA[subsession.round_number - 1]
        group.beta = C.BETA[subsession.round_number - 1]
        group.adjust_cost = C.ADJUST_COST[subsession.round_number - 1]
        group.init_price = C.INIT_PRICE[subsession.round_number - 1]


def calc_profit(player: Player):
    gross_profit = cu((player.price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.price + player.group.theta * player.group.avg))

    if player.is_adjusted:
        return gross_profit - player.group.adjust_cost
    else:
        return gross_profit


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Guess(Page):
    form_model = 'player'
    form_fields = ['is_adjusted']
    #form_fields = ['price']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(avg_history=avg_history(group))

class Guess2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_adjusted

    form_model = 'player'
    form_fields = ['price']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(avg_history=avg_history(group))



class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        sorted_prices = sorted(p.price for p in group.get_players())
        return dict(sorted_prices=sorted_prices,
                    profit = calc_profit(player))


page_sequence = [Introduction, Guess, Guess2, ResultsWaitPage, Results]
