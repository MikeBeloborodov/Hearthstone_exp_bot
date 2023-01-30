from win32api import GetSystemMetrics


"""
Tresholds for cv2
"""
# General treshold
CONFIDENCE_TRESHOLD = 0.7
# Treshold for treasure items
TREASURE_ITEM_CONFIDENCE_TRESHOLD = 0.4
# Enemy treshold
ENEMY_CONFIDENCE_TRESHOLD = 0.2


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
ABILITY_ICON = 'data/images/ability_icon.jpg'
ABILITY_ICON_2 = 'data/images/ability_icon_2.jpg'
ABILITY_ICON_3 = 'data/images/ability_icon_3.jpg'
BATTLE_NET_PLAY_BUTTON = 'data/images/battle_net_play_button.jpg'
BATTLE_SPOILS_ICON = 'data/images/battle_spoils.jpg'
ENEMY_ICON = 'data/images/enemy.jpg'
FIGHT_BUTTON = 'data/images/fight_button.jpg'
LOCATION_CHOICE_BUTTON = 'data/images/location_choice_button.jpg'
LOCK_PARTY_BUTTON = 'data/images/lock_in_party_confirmation_button.jpg'
MERCS_BUTTON = 'data/images/mercenaries_button.jpg'
MERCS_CHOOSE_BARRENS = 'data/images/mercenaries_choose_barrens.jpg'
MERCS_NEW_RUN = 'data/images/mercenaries_new_run.jpg'
PARTY_CHOICE_BUTTON = 'data/images/party_choice_button.jpg'
PLAY_BUTTON = 'data/images/play_button.jpg'
RETIRE_BUTTON = 'data/images/retire_button.jpg'
RETIRE_CONFIRM_BUTTON = 'data/images/retire_confirm_button.jpg'
TAKE_TREASURE_BUTTON = 'data/images/take_treasure_button.jpg'
TREASURE_ITEM_ICON = 'data/images/treasure_item.jpg'
VICTORY_EMBLEM = 'data/images/victory_emblem.jpg'
VIEW_PARTY_BUTTON = 'data/images/view_party_button.jpg'
YELLOW_PRE_BATTLE_BUTTON = 'data/images/yellow_button_pre_battle.jpg'
YOUR_QUESTS_ICON = 'data/images/your_quests.jpg'
YOUR_WEEKLY_QUESTS = 'data/images/your_weekly_quests.jpg'
READY_BUTTON = 'data/images/ready_button.jpg'
GREEN_READY_BUTTON = 'data/images/green_ready_button.jpg'