from interpreter.core import AutobotCore

if __name__ == '__main__':

    autobot = AutobotCore(r'STEPS.txt')
    autobot.execute()