from otree.api import Currency as c, currency_range, expect, Bot, SubmissionMustFail
from . import *


class PlayerBot(Bot):
    cases = ['no_adjust', '1_adjust', '2_adjust']

    def play_round(self):
        if self.round_number == 1:
            yield Introduction

        if self.case == 'no_adjust':
            if self.player.id_in_group == 1:
                yield Probability, dict(prob7=0, prob8=0, prob9=0, prob10=0, prob11=100, prob12=0, prob13=0)
                expect(self.player.payoff, C.JACKPOT)
                expect('you win', 'in', self.html)
            else:
                yield Guess, dict(guess=10)
                expect(self.player.payoff, 0)
                expect('you did not win', 'in', self.html)
        else:
            if self.player.id_in_group in [1, 2]:
                yield Guess, dict(guess=9)
                expect(self.player.payoff, C.JACKPOT / 2)
                expect('you are one of the 2 winners', 'in', self.html)
            else:
                yield Guess, dict(guess=10)
                expect(self.player.payoff, 0)
                expect('you did not win', 'in', self.html)

        yield Results