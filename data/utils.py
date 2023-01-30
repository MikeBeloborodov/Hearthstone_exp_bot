from win32api import GetSystemMetrics


"""
Tresholds for cv2
"""
# General treshold
CONFIDENCE_TRESHOLD = 0.5
# Treshold for treasure items
TREASURE_ITEM_CONFIDENCE_TRESHOLD = 0.45
# Enemy treshold
ENEMY_CONFIDENCE_TRESHOLD = 0.5


"""
Various timers in seconds
"""
# Time to sleep between battle cycles 
T_BETWEEN_CYCLES = 1680 # 28 minutes
# Time to sleep after program crashes / reloads
T_AFTER_CRASH = 600

# Max tries to search for a target
MAX_SEARCH_TRIES = 60

# Max tries to search for victory emblem during the battle
MAX_VICTORY_SEARCH = 25

# Max crashes before program stops
MAX_CRASHES_TRESHOLD = 10


"""
Monitor height and width values
"""
MONITOR_WIDTH = GetSystemMetrics(0)
MONITOR_HEIGHT = GetSystemMetrics(1)

"""
Paths to target images
"""
ABILITY_ICON = 'data/images_1600x900/ability_icon.jpg'
ABILITY_ICON_2 = 'data/images_1600x900/ability_icon_2.jpg'
ABILITY_ICON_3 = 'data/images_1600x900/ability_icon_3.jpg'
BATTLE_NET_PLAY_BUTTON = 'data/images_1600x900/battle_net_play_button.jpg'
BATTLE_SPOILS_ICON = 'data/images_1600x900/battle_spoils.jpg'
ENEMY_ICON_1 = 'data/images_1600x900/enemy_1.jpg'
ENEMY_ICON_2 = 'data/images_1600x900/enemy_2.jpg'
ENEMY_ICON_3 = 'data/images_1600x900/enemy_3.jpg'
ENEMY_ICON_4 = 'data/images_1600x900/enemy_4.jpg'
ENEMY_ICON_5 = 'data/images_1600x900/enemy_5.jpg'
ENEMY_ICON_6 = 'data/images_1600x900/enemy_6.jpg'
FIGHT_BUTTON = 'data/images_1600x900/fight_button.jpg'
LOCATION_CHOICE_BUTTON = 'data/images_1600x900/location_choice_button.jpg'
LOCK_PARTY_BUTTON = 'data/images_1600x900/lock_in_party_confirmation_button.jpg'
MERCS_BUTTON = 'data/images_1600x900/mercenaries_button.jpg'
MERCS_CHOOSE_BARRENS = 'data/images_1600x900/mercenaries_choose_barrens.jpg'
MERCS_NEW_RUN = 'data/images_1600x900/mercenaries_new_run.jpg'
PARTY_CHOICE_BUTTON = 'data/images_1600x900/party_choice_button.jpg'
PLAY_BUTTON = 'data/images_1600x900/play_button.jpg'
RETIRE_BUTTON = 'data/images_1600x900/retire_button.jpg'
RETIRE_CONFIRM_BUTTON = 'data/images_1600x900/retire_confirm_button.jpg'
TAKE_TREASURE_BUTTON = 'data/images_1600x900/take_treasure_button.jpg'
TREASURE_ITEM_ICON = 'data/images_1600x900/treasure_item.jpg'
VICTORY_EMBLEM = 'data/images_1600x900/victory_emblem.jpg'
VIEW_PARTY_BUTTON = 'data/images_1600x900/view_party_button.jpg'
YELLOW_PRE_BATTLE_BUTTON = 'data/images_1600x900/yellow_button_pre_battle.jpg'
READY_BUTTON = 'data/images_1600x900/ready_button.jpg'
GREEN_READY_BUTTON = 'data/images_1600x900/green_ready_button.jpg'
LEFT_ARROW = 'data/images_1600x900/left_arrow.jpg'
QUILBOAR_LOCATION = 'data/images_1600x900/quilboar_location.jpg'
YOUR_QUESTS_ICON = 'data/images/your_quests.jpg'
YOUR_WEEKLY_QUESTS = 'data/images/your_weekly_quests.jpg'
CLOSE_BUNDLE = 'data/images/close_bundle.jpg'