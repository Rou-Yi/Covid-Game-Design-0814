from _night.enemy.enemy import EnemyGroup
from _night.ally.ally import AllyGroup
from _night.mana.mana import ManaGroup
from _night.ally.ally_button_menu import Button_menu, Pause_menu, User_guide_menu
from _night.ending_page.ending_page import Ending_page
from all_image import BACKGROUND_NIGHT
from _night.game.user_request import *
from sound import play_soundtrack_win, play_soundtrack_loss, play_soundtrack_button


class GameModel:
    def __init__(self, level, music):
        # data
        self.bg_image = BACKGROUND_NIGHT
        self.__enemies = EnemyGroup()
        self.__allies = AllyGroup()
        self.__menu = Button_menu(level)
        self.__pause = Pause_menu()
        self.__mana = ManaGroup(level)
        self.__user_guide = User_guide_menu()
        # selected item
        self.selected_button = None
        # game over variables
        self.unlock_next_level = False
        self.game_over = False
        self.game_over_win = False
        self.game_over_loss = False
        self.result = None
        # apply observer pattern
        self.subject = RequestSubject(self)
        self.generator = CatsGenerator(self.subject, level)
        self.pause_game_claim = Pause_game(self.subject)
        self.guide_claim = Guide(self.subject, level)
        #
        self.mana_value = self.__mana.mana_value
        self.level = level
        self.music = music

    def user_request(self, user_request: str):
        """ summon cats """
        self.subject.notify(user_request)

    def get_request(self, events: dict) -> str:
        """get keyboard response or button response"""
        # initial
        self.selected_button = None
        # mouse event
        if events["mouse position"] is not None:
            x, y = events["mouse position"]
            self.select(x, y)
            if self.selected_button is not None:
                play_soundtrack_button()
                return self.selected_button.response
            return "nothing"
        return "nothing"

    def select(self, mouse_x: int, mouse_y: int) -> None:
        """change the state of whether the items are selected"""
        # if the button is clicked, get the button response.
        for btn in self.__menu.get_buttons():
            if btn.clicked(mouse_x, mouse_y):
                self.selected_button = btn
        for btn in self.__pause.get_buttons():
            if btn.clicked(mouse_x, mouse_y):
                self.selected_button = btn
        for btn in self.__user_guide.get_buttons():
            if btn.clicked(mouse_x, mouse_y):
                self.selected_button = btn

    def allies_attack(self):
        """ 友軍執行攻擊 """
        for cats in self.__allies.get():
            cats.attack(self.__enemies)

    def allies_advance(self):
        """ 友軍執行移動、血量判斷 """
        self.game_over_loss = self.__allies.advance(self.__enemies)

    def enemies_campaign(self):
        """ 自動派出敵人 """
        self.__enemies.summon(self.level)
        self.__enemies.campaign()

    def enemies_attack(self):
        """ 敵人執行攻擊 """
        for virus in self.enemies.get():
            virus.attack(self.__allies)

    def enemies_advance(self, ):
        """ 敵人執行移動、血量判斷 """
        self.game_over_win = self.__enemies.advance(self.__allies)

    def mana_advance(self):
        """ 魔力條補充、魔力值更新 """
        self.__mana.advance()
        self.mana_value = self.__mana.mana_value

    def game_over_advance(self):
        """ 當贏或輸成立時，結束遊戲 """
        if self.game_over_loss or self.game_over_win:
            self.game_over = True
            if self.game_over_loss:
                self.result = Ending_page.Loss()
                play_soundtrack_loss()
            elif self.game_over_win:
                self.unlock_next_level = True
                self.result = Ending_page.Win(self.level)
                play_soundtrack_win()

    def force_to_end_game(self):
        """ 從暫停頁面，選擇回到主畫面，強制結束遊戲 """
        if self.pause_game_claim.force_end_game:
            self.game_over = True
            self.result = Ending_page.Loss()
            self.result.response = "main menu night"
            self.result.jump_page = True

    @property
    def enemies(self):
        return self.__enemies

    @property
    def allies(self):
        return self.__allies

    @property
    def menu(self):
        return self.__menu

    @property
    def mana(self):
        return self.__mana

    @property
    def pause(self):
        return self.__pause

    @property
    def pause_game(self):
        return self.pause_game_claim.pause_game

    @property
    def force_end_game(self):
        return self.pause_game_claim.force_end_game

    @property
    def user_guide(self):
        return self.__user_guide

    @property
    def user_guide_claim(self):
        return self.guide_claim

    @property
    def play_music(self):
        return self.pause_game_claim.play_music

