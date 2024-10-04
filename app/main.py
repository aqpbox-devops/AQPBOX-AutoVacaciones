import interpreter.functions as bot
from mylogger.timer import TimeCounter
from mylogger.printer import stenvmsg, stdebug, WHT, YLW
import pandas as pd
import time

def write_register(report, employee_code, registered: bool, warning):
    report['CODIGO DE TRABAJADOR'].append(employee_code)
    report['REGISTRADO'].append('SI' if registered else 'NO')
    report['MENSAJE DE ADVERTENCIA'].append(warning)

if __name__ == '__main__':

    auth = bot.load_credentials('botcache.json')

    stenvmsg('Running Ofiplan')
    bot.open_exe(auth['exe'], wait=1.2)
    bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_SIST.png'))
    bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_RRHH.png'))
    bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_VACA.png'))
    bot.write_text(auth['username'])
    bot.press_keys('tab', delay=0.1)
    bot.write_text(auth['secret'])
    bot.press_keys('enter', delay=0.25)
    bot.press_keys('enter', delay=0.2, wait=1.5)

    if bot.find_and_click(bot.dirjoin(auth['imgs'], 'ASK_OPEN.png'), n_clicks=0):
        TimeCounter().total()
        stenvmsg('On main vacations screen.')
        bot.press_keys('space')
        bot.press_keys('enter')
        bot.press_keys('enter')
        bot.press_keys('enter', wait=1.5)

        bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_MANN.png'))
        bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_CMAC.png'))
        bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_INGR.png'), n_clicks=2, wait=1.5)
        bot.DataFrameIterator().load_from_file(auth['xlsxi'])
        found, x, y = bot.find_image(bot.dirjoin(auth['imgs'], 'PLH_TRAB.png'))
        
        TimeCounter().total()
        stenvmsg('On vacations inputer screen.')
        if found:
            report = {'CODIGO DE TRABAJADOR': [], 'REGISTRADO': [], 'MENSAJE DE ADVERTENCIA': []}
            while bot.DataFrameIterator().next_row():
                warning = 'Error en general, no se pudo registrar'
                employee_code = bot.DataFrameIterator().get_by_letter('A')
                registered = False
                stdebug(f"Inserting employee {YLW}#{employee_code}{WHT}.")
                bot.click(x, y, n_clicks=2)
                bot.press_keys('del')
                bot.write_text(employee_code)
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('B'))
                bot.press_keys('tab')
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('C'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('D'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('E'))
                bot.press_keys('tab')
                time.sleep(0.1)
                if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_ERRO.png'), n_clicks=0):
                    if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_CRUR.png'), n_clicks=0):
                        warning = 'El rango de fechas elegido cruza con otro registro.'
                        write_register(report, employee_code, registered, warning)
                    elif bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_LT1Y.png'), n_clicks=0):
                        warning = 'El tiempo de servicio del trabajador es menor a 12 meses.'
                        registered = True
                        write_register(report, employee_code, registered, warning)

                    time.sleep(2)
                    bot.press_keys('enter')

                    if registered:
                        stdebug('NO CONTINUA INSERTANDO')
                        continue
                
                bot.write_text(bot.DataFrameIterator().get_by_letter('F'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('G'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('H'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('I'))
                bot.press_keys('tab')
                if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_ERRO.png'), n_clicks=0):
                    if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_TRNM.png'), n_clicks=0):
                        warning = 'Trabajador de reemplazo no puede ser el mismo.'
                    
                    write_register(report, employee_code, registered, warning)

                    time.sleep(2)
                    bot.press_keys('enter')
                    continue
                bot.write_text(bot.DataFrameIterator().get_by_letter('J'))
                bot.press_keys('tab')
                bot.write_text(bot.DataFrameIterator().get_by_letter('D'))
                bot.press_keys('tab')
                if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_ERRO.png'), n_clicks=0):
                    if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_FMAI.png'), n_clicks=0):
                        warning = 'Fecha de aprobacion mayor a fecha de inicio.'
                    
                    write_register(report, employee_code, registered, warning)
                    time.sleep(2)
                    bot.press_keys('enter')
                    continue
                bot.write_text(bot.DataFrameIterator().get_by_letter('K'))
                
                if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_ERRO.png'), n_clicks=0):
                    if bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_CRUL.png'), n_clicks=0):
                        warning = 'El trabajador se encuentra en cruce de licencia/subsidio/descanso medico.'
                    elif bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_MCDO.png'), n_clicks=0):
                        warning = 'Se excede los dias parametrizados al trabajador'
                    elif bot.find_and_click(bot.dirjoin(auth['imgs'], 'MSG_LT1Y.png'), n_clicks=0):
                        warning = 'El tiempo de servicio del trabajador es menor a 12 meses.'

                    write_register(report, employee_code, registered, warning)
                    time.sleep(2)
                    bot.press_keys('enter')

                elif bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_SAVE.png'), wait=0.3, ignore_fatal=True):
                    bot.press_keys('enter')
                    #bot.find_and_click(bot.dirjoin(auth['imgs'], 'BTN_ISOK.png'), wait=0.2)
                TimeCounter().total()
            stenvmsg('On report generation.')
            bot.save_dataframe(auth['xlsxo'], pd.DataFrame(report))
            
        TimeCounter().total()