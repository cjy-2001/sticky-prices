class Guess(Page):
    form_model = 'player'
    form_fields = ['is_adjusted']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if not player.is_adjusted:
            player.price = player.group.init_price
            player.expected_profit = calc_profit(player, player.expected_avg)
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


class Guess2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_adjusted

    form_model = 'player'
    form_fields = ['price']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.expected_profit = calc_profit(player, player.expected_avg)
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