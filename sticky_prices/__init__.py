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
    PRICE_MAX = 100
    PAYMENT = 100

    INIT_PRICE = [10] * NUM_ROUNDS
    INIT_PRODUCT_COST = [9.2] * NUM_ROUNDS
    NEW_PRODUCT_COST = ([8.7, 10.7, 8.7])
    ALPHA = [9] * NUM_ROUNDS
    THETA = [1.8] * NUM_ROUNDS
    BETA = [2.5] * NUM_ROUNDS
    ADJUST_COST = [3] * NUM_ROUNDS


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    avg = models.FloatField()
    best_price = models.IntegerField()
    best_profit = models.FloatField()
    num_winners = models.IntegerField()

    init_price = models.FloatField()
    cost = models.FloatField()
    alpha = models.FloatField()
    theta = models.FloatField()
    beta = models.FloatField()
    adjust_cost = models.FloatField()


class Player(BasePlayer):
    price = models.IntegerField(
        min=0, max=C.PRICE_MAX, label="Please enter your new price (you can keep the initial price):"
    )
    is_winner = models.BooleanField(initial=False)
    is_adjusted = models.BooleanField(initial=False)



# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    prices = [p.price for p in players]
    avg = sum(prices) / len(players)
    group.avg = round(avg, 2)
    #Decide if the player adjusted
    for p in players:
        if p.price != p.group.init_price:
            p.is_adjusted = True
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
    gross_profit = (player.price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.price + player.group.theta * player.group.avg)

    if player.is_adjusted:
        return round(gross_profit - player.group.adjust_cost, 2)
    else:
        return round(gross_profit, 2)


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Guess(Page):
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


page_sequence = [Introduction, Guess, ResultsWaitPage, Results]
