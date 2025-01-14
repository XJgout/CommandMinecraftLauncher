import choice
import const
import argparse


def main():
    parser = argparse.ArgumentParser(description="Command Minecraft Launcher")
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
    args = parser.parse_args()

    if args.debug:
        const.DEBUG = True

    choice.first_init_choice()
    choice.main_menu()

if __name__ == '__main__':
    main()