import pygame
from all_image import *
from menu.menu import Menu, LevelMenu, Introduction_Menu, Time_Changer
from _night.game.game import Game_night
from _day.game.game import Game_day
from menu.intro import Intro


class Page_controller:
    """
    Used in start_menu.py to control the current menu, music or to enter a game level.
    Import every menu from menu.py.
    """
    def __init__(self):
        self.events = {"quit": False,
                       "mouse position": None,
                       "scroll up": False,
                       "scroll down": False,
                       }
        self.game_request_to_quit = False
        # level locked setting
        self.level_state_night = [1, 0, 0]
        self.level_state_day = [1, 0, 1]
        # Menus
        self.main_menu_night = Menu.MainMenu_Night()
        self.main_menu_day = Menu.MainMenu_Day()
        self.level_menu_night = LevelMenu.LevelMenu_Night(self.level_state_night)
        self.level_menu_day = LevelMenu.LevelMenu_Day(self.level_state_day)
        self.introduction_night = Introduction_Menu("night")
        self.introduction_day = Introduction_Menu("day")
        self.day_to_night = Time_Changer.Change_to_night()
        self.night_to_day = Time_Changer.Change_to_Day()
        self.intro = Intro()
        # start from the intro menu
        self.response = 'intro'
        self.menu = self.intro
        # music
        self.play_music_count = 1
        self.sound = pygame.mixer.Sound("./sound/Background (mixkit-delightful 4).mp3")

    def receive_user_input(self):
        """receive user input from the events"""
        # event initialization
        self.events = {"quit": False,
                       "mouse position": None,
                       "scroll up": False,
                       "scroll down": False,
                       }
        # update event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.events["quit"] = True
            if self.game_request_to_quit:  # 遊戲內想關掉遊戲用
                self.events["quit"] = True
            # player click action
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 4:
                    self.events["scroll up"] = True
                if event.button == 5:
                    self.events["scroll down"] = True
                else:
                    self.events["mouse position"] = [x, y]

    def music_control(self):
        # play background music after intro page ends.
        if self.play_music_count and (self.response != 'intro'):
            self.sound.set_volume(self.intro.volume)
            self.sound.play(loops=-1, fade_ms=1000)
            self.play_music_count = 0

    def update_view(self):
        """ draw menu """
        self.menu.draw()

    def update_menu(self):
        """ update if any menu has been selected and control the background music. """
        self.menu.update(self.events)
        self.music_control()
        if self.menu.response == 'play music':
            self.sound.set_volume(self.intro.volume)
        elif self.menu.response == 'pause music':
            self.sound.set_volume(0)
        else:
            self.response = self.menu.response

    def choose_menu(self, response):
        """ Transfer the menu """
        # 開場動畫
        if response == 'intro':
            self.menu = self.intro
        # 白天黑夜之間的轉換 (加 return 防止被後面的選項覆蓋)
        elif response.startswith('time:'):
            if response == 'time: day to night':
                self.menu = self.day_to_night
                return
            elif response == 'time: night to day':
                self.menu = self.night_to_day
                return
        # 黑夜系列的選單 (主畫面 / 關卡選單 / 介紹畫面)
        elif response.endswith('night'):
            if response == 'main menu night':
                self.menu = self.main_menu_night
            elif response == 'level menu night':
                self.menu = self.level_menu_night
            elif response == 'introduction night':
                self.menu = self.introduction_night
            else:
                self.menu = self.main_menu_night
        # 白天系列的選單 (主畫面 / 關卡選單 / 介紹畫面)
        elif response.endswith('day'):
            if response == 'main menu day':
                self.menu = self.main_menu_day
            elif response == 'level menu day':
                self.menu = self.level_menu_day
            elif response == 'introduction day':
                self.menu = self.introduction_day
            else:
                self.menu = self.main_menu_day

    def choose_level(self, response):
        """ Transfer the level and enter the game  """
        current_volume = self.sound.get_volume()  # 得到當前音樂播放狀態
        self.sound.stop()  # 進遊戲，結束主音樂

        # Game for night (Lv_1 / Lv_2 / Lv_3)
        if response == 'Lv_1':
            game = Game_night('Lv_1', self.intro.volume, current_volume)
            self.response, self.level_state_night[1] = game.run()
            self.level_menu_night.update_level_state(self.level_state_night)  # update the level state to menu
            self.events["quit"] = game.quit
        elif response == 'Lv_2':
            game = Game_night('Lv_2', self.intro.volume, current_volume)
            self.response, self.level_state_night[2] = game.run()
            self.level_menu_night.update_level_state(self.level_state_night)  # update the level state to menu
            self.events["quit"] = game.quit
        elif response == 'Lv_3':
            game = Game_night('Lv_3', self.intro.volume, current_volume)
            self.response, _ = game.run()
            self.events["quit"] = game.quit

        # Game for day (Lv_Easy / Lv_Hard / Lv_Infinity)
        elif response == 'Lv_Easy':
            game = Game_day('Easy', self.intro.volume, current_volume)
            self.response, self.level_state_day[1] = game.run()
            self.level_menu_day.update_level_state(self.level_state_day)  # update the level state to menu
            self.events["quit"] = game.quit
        elif response == 'Lv_Hard':
            game = Game_day('Hard', self.intro.volume, current_volume)
            self.response, self.level_state_day[2] = game.run()
            self.level_menu_day.update_level_state(self.level_state_day)  # update the level state to menu
            self.events["quit"] = game.quit
        elif response == 'Lv_Infinity':
            game = Game_day('Infinity', self.intro.volume, current_volume)
            self.response, _ = game.run()
            self.events["quit"] = game.quit

        self.play_music_count = 1  # 遊戲出來後，恢復播放主音樂
        if self.events["quit"] is True:
            self.game_request_to_quit = True

    @property
    def quit(self):
        return self.events["quit"]

    @property
    def page_response(self):
        return self.response
