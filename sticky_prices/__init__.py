from otree.api import *


doc = """
Sticky prices experiment based on oTree.
Players will play as different firms and decide if they will change their prices given an upcoming cost shock; 
Served as a real-life experiment to test the Nominal Rigidity (or sticky prices) theory.
See https://www.nber.org/system/files/working_papers/w2327/w2327.pdf
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 1
    NUM_PRACTICE_ROUNDS = 1
    NUM_REAL_ROUNDS = 10
    NUM_ROUNDS = NUM_PRACTICE_ROUNDS + NUM_REAL_ROUNDS
    NAME_IN_URL = 'sticky_prices'
    INSTRUCTIONS_TEMPLATE = 'sticky_prices/instructions.html'
    PRICE_MAX = cu(100)

    INIT_PRICE = [cu(10)] * NUM_ROUNDS
    INIT_COST = cu(9.2)
    NEW_PRODUCT_COST = [cu(9.2), cu(8.7), cu(10.7), cu(9.7), cu(6.2), cu(8.2), cu(11.2), cu(12.2), cu(7.7), cu(10.2), cu(7.2)]
    ALPHA = [9.2] * NUM_ROUNDS
    THETA = [1.8] * NUM_ROUNDS
    BETA = [2.5] * NUM_ROUNDS
    ADJUST_COST = [cu(3)] * NUM_ROUNDS
    START_EARNINGS = cu(15)


class Subsession(BaseSubsession):
    is_practice_round = models.BooleanField()
    real_round_number = models.IntegerField()


class Group(BaseGroup):
    avg = models.CurrencyField(initial=-1)
    init_price = models.CurrencyField()
    cost = models.CurrencyField()
    alpha = models.FloatField()
    theta = models.FloatField()
    beta = models.FloatField()
    adjust_cost = models.CurrencyField()


class Player(BasePlayer):
    prob6 = models.IntegerField(initial=0)
    prob7 = models.IntegerField(initial=0)
    prob8 = models.IntegerField(initial=0)
    prob9 = models.IntegerField(initial=0)
    prob10 = models.IntegerField(initial=0)
    prob11 = models.IntegerField(initial=0)
    prob12 = models.IntegerField(initial=0)
    prob13 = models.IntegerField(initial=0)
    prob14 = models.IntegerField(initial=0)
    expected_avg = models.CurrencyField(initial=0)
    price = models.CurrencyField(min=cu(0), max=C.PRICE_MAX, initial=10)
    profit = models.CurrencyField(initial=0)
    is_adjusted = models.BooleanField(initial=False)
    earnings = models.CurrencyField(initial=C.START_EARNINGS)

    quiz1 = models.StringField(widget=widgets.RadioSelect,
                               choices=["A. I must charge $10", "B. I am not allowed to charge $10", "C. I can keep my price at $10 or I can change it"],
                               label="If yesterday’s price is $10, then which of the following is true:")
    quiz2 = models.StringField(widget=widgets.RadioSelect,
                               choices=["A. The buyers will want to buy more from me", "B. The buyers will want to buy less from me"],
                               label="If you increase your price, then:")
    quiz3 = models.StringField(widget=widgets.RadioSelect,
                               choices=["A. The buyers will want to buy more from me, since the other sellers seem like a worse deal", "B. The buyers will want to buy less from me"],
                               label="If the average price in the market, due to the decisions of the other sellers, increase, then:")
    quiz4 = models.StringField(widget=widgets.RadioSelect,
                               choices=["A. Enter two numbers of 100 in the 7's and 8's columns", "B. Enter two numbers of 50 in the 7's and 8's columns", "C. Enter two numbers of 1 in the 7's and 8's columns"],
                               label="If you believed that there is a 50% chance that the market price will be 7 and a 50% chance that the market price will be 8, how would you indicate that in the probability table above?")
    quiz5 = models.StringField(widget=widgets.RadioSelect,
                               choices=["A. The market price", "B. The price I set", "C. The cost of producing a widget", "D. All of the above"],
                               label="Which of the following can affect you profit?")


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    for p in players:
        if not p.is_adjusted:
            p.price = p.group.init_price
    prices = [p.price for p in players]
    group.avg = sum(prices) / len(players)
    for p in players:
        p.profit = calc_profit(p, group.avg)
        if not group.subsession.is_practice_round:
            practice_player = p.in_round(1)
            p.payoff = p.profit
            p.earnings += earnings_history(p) - practice_player.profit


def creating_session(subsession):
    subsession.is_practice_round = (subsession.round_number <= C.NUM_PRACTICE_ROUNDS)

    if not subsession.is_practice_round:
        subsession.real_round_number = (
            subsession.round_number - C.NUM_PRACTICE_ROUNDS
        )

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
    return sum(p.profit for p in player.in_all_rounds())


def custom_export(players):
    # header row
    yield ['participant_code', 'round_number',
           '6_probability', '7_probability', '8_probability', '9_probability', '10_probability', '11_probability', '12_probability', '13_probability', '14_probability',
           'expected_avg', 'selected_price', 'profit per round', 'accumulated earnings (including $15)']
    for p in players:
        participant = p.participant
        yield [participant.code, p.round_number,
               p.prob6, p.prob7, p.prob8, p.prob9, p.prob10, p.prob11, p.prob12, p.prob13, p.prob14,
               p.expected_avg, p.price, p.payoff, p.earnings]


# PAGES
class Introduction(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


    @staticmethod
    def error_message(player, values):
        if values['quiz1'] != "C. I can keep my price at $10 or I can change it" or values['quiz2'] != "B. The buyers will want to buy less from me"\
                or values['quiz3'] != "A. The buyers will want to buy more from me, since the other sellers seem like a worse deal"\
                or values['quiz4'] != "B. Enter two numbers of 50 in the 7's and 8's columns" or values['quiz5'] != "D. All of the above":
            return 'One or more answers to the quiz are incorrect, please try again.'


    def vars_for_template(player: Player):
        group = player.group
        other_members = C.PLAYERS_PER_GROUP - 1

        return dict(player_expected_avg=player.expected_avg,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_earnings=player.earnings,
                    play_adjusted=player.is_adjusted,
                    prob6=player.prob6,
                    prob7=player.prob7,
                    prob8=player.prob8,
                    prob9=player.prob9,
                    prob10=player.prob10,
                    prob11=player.prob11,
                    prob12=player.prob12,
                    prob13=player.prob13,
                    prob14=player.prob14,

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    other_members=C.PLAYERS_PER_GROUP-1,

                    payoff=player.payoff,

                    quiz1='quiz1',
                    quiz2='quiz2',
                    quiz3='quiz3',
                    quiz4='quiz4',
                    quiz5='quiz5'
                    )


class SetPrice(Page):
    timeout_seconds = 180
    form_model = 'player'
    form_fields =  ['prob6', 'prob7', 'prob8', 'prob9', 'prob10', 'prob11', 'prob12', 'prob13', 'prob14', 'price', 'expected_avg', 'is_adjusted']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.price = 10


    @staticmethod
    def error_message(player, values):
        if values['prob6'] + values['prob7'] + values['prob8'] + values['prob9'] + values['prob10'] + values['prob11'] + values['prob12'] + values['prob13'] + values['prob14'] != 100:
            return 'The sum of probabilities must add up to 100'


    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        first_round = player.round_number == 1
        if not first_round:
            #prev_player = player.in_round(player.round_number - 1)
            #diff = abs(player.group.cost - prev_player.group.cost)
            #up = player.group.cost >= prev_player.group.cost
            diff = abs(player.group.cost - C.INIT_COST)
            up = player.group.cost >= C.INIT_COST
            return dict(player_expected_avg=player.expected_avg,
                        player_price=player.price,
                        player_profit=player.profit,
                        player_earnings=player.earnings,
                        play_adjusted=player.is_adjusted,
                        prob6=player.prob6,
                        prob7=player.prob7,
                        prob8=player.prob8,
                        prob9=player.prob9,
                        prob10=player.prob10,
                        prob11=player.prob11,
                        prob12=player.prob12,
                        prob13=player.prob13,
                        prob14=player.prob14,

                        group_avg=player.group.avg,
                        group_cost=player.group.cost,
                        group_init_price=player.group.init_price,
                        payoff=player.payoff,
                        first_round=first_round,
                        diff=diff,
                        up=up
                        )
        else:
            return dict(player_expected_avg=player.expected_avg,
                        player_price=player.price,
                        player_profit=player.profit,
                        player_earnings=player.earnings,
                        play_adjusted=player.is_adjusted,
                        prob6=player.prob6,
                        prob7=player.prob7,
                        prob8=player.prob8,
                        prob9=player.prob9,
                        prob10=player.prob10,
                        prob11=player.prob11,
                        prob12=player.prob12,
                        prob13=player.prob13,
                        prob14=player.prob14,

                        group_avg=player.group.avg,
                        group_cost=player.group.cost,
                        group_init_price=player.group.init_price,
                        payoff=player.payoff,
                        first_round=first_round,
                        )


    @staticmethod
    def js_vars(player):
        return dict(
            cost=player.group.cost,
            alpha=player.group.alpha,
            beta=player.group.beta,
            theta=player.group.theta,
            avg=player.expected_avg,
            adjust_cost=player.group.adjust_cost,
            init_price=player.group.init_price
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        practice_earnings = earnings_history(player)+C.START_EARNINGS
        return dict(player_expected_avg = player.expected_avg,
                    player_price=player.price,
                    player_profit=player.profit,
                    player_earnings=player.earnings,
                    play_adjusted=player.is_adjusted,
                    prob6=player.prob6,
                    prob7=player.prob7,
                    prob8=player.prob8,
                    prob9=player.prob9,
                    prob10=player.prob10,
                    prob11=player.prob11,
                    prob12=player.prob12,
                    prob13=player.prob13,
                    prob14=player.prob14,

                    group_avg=player.group.avg,
                    group_cost=player.group.cost,
                    group_init_price=player.group.init_price,
                    practice_earnings=practice_earnings,
                    payoff=player.payoff
                    )


class PracticeFeedback(Page):
    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.is_practice_round


class ThankYou(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(player_expected_avg = player.expected_avg,
                    player_price = player.price,
                    player_profit = player.profit,
                    player_adjusted = player.is_adjusted,
                    player_earnings= player.earnings,

                    group_avg = player.group.avg,
                    group_cost = player.group.cost,
                    group_init_price = player.group.init_price,
                    payoff=player.payoff
                    )


page_sequence = [Introduction, SetPrice, ResultsWaitPage, Results, PracticeFeedback, ThankYou]
