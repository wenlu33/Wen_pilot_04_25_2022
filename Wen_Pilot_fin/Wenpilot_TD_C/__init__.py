from otree.api import *
from otree.models import player

doc = """
This is TD game with regret
"""


class C(BaseConstants):
    NAME_IN_URL = 'TD_C'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 7
    INSTRUCTIONS_TEMPLATE = 'Wenpilot_TD_C/instructions.html'
    # Player's reward for the lowest claim"""
    ADJUSTMENT_ABS = int(40)
    # Player's deduction for the higher claim
    # The maximum claim to be requested
    MAX_AMOUNT = int(200)
    # The minimum claim to be requested
    MIN_AMOUNT = int(40)
    timeout_seconds = 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    lower_claim = models.IntegerField()


class Player(BasePlayer):
    q1 = models.StringField(
        choices=['20', '30', '40', '50'],
        label='The <strong>minimum</strong> amount I can submit is:',
        widget=widgets.RadioSelect,
    )

    q2 = models.StringField(
        choices=['100', '200', '300', '400'],
        label='The <strong>maximum</strong> amount I can submit is:',
        widget=widgets.RadioSelect,
    )
    q3 = models.StringField(
        choices=['There is no adjustment','10', '20', '30', '40'],
        label='What is the adjustment if I submit <strong>differently</strong> than the other subject?',
        widget=widgets.RadioSelect,
    )
    q4 = models.StringField(
        choices=['M', 'M – adjustment', 'M + adjustment'],
        label='M represents the number submitted. </br> If I and the other subject <strong>both</strong> submit M, how much will I get?',
        widget=widgets.RadioSelect,
    )
    q5 = models.StringField(
        choices=['M', 'm', 'M – adjustment', 'M + adjustment', 'm - adjustment', 'm + adjustment'],
        label='M and m represent the number submitted and M is larger than m. </br> If <strong>I submit M</strong> and the other subject submit m, how much will I get?',
        widget=widgets.RadioSelect,
    )
    q6 = models.StringField(
        choices=['M', 'm', 'M – adjustment', 'M + adjustment', '$m - adjustment', 'm + adjustment'],
        label='M and m represent the number submitted and M is larger than m. </br> If <strong>I submit m</strong> and the other subject submit M, how much will I get?',
        widget=widgets.RadioSelect,
    )
    ## how to make people not move to next step unless they answer correctly?
    ## how to make instructions side by side with the assessment?
    ## if i want to pay them with number of questions they answered correctly (to motivate them to answer correctly), how should i do it?

    claim = models.IntegerField(
        min=C.MIN_AMOUNT,
        max=C.MAX_AMOUNT,
        label='What number are <strong>you</strong> submitting for this round?',
        doc="""
        Each player's claim
        """,
    )
    guess = models.IntegerField(
        min=C.MIN_AMOUNT,
        max=C.MAX_AMOUNT,
        label='What number do you think <strong>the other subject</strong> will submit?',
        doc="""
            Each player's guess
            """,
    )
    adjustment = models.IntegerField()
    is_winner = models.BooleanField()
    potential_optimal_claim = models.IntegerField(min=C.MIN_AMOUNT, max=C.MAX_AMOUNT)
    potential_max_payoff = models.CurrencyField()


class Message(ExtraModel):
    group = models.Link(Group)
    sender = models.Link(Player)
    text = models.StringField()


# def to_dict(msg: Message):
#     return dict(sender=msg.sender.id_in_group, text=msg.text)

# FUNCTIONS
def creating_session(subsession):
    subsession.group_randomly()
    print('in creating session')
    # Establish a total earnings variable for each participant and
    # initialize to 0 at beginning of session.
    # for p in subsession.get_players():
    #     if subsession.round_number == 1:
    #         p.participants.totalEarnings = 0


