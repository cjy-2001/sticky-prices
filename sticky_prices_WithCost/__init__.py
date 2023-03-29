from otree.api import *
import random

doc = """
Sticky prices experiment based on oTree (wrote for Professor Munro at Middlebury College for his research paper).
Players will play as different firms and decide if they will change their prices given an upcoming cost shock; 
Served as a real-life experiment to test the Nominal Rigidity (or sticky prices) theory.
See https://www.nber.org/system/files/working_papers/w2327/w2327.pdf
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 5
    NUM_PRACTICE_ROUNDS = 1
    NUM_REAL_ROUNDS = 16
    NUM_ROUNDS = NUM_PRACTICE_ROUNDS + NUM_REAL_ROUNDS
    NAME_IN_URL = 'sticky_prices_WithCost'
    INSTRUCTIONS_TEMPLATE = 'sticky_prices_WithCost/instructions.html'
    PRICE_MAX = cu(100)
    INIT_PRICE = [cu(10)] * NUM_ROUNDS
    INIT_COST = cu(9.2)
    NEW_PRODUCT_COST = [cu(10.45), cu(7.45), cu(9.70), cu(10.45), cu(7.95),
                        cu(11.70), cu(8.70), cu(6.70), cu(10.95), cu(7.45),
                        cu(9.70), cu(10.45), cu(7.95), cu(11.70), cu(8.70),
                        cu(6.70), cu(10.95)]
    ALPHA = [9.2] * NUM_ROUNDS
    BETA = [2.5] * NUM_ROUNDS
    THETA = [1.8] * NUM_ROUNDS
    ADJUST_COST = [cu(2)] * NUM_ROUNDS
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


# helper functions to create multiple fields
def makeProb():
    return models.IntegerField(initial=0, blank=True)

def makeQuiz(choices, label):
    return models.StringField(widget=widgets.RadioSelect,
        choices=choices,
        label=label,
        )

def makeLottery(label):
    return models.BooleanField(
        widget=widgets.RadioSelect,
        choices=[[True,"A. Yes"], [False, "B. No"]],
        label=label,
        )

class Player(BasePlayer):
    prob6 = makeProb()
    prob7 = makeProb()
    prob8 = makeProb()
    prob9 = makeProb()
    prob10 = makeProb()
    prob11 = makeProb()
    prob12 = makeProb()
    prob13 = makeProb()
    prob14 = makeProb()
    expected_avg = models.CurrencyField(initial=0, blank=True)
    price = models.CurrencyField(min=cu(0), max=C.PRICE_MAX, initial=cu(0))
    slider_price = models.CurrencyField(min=cu(6), max=cu(14), initial=cu(10))
    profit = models.CurrencyField(initial=0)
    sec_profit = models.CurrencyField(initial=0)
    is_adjusted = models.BooleanField(initial=False)
    earnings = models.CurrencyField(initial=0)
    timeout = models.BooleanField(initial=False)

    # create quiz questions
    quiz1 = makeQuiz(
        ["A. I will stay with the same group of 5 people throughout the entire experiment", "B. Other people will get re-sorted so that I am not with the same 5 people I had played with previously"],
        "When you move to a new round, you will have another decision to make about adjusting your price or keeping it at $10. Do you stay with the same 5 people from round to round, or does group membership get reshuffled each time?"
        )
    quiz2 = makeQuiz(
        ["A. I must charge $10.00", "B. I am not allowed to charge $10.00", "C. I can keep my price at $10.00 or I can change it"],
        "If yesterday's price is $10.00, which of the following is true:"
    )
    quiz3 = makeQuiz(
        ["A. The buyers will want to buy more from me", "B. The buyers will want to buy less from me"],
        "If you increase your price, then:"
    )
    quiz4 = makeQuiz(
        ["A. The buyers will want to buy more from me, since the other sellers seem like a worse deal", "B. The buyers will want to buy less from me"],
        "If the average price in the market increases, due to the decisions of the other sellers, then:"
    )
    quiz5 = makeQuiz(
        ["A. Enter two numbers of 100 in the 7's and 8's columns", "B. Enter two numbers of 50 in the 7's and 8's columns", "C. Enter two numbers of 1 in the 7's and 8's columns"],
        "If you believe that there is a 50% chance that the market price will be 7 and a 50% chance that the market price will be 8, how would you indicate that in the probability table above?"
    )
    quiz6 = makeQuiz(
        ["A. The market price", "B. The price I set", "C. The cost of producing a widget", "D. All of the above"],
        "Which of the following can affect your profit?"
    )
    quiz7 = makeQuiz(
        ["A. $7.82", "B. $8.93", "C. $10.00", "D. $11.21"],
        "To practice this, suppose the production cost is $6.20 and you set your beliefs to those in Belief Example 2 (as shown in the table above). Moving the slider, which price would maximize the profit you receive from adjusting your price?"
    )

    # create lotteries 
    lottery1 = makeLottery("Would you like to enter the first lottery (50% chance to lose $1)?")
    lottery2 = makeLottery("Would you like to enter the second lottery (50% chance to lose $2)?")
    lottery3 = makeLottery("Would you like to enter the third lottery (50% chance to lose $3)?")
    lottery4 = makeLottery("Would you like to enter the fourth lottery (50% chance to lose $4)?")
    lottery5 = makeLottery("Would you like to enter the fifth lottery (50% chance to lose $5)?")

    gender = models.StringField(widget=widgets.RadioSelect,
                                   choices=["Male", "Female", "Non-binary", "Other", "Prefer not to answer"],
                                   label="What is your gender identity?")
    whichLottery = models.StringField(initial="")
    decision = models.BooleanField(initial=False)
    win = models.BooleanField(initial=False)
    lotteryResult = models.IntegerField(initial=0)
    comment = models.StringField()

# FUNCTIONS
# main profit calculation function
def calc_profit(player: Player, group_avg):
    # apply profit formula
    gross_profit = cu((player.price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.price + player.group.theta * group_avg))

    # check if it's adjusted
    if player.is_adjusted:
        return gross_profit - player.group.adjust_cost
    else:
        return gross_profit


# profit calculation based on initial price
def calc_profit_on_initial(player: Player, group_avg):
    gross_profit = cu((player.group.init_price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.group.init_price + player.group.theta * group_avg))

    return gross_profit


# profit calculation based on slide price
def calc_profit_on_slide(player: Player, group_avg):
    gross_profit = cu((player.slider_price - player.group.cost) * \
                       (player.group.alpha - player.group.beta * player.slider_price + player.group.theta * group_avg))

    return gross_profit - player.group.adjust_cost


def earnings_history(player: Player):
    return sum(p.profit for p in player.in_all_rounds()) + C.START_EARNINGS


# calculate lottery result
def finalLottery(player: Player):
    # pick a lottery
    player.whichLottery = random.choice(["lottery 1", "lottery 2", "lottery 3", "lottery 4", "lottery 5"])

    # win or lose?
    winOrLose = random.randint(1, 2)
    if winOrLose == 2:
        player.win = True

    attribute = player.whichLottery.replace(" ", "")
    player.decision = getattr(player, attribute)

    # if player selects to play
    if player.decision:
        if player.win:
            player.earnings += 4
            player.payoff += 4
            player.lotteryResult += 4
        else:
            player.earnings -= int(attribute[-1])
            player.payoff -= int(attribute[-1])
            player.lotteryResult -= int(attribute[-1])


def set_payoffs(group: Group):
    # get all players
    players = group.get_players()

    for p in players:
        p.price = p.slider_price

        # determine if player adjusts price
        if not p.is_adjusted:
            p.price = p.group.init_price
        if p.price == p.group.init_price:
            p.is_adjusted = False
        else:
            p.is_adjusted = True

    # calculate group's average price
    prices = [p.price for p in players]
    group.avg = sum(prices) / len(players)

    # calculate each player's profit
    for p in players:
        p.profit = calc_profit(p, group.avg)
        if p.is_adjusted:
            p.sec_profit = calc_profit_on_initial(p, group.avg)
        else:
            p.sec_profit = calc_profit_on_slide(p, group.avg)

        # determine earnings
        if not group.subsession.is_practice_round:
            practice_player = p.in_round(1)
            p.payoff = p.profit
            p.earnings = earnings_history(p) - practice_player.profit
        else:
            p.payoff = C.START_EARNINGS
            p.earnings = C.START_EARNINGS


def creating_session(subsession):
    subsession.is_practice_round = (subsession.round_number <= C.NUM_PRACTICE_ROUNDS)

    if not subsession.is_practice_round:
        subsession.real_round_number = (
            subsession.round_number - C.NUM_PRACTICE_ROUNDS
        )

    # if we want to mix up different groups
    # subsession.group_randomly()

    # assign each round's parameters
    for group in subsession.get_groups():
        group.cost = C.NEW_PRODUCT_COST[subsession.round_number - 1]
        group.alpha = C.ALPHA[subsession.round_number - 1]
        group.theta = C.THETA[subsession.round_number - 1]
        group.beta = C.BETA[subsession.round_number - 1]
        group.adjust_cost = C.ADJUST_COST[subsession.round_number - 1]
        group.init_price = C.INIT_PRICE[subsession.round_number - 1]


def custom_export(players):
    # header row
    yield ['participant_code', 'round_number',
           '6_probability', '7_probability', '8_probability', '9_probability', '10_probability', '11_probability', '12_probability', '13_probability', '14_probability',
           'expected_avg', 'price on slider', 'selected_price', 'timeout?', 'profit per round', 'accumulated earnings (including $15)', 'lotteryResult',
           'gender', 'lottery1', 'lottery2', 'lottery3', 'lottery4', 'lottery5', 'comment']

    for p in players:
        participant = p.participant
        yield [participant.code, p.round_number,
               p.prob6, p.prob7, p.prob8, p.prob9, p.prob10, p.prob11, p.prob12, p.prob13, p.prob14,
               p.expected_avg, p.slider_price, p.price, p.timeout, p.payoff, p.earnings, p.lotteryResult,
               p.gender, p.lottery1, p.lottery2, p.lottery3, p.lottery4, p.lottery5, p.comment]


# helper function to return current information
def commonVars(player):
    return dict(
        player_expected_avg=player.expected_avg,
        player_slider_price=player.slider_price,
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
        )

# PAGES
class Introduction(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6', 'quiz7']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player, values):
        if values['quiz1'] != "A. I will stay with the same group of 5 people throughout the entire experiment" \
                or values['quiz2'] != "C. I can keep my price at $10.00 or I can change it"\
                or values['quiz3'] != "B. The buyers will want to buy less from me"\
                or values['quiz4'] != "A. The buyers will want to buy more from me, since the other sellers seem like a worse deal" \
                or values['quiz5'] != "B. Enter two numbers of 50 in the 7's and 8's columns"\
                or values['quiz6'] != "D. All of the above" \
                or values['quiz7'] != "A. $7.82":
            return 'One or more answers to the quiz are incorrect, please try again.'

    def vars_for_template(player: Player):
        return dict(
            other_members=C.PLAYERS_PER_GROUP-1,
            quiz1='quiz1',
            quiz2='quiz2',
            quiz3='quiz3',
            quiz4='quiz4',
            quiz5='quiz5',
            quiz6='quiz6',
            quiz7='quiz7',
        ) | commonVars(player)


class SetPrice(Page):
    timeout_seconds = 180
    form_model = 'player'
    form_fields =  ['prob6', 'prob7', 'prob8', 'prob9', 'prob10', 'prob11', 'prob12', 'prob13', 'prob14', 'slider_price', 'expected_avg', 'is_adjusted']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.price = cu(10)
            player.timeout = True

    @staticmethod
    def error_message(player, values):
        if values['prob6'] + values['prob7'] + values['prob8'] + values['prob9'] + values['prob10'] + values['prob11'] + values['prob12'] + values['prob13'] + values['prob14'] != 100:
            return 'The sum of probabilities must add up to 100'


    @staticmethod
    def vars_for_template(player: Player):
        first_round = player.round_number == 1

        # check if it is the first round
        if not first_round:
            diff = abs(player.group.cost - C.INIT_COST)
            up = player.group.cost >= C.INIT_COST
            return dict(
                    first_round=first_round,
                    diff=diff,
                    up=up,
                    ) | commonVars(player)
        else:
            return dict(
                    first_round=first_round,
                    ) | commonVars(player)

    @staticmethod
    def js_vars(player):
        return dict(
            cost=player.group.cost,
            alpha=player.group.alpha,
            beta=player.group.beta,
            theta=player.group.theta,
            avg=player.expected_avg,
            adjust_cost=player.group.adjust_cost,
            init_price=player.group.init_price,
        )


class ResultsWaitPage1(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class ResultsWaitPage2(WaitPage):
    after_all_players_arrive = set_payoffs


class ResultsWaitPage3(WaitPage):
    pass


class Results(Page):
    timeout_seconds = 60
    timer_text = "Time left to advance to the next page:"

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        practice_earnings = earnings_history(player)
        num_adjusted = 0

        for p in group.get_players():
            if p.is_adjusted:
                num_adjusted += 1

        return dict(
                    practice_earnings=practice_earnings,
                    num_adjusted=num_adjusted,
                    ) | commonVars(player)


class PracticeFeedback(Page):
    timeout_seconds = 30
    timer_text = "Time left to advance to the next page:"

    @staticmethod
    def is_displayed(player: Player):
        subsession = player.subsession
        return subsession.is_practice_round


class Lottery(Page):
    form_model = 'player'
    form_fields = ['lottery1', 'lottery2', 'lottery3', 'lottery4', 'lottery5', 'gender']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player, timeout_happened):
        finalLottery(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            whichLottery=player.whichLottery,
            decision=player.decision,
            win=player.win,
            ) | commonVars(player)


class LotteryResult(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
                    lottery1=player.lottery1,
                    lottery2=player.lottery2,
                    lottery3=player.lottery3,
                    lottery4=player.lottery4,
                    lottery5=player.lottery5,
                    whichLottery=player.whichLottery,
                    decision=player.decision,
                    win=player.win
                    ) | commonVars(player)


class Feedback(Page):
    form_model = 'player'
    form_fields = ['comment']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class ThankYou(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        total_earnings = player.earnings + 7.5
        return dict(
                    total_earnings=total_earnings,
                    )


page_sequence = [Introduction, ResultsWaitPage1, SetPrice, ResultsWaitPage2, Results, ResultsWaitPage3, PracticeFeedback, ResultsWaitPage1, Lottery, LotteryResult, Feedback, ThankYou]