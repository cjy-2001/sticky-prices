from otree.api import *


doc = """
Sticky prices experiment based on oTree.
Players will play as different firms and decide if they will change their prices given an upcoming cost shock; 
Served as a real-life experiment to test the Nominal Rigidity (or sticky prices) theory.
See https://www.nber.org/system/files/working_papers/w2327/w2327.pdf
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    NAME_IN_URL = 'sticky_prices'
    INSTRUCTIONS_TEMPLATE = 'sticky_prices/instructions.html'
    PRICE_MAX = cu(100)

    INIT_PRICE = [cu(10)] * NUM_ROUNDS
    INIT_PRODUCT_COST = [cu(9.2)] * NUM_ROUNDS
    NEW_PRODUCT_COST = ([cu(8.7), cu(10.7), cu(8.7)])
    ALPHA = [9.2] * NUM_ROUNDS
    THETA = [1.8] * NUM_ROUNDS
    BETA = [2.5] * NUM_ROUNDS
    ADJUST_COST = [cu(3)] * NUM_ROUNDS
    START_EARNINGS = cu(15)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    avg = models.CurrencyField(initial=-1)
    init_price = models.CurrencyField()
    cost = models.CurrencyField()
    alpha = models.FloatField()
    theta = models.FloatField()
    beta = models.FloatField()
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
    expected_init_profit = models.CurrencyField(initial=0)
    price = models.CurrencyField(
        min=cu(0), max=C.PRICE_MAX, label="Please enter your new price:", initial=0
    )
    profit = models.CurrencyField(initial=0)
    is_adjusted = models.BooleanField(initial=False)
    redo = models.BooleanField(initial=False)
    reprice = models.BooleanField(initial=False)


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    prices = [p.price for p in players]
    group.avg = sum(prices) / len(players)
    for p in players:
        p.profit = calc_profit(p, group.avg)
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


def calc_init_profit(player: Player, group_avg):
    gross_profit = cu((player.group.init_price - player.group.cost) * \
                      (player.group.alpha - player.group.beta * player.group.init_price + player.group.theta * group_avg))

    return gross_profit


def earnings_history(player: Player):
    return sum(p.profit for p in player.in_previous_rounds())


def custom_export(players):
    # header row
    yield ['participant_code', 'round_number', 'id_in_group', 'expected_avg', 'price', 'payoff']
    for p in players:
        participant = p.participant
        yield [participant.code, p.round_number, p.id_in_group, p.expected_avg, p.price, p.payoff]


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(player: Player):
        group = player.group
        other_members = C.PLAYERS_PER_GROUP - 1
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player) + C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,

                    other_members=other_members
                    )


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
        player.expected_init_profit = calc_init_profit(player, player.expected_avg)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class SetPrice(Page):

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
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )

    @staticmethod
    def js_vars(player):
        return dict(
            cost=player.group.cost,
            alpha=player.group.alpha,
            beta=player.group.beta,
            theta=player.group.theta,
            avg=player.expected_avg,
            adjust_cost=player.group.adjust_cost
        )


class Expect(Page):
    form_model = 'player'
    form_fields = ['redo']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.price != player.group.init_price:
            player.is_adjusted = True

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


#Making duplicate pages
class SecondProbability(Page):
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
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )


class SecondSetPrice(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_profit = calc_profit(player, player.expected_avg)
        player.expected_init_profit = calc_init_profit(player, player.expected_avg)


    form_model = 'player'
    form_fields = ['price']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    )

    @staticmethod
    def js_vars(player):
        return dict(
            cost=player.group.cost,
            alpha=player.group.alpha,
            beta=player.group.beta,
            theta=player.group.theta,
            avg=player.expected_avg,
            adjust_cost=player.group.adjust_cost
        )


class SecondExpect(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.redo

    form_model = 'player'
    form_fields = ['redo']

    def before_next_page(player, timeout_happened):
        if player.price != player.group.init_price:
            player.is_adjusted = True

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg=player.expected_avg,
                    player_expected_profit=player.expected_profit,
                    player_expected_init_profit=player.expected_init_profit,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_adjusted=player.is_adjusted,
                    player_redo=player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS),

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
                    player_expected_init_profit=player.expected_init_profit,
                    player_price = player.price,
                    player_profit = player.profit,
                    player_adjusted = player.is_adjusted,
                    player_redo = player.redo,
                    player_earnings=(earnings_history(player)+C.START_EARNINGS+player.profit),

                    group_avg = player.group.avg,
                    group_cost = player.group.cost,
                    group_init_price = player.group.init_price,
                    )




page_sequence = [Introduction,
                 Probability, SetPrice, Expect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 SecondProbability, SecondSetPrice, SecondExpect,
                 ResultsWaitPage, Results]

#1. Change probability 2. Change price 3. Adjust price to 4. Keep the initital