+ 7 * document.getElementById("prob7").value + 8 * document.getElementById("prob8").value
                    + 9 * document.getElementById("prob9").value + 10 * document.getElementById("prob10").value + 11 * document.getElementById("prob11").value
                    + 12 * document.getElementById("prob12").value + 13 * document.getElementById("prob13").value + 13 * document.getElementById("prob14").value)




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


class Probability(Page):
    form_model = 'player'
    form_fields = ['prob6', 'prob7', 'prob8', 'prob9', 'prob10', 'prob11', 'prob12', 'prob13', 'prob14', 'price']

    @staticmethod
    def error_message(player, values):
        print('values is', values)
        if values['prob7'] + values['prob8'] + values['prob9'] + values['prob10'] + values['prob11'] + values['prob12'] + values['prob13'] != 100:
            return 'The numbers must add up to 100'

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