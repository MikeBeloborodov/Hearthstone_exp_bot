import os
import time
import asyncio
from dotenv import load_dotenv
from data.hearthstone_bot import HearthstoneBot
from data.telegram_bot import TelegramBot
from data.args import create_parser
from data.utils import (
    MAX_CRASHES_TRESHOLD,
    T_AFTER_CRASH,
    BATTLE_NET_PLAY_BUTTON,
    BATTLE_NET_CONFIDENCE_TRESHOLD,
    READY_BUTTON,
    GREEN_READY_BUTTON,
    FIGHT_BUTTON,
    ABILITY_ICON,
    ABILITY_ICON_2,
    ABILITY_ICON_3
)
from data.exceptions import (
    MaxTriesReached, 
)


load_dotenv()


async def main():
    """
    Main loop of the bot.
    """

    # Create Hearthstone bot object
    hs_bot = HearthstoneBot()

    # Create Telegram bot object
    tg_bot = TelegramBot(
        token=os.environ["BOT_TOKEN"],
        chat_id=os.environ["MASTER_CHAT_ID"]
    )

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    while hs_bot.crashes_counter < MAX_CRASHES_TRESHOLD:
        try:

            if args.pre_run_menu:
                # Start new run from mercenaries menu
                hs_bot.current_window = 'Hearthstone'
                hs_bot.new_run_from_mercenaries()

                # Send announcements
                hs_bot.games_counter += 1
                announcement = f'Game #{hs_bot.games_counter} started.'
                print(announcement)
                if args.tg_notification:
                    await tg_bot.send_message(message=announcement)

                # Waiting cycle
                args.pre_run_menu = False
                await hs_bot.wait()

            else:
                hs_bot.current_window = 'Battle.net'
                hs_bot.search_and_click_on_target(
                    BATTLE_NET_PLAY_BUTTON,
                    confidence_treshold=BATTLE_NET_CONFIDENCE_TRESHOLD
                )

                hs_bot.current_window = 'Hearthstone'

                if hs_bot.search_multiple_targets(
                    [ABILITY_ICON, ABILITY_ICON_2, ABILITY_ICON_3,
                    READY_BUTTON, GREEN_READY_BUTTON, FIGHT_BUTTON],
                    max_tries=10
                ):

                    # Send pre battle announcements
                    announcement = f'Waiting cycle is finished.'
                    hs_bot.show_desktop_notification(message=announcement)
                    if args.tg_notification:
                        await tg_bot.send_message(message=announcement)

                    # Start battle
                    await hs_bot.battle_sequence(tg_bot)

                    # Collect rewards
                    hs_bot.collect_rewards()

                    # Retire party
                    hs_bot.retire_party()

                    args.pre_run_menu = True

                else:
                    hs_bot.go_to_mercenaries()
                    args.pre_run_menu = True

        except MaxTriesReached as error:

            hs_bot.crashes_counter += 1

            await hs_bot.handle_exception(
                error=error,
                tg_bot=tg_bot
            )

            # Close Hearthstone application
            os.system("taskkill /im Hearthstone.exe")
            args.pre_run_menu = False
            time.sleep(T_AFTER_CRASH)


if __name__ == "__main__":
    asyncio.run(main())