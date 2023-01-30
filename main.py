import os
import time
import asyncio
from dotenv import load_dotenv
from data.hearthstone_bot import HearthstoneBot
from data.telegram_bot import TelegramBot
from data.args import create_parser
from data.exceptions import MaxTriesReached
from data.utils import (
    MAX_CRASHES_TRESHOLD,
    T_AFTER_CRASH,
    BATTLE_NET_PLAY_BUTTON,
    READY_BUTTON,
    GREEN_READY_BUTTON,
    FIGHT_BUTTON,
    VICTORY_EMBLEM
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

    games_counter = 0
    crashes_counter = 0
    while crashes_counter < MAX_CRASHES_TRESHOLD:
        try:

            if args.pre_run_menu:
                # Start new run from mercenaries menu
                hs_bot.new_run_from_mercenaries()

                # Send announcements
                games_counter += 1
                announcement = f'Game #{games_counter} started.'
                print(announcement)
                if args.tg_notification:
                    await tg_bot.send_message(message=announcement)

                # Waiting cycle
                await hs_bot.wait()

                # Send pre battle announcements
                announcement = f'Waiting cycle is finished.'
                hs_bot.show_desktop_notification(message=announcement)
                if args.tg_notification:
                    await tg_bot.send_message(message=announcement)

                # Start battle
                hs_bot.battle_sequence()

                # Collect rewards
                hs_bot.collect_rewards()

                # Retire party
                hs_bot.retire_party()

            else:

                hs_bot.search_and_click_on_target(BATTLE_NET_PLAY_BUTTON)

                if hs_bot.search_multiple_targets(
                    [READY_BUTTON, GREEN_READY_BUTTON, FIGHT_BUTTON], 
                    max_tries=5
                ):
                    hs_bot.click_on_target()

                    if not hs_bot.is_target_on_screen(
                        VICTORY_EMBLEM,
                        max_tries=30
                    ):
                        hs_bot.battle_sequence()

                    hs_bot.collect_rewards()
                    hs_bot.retire_party()
                    args.pre_run_menu = True
                    continue

                hs_bot.go_to_mercenaries()
                args.pre_run_menu = True

        except MaxTriesReached as error:

            crashes_counter += 1

            screenshot_path = hs_bot.save_screenshot(folder='errors')

            error_message = (
                f'Max search tries reached during the game #{games_counter}. '
                f'Crash #{crashes_counter}.'
            )
            await tg_bot.send_message(
                message=error_message
            )
            await tg_bot.send_document(
                document_path=screenshot_path
            )

            print(error)

            # Close Hearthstone application
            os.system("taskkill /im Hearthstone.exe")
            args.pre_run_menu = False
            time.sleep(T_AFTER_CRASH)


if __name__ == "__main__":
    asyncio.run(main())