from otree.api import *


doc = """
Sticky prices experiment based on oTree.
Players will play as different firms and decide if they will change their prices given an upcoming cost shock; 
whoever gets the highest profit wins.
Served as a real-life experiment to test the Nominal Rigidity (or sticky prices) theory.
See https://www.nber.org/system/files/working_papers/w2327/w2327.pdf
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 1
    NUM_ROUNDS = 3
    NAME_IN_URL = 'sticky_prices'
    INSTRUCTIONS_TEMPLATE = 'sticky_prices/instructions.html'
    PRICE_MAX = cu(100)

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
    avg = models.CurrencyField(initial=-1)
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
    prob7 = models.IntegerField(min=0, max=100, label="$7:",initial=0)
    prob8 = models.IntegerField(min=0, max=100, label="$8:",initial=0)
    prob9 = models.IntegerField(min=0, max=100, label="$9:",initial=0)
    prob10 = models.IntegerField(min=0, max=100, label="$10:",initial=0)
    prob11 = models.IntegerField(min=0, max=100, label="$11:",initial=0)
    prob12 = models.IntegerField(min=0, max=100, label="$12:",initial=0)
    prob13 = models.IntegerField(min=0, max=100, label="$13:",initial=0)
    expected_avg = models.CurrencyField(initial=0)
    expected_profit = models.CurrencyField(initial=0)
    price = models.CurrencyField(min=cu(0), max=C.PRICE_MAX, label="Please enter your new price:", initial=0)
    profit = models.CurrencyField(initial=0)
    is_adjusted = models.BooleanField(initial=False)
    redo = models.BooleanField(initial=False)


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    prices = [p.price for p in players]
    group.avg = sum(prices) / len(players)
    for p in players:
        p.profit = calc_profit(p, group.avg)
    profits = [p.profit for p in players]
    group.best_profit = max(profits)
    best_player = max(players, key=lambda player: player.profit)
    group.best_price = best_player.price
    for p in players:
        p.payoff = p.profit


def creating_session(subsession):
    subsession.group_randomly()
    for group in subsession.get_groups():
        group.cost = C.NEW_PRODUCT_COST[subsession.round_number - 1]
        group.alpha = C.ALPHA[subsession.round_number - 1]
        group.theta = C.THETA[subsession.round_number - 1]
        group.beta = C.BETA[subsession.round_number - 1]
        group.adjust_cost = C.ADJUST_COST[subsession.round_number - 1]
        group.init_price = C.INIT_PRICE[subsession.round_number - 1]


def calc_profit(player: Player, group_avg):
    gross_profit = cu((player.price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.price + player.group.theta * group_avg))

    if player.is_adjusted:
        return gross_profit - player.group.adjust_cost
    else:
        return gross_profit


def earnings_history(player: Player):
    return sum(p.profit for p in player.in_previous_rounds())


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Probability(Page):
    form_model = 'player'
    form_fields = ['prob7', 'prob8', 'prob9', 'prob10', 'prob11', 'prob12', 'prob13']

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['prob7'] + values['prob8'] + values['prob9'] + values['prob10'] + values['prob11'] + values['prob12'] + values['prob13'] != 100:
            return 'The numbers must add up to 100'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_avg = cu(7 * player.prob7 + 8 * player.prob8 + 9 * player.prob9 + 10 * player.prob10 + 11 * player.prob11 +
                                 12 * player.prob12 + 13 * player.prob13) / 100

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Guess(Page):
    form_model = 'player'
    form_fields = ['is_adjusted']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if not player.is_adjusted:
            player.price = player.group.init_price
            player.expected_profit = calc_profit(player, player.expected_avg)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Guess2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_adjusted

    form_model = 'player'
    form_fields = ['price']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_profit = calc_profit(player, player.expected_avg)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Expect(Page):
    form_model = 'player'
    form_fields = ['redo']

    @staticmethod
    def before_next_page(player, timeout_happened):
        pass

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


#Making duplicate pages
class Second_Probability(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo

    form_model = 'player'
    form_fields = ['prob7', 'prob8', 'prob9', 'prob10', 'prob11', 'prob12', 'prob13']

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['prob7'] + values['prob8'] + values['prob9'] + values['prob10'] + values['prob11'] + values['prob12'] + values['prob13'] != 100:
            return 'The numbers must add up to 100'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_avg = cu(7 * player.prob7 + 8 * player.prob8 + 9 * player.prob9 + 10 * player.prob10 + 11 * player.prob11 +
                                 12 * player.prob12 + 13 * player.prob13) / 100

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Second_Guess(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo

    form_model = 'player'
    form_fields = ['is_adjusted']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if not player.is_adjusted:
            player.price = player.group.init_price
            player.expected_profit = calc_profit(player, player.expected_avg)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Second_Guess2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo & player.is_adjusted

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_profit = calc_profit(player, player.expected_avg)

    form_model = 'player'
    form_fields = ['price']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class Second_Expect(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo

    form_model = 'player'
    form_fields = ['redo']

    def before_next_page(player, timeout_happened):
        pass

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+15),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        sorted_prices = sorted(p.price for p in group.get_players())
        return dict(player_expected_avg = player.expected_avg,
                    player_expected_profit = player.expected_profit,
                    player_price = player.price,
                    player_profit = player.profit,
                    player_adjusted = player.is_adjusted,
                    player_redo = player.redo,
                    player_earnings=(earnings_history(player)+15+player.profit),

                    group_avg = player.group.avg,
                    group_cost = player.group.cost,
                    group_init_price = player.group.init_price,
                    )




page_sequence = [Introduction,
                 Probability, Guess, Guess2, Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 Second_Probability, Second_Guess, Second_Guess2, Second_Expect,
                 ResultsWaitPage, Results]