def set_payoffs(group: Group):
    p1, p2 = group.get_players()
    if p1.claim == p2.claim:
        group.lower_claim = p1.claim
        for p in [p1, p2]:
            p.payoff = group.lower_claim
            p.adjustment = int(0)
            p.potential_optimal_claim = group.lower_claim - 1
            p.potential_max_payoff = group.lower_claim - 1 + C.ADJUSTMENT_ABS
    else:
        if p1.claim < p2.claim:
            winner = p1
            loser = p2
        else:
            winner = p2
            loser = p1
        group.lower_claim = winner.claim
        winner.adjustment = C.ADJUSTMENT_ABS
        loser.adjustment = -C.ADJUSTMENT_ABS
        winner.payoff = group.lower_claim + winner.adjustment
        loser.payoff = group.lower_claim + loser.adjustment
        winner.potential_optimal_claim = group.lower_claim
        loser.potential_optimal_claim = group.lower_claim - 1
        winner.potential_max_payoff = group.lower_claim + winner.adjustment
        loser.potential_max_payoff = group.lower_claim - 1 + winner.adjustment


# for p in group.get_players():
#     p.participant.totalEarnings += p.participant.payoff

# prev_player = player.in_all_round()
# print(prev_player.payoff)


# def set_payoffs(group: Group):
#     p1, p2 = group.get_players()
#     if p1.claim == p2.claim:
#         group.lower_claim = p1.claim
#         winner = [p for p in [p1, p2] if p.claim == group.lower_claim]
#         for p in [p1, p2]:
#             if p == winner:
#                 p.is_winner = True
#                 p.payoff = group.lower_claim
#                 p.adjustment = int(0)
#                 p.potential_optimal_claim = group.lower_claim - 1
#                 p.potential_max_payoff = p.group.lower_claim - 1 + C.ADJUSTMENT_ABS
#             else:
#                 p.is_winner = False
#                 p.payoff = group.lower_claim
#                 p.adjustment = int(0)
#                 p.potential_optimal_claim = group.lower_claim - 1
#                 p.potential_max_payoff = p.group.lower_claim - 1 + C.ADJUSTMENT_ABS
#     else:
#         group.lower_claim = min([p.claim for p in [p1, p2]])
#         winner = [p for p in [p1, p2] if p.claim == group.lower_claim]
#         for p in [p1, p2]:
#             if p == winner:
#                 p.is_winner = True
#                 p.payoff = group.lower_claim + C.ADJUSTMENT_ABS
#                 p.potential_optimal_claim = group.lower_claim
#                 p.potential_max_payoff = group.lower_claim + C.ADJUSTMENT_ABS
#             else:
#                 p.is_winner = False
#                 p.payoff = group.lower_claim - C.ADJUSTMENT_ABS
#                 p.potential_optimal_claim = group.lower_claim - 1
#                 p.potential_max_payoff = group.lower_claim - 1 + C.ADJUSTMENT_ABS

## How to get this value and show it in result page???


def other_player(player: Player):
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Assessment1(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(q1='$ED40', q2='$ED200', q3='$ED40', q4='$ED M', q5="$ED (m - adjustment)", q6='$ED (m + adjustment)')
        # errors = {f: 'Wrong' for f in solutions if values[f] != solutions[f]}

        if values != solutions:
        # if errors:
            return "One or more answers were incorrect, please refer to the instruction and make correction."

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


    # @staticmethod
    # def error_message(player, values):
    #     print('values is', values)
    #     if values['int1'] + values['int2'] + values['int3'] != 100:
    #         return 'The numbers must add up to 100'


# class Assessment2(Page):
#     form_model = 'player'
#     form_fields = ['q2']
#
#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1
#
#
# class Assessment3(Page):
#     form_model = 'player'
#     form_fields = ['q3']
#
#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1
#
#
# class Assessment4(Page):
#     form_model = 'player'
#     form_fields = ['q4']
#
#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1
#
#
# class Assessment5(Page):
#     form_model = 'player'
#     form_fields = ['q5']
#
#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1
#
#
# class Assessment6(Page):
#     form_model = 'player'
#     form_fields = ['q6']
#
#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1


class Claim(Page):
    form_model = 'player'
    form_fields = ['guess', 'claim']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class new_assign_page(Page):
    pass

class chat(Page):
    def get_timeout_seconds(player):
        return C.timeout_seconds  # in seconds


class aMyWaitPage(WaitPage):
    template_name = 'Wenpilot_TDRegret_CR/aMyWaitPage.html'


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(other_player_claim=other_player(player).claim)


page_sequence = [Introduction,
                new_assign_page, aMyWaitPage, chat, Claim, ResultsWaitPage, Results, ResultsWaitPage]
