import interpreter.functions as bot
from interpreter.functions import IMGS, PyAutoGUI_Stopper, RegisterTracker
from interpreter.file_finder import find_shortcut_target
from mylogger.timer import TimeCounter
from mylogger.printer import stenvmsg, stdebug, stfatal, stprint, WHT, YLW, CYN, MGT, RED
from typing import *
import keyboard
import threading
import time

WARNINGS = {'MSG_CRUR.png': {'msg': 'El rango de fechas elegido cruza con otro registro.', 
                             'error': True}, 
            'MSG_CRUL.png': {'msg': 'El trabajador se encuentra en cruce de licencia/subsidio/descanso medico.', 
                             'error': True}, 
            'MSG_LT1Y.png': {'msg': 'El tiempo de servicio del trabajador es menor a 12 meses.', 
                             'error': False}, 
            'MSG_TRNM.png': {'msg': 'Trabajador de reemplazo no puede ser el mismo.', 
                             'error': True}, 
            'MSG_FMAI.png': {'msg': 'Fecha de aprobacion es mayor a la fecha de inicio.', 
                             'error': True}, 
            'MSG_MCDD.png': {'msg': 'Se excede los dias parametrizados al trabajador', 
                             'error': True},
            'MSG_MFDI.png': {'msg': 'Ya existe un registro con la misma fecha de inicio.',
                             'error': True},
            'MSG_RXVF.png': {'msg': 'Cruce de rango de fechas (Se encuentra activo el Registro Automático de Vacaciones Físicas).',
                             'error': True},
            'MSG_SASU.png': {'msg': 'Considerar Sabado y Domingo para completar el bloque de dias fraccionados.',
                             'error': False},
            'MSG_LTDF.png': {'msg': 'Llego al tope de dias fraccionados. Que salga de vacaciones de manera continua.',
                             'error': False},
            'MSG_SDFM.png': {'msg': 'El saldo de dias fraccionados es menor a los que solicita.',
                             'error': False},}

def wait_for_error(wait_for: List[str]=None, delay=0.2):
    if wait_for is None:
        wait_for = list(WARNINGS.keys())

    time.sleep(delay)
    err_img_path = bot.dirjoin(IMGS, 'MSG_ERRO.png')
    error = False

    if bot.find_and_click(err_img_path, n_clicks=0, ignore_fatal=True):

        for img in wait_for:

            stprint(f"Checking if alert [{CYN}{img}{WHT}] is on screen")

            if bot.find_and_click(bot.dirjoin(IMGS, img), n_clicks=0, ignore_fatal=True):
                msg = WARNINGS[img]['msg']
                error = WARNINGS[img]['error']
                RegisterTracker().keep(error, msg)

                stprint(f"Employee {CYN}{RegisterTracker().code}{WHT} saved with '{RED}{msg}{WHT}' message")

        while bot.find_and_click(err_img_path, n_clicks=0, ignore_fatal=True):
            bot.press_keys('enter', wait=0.1)

    return error

def stop_script():
    stenvmsg("Listening for stop command (Esc)...")
    keyboard.wait('esc')
    PyAutoGUI_Stopper().stop()
    stenvmsg(f"{RED}Killed process.")

def start_stop_listener():
    stop_thread = threading.Thread(target=stop_script)
    stop_thread.daemon = True
    stop_thread.start()

if __name__ == '__main__':

    auth = bot.load_credentials('appbotcache.json')
    start_stop_listener()
    stenvmsg('Searching Ofiplan')
    exe_path = find_shortcut_target(auth['shortcut'])

    if exe_path is None:
        stfatal(f"No se encontró el executable para {MGT}{auth['shortcut']}{WHT}.")

    stenvmsg(f"Running {CYN}{auth['shortcut']}{WHT} at {MGT}{exe_path}{WHT}")
    bot.open_exe(exe_path, wait=3)
    TimeCounter().total()

    """keyboard.wait('f1')
    time.sleep(3)
    stenvmsg('Now its my turn')
    """

    IMGS = auth['imgs']

    while True:
        bot.find_and_click(bot.dirjoin(IMGS, 'BTN_CONN.png'))
        bot.write_text(auth['username'], interval=0.05)
        bot.press_keys('tab', delay=0.2)
        bot.write_text(auth['secret'], interval=0.05)
        bot.press_keys('enter', delay=0.4)
        bot.press_keys('enter', delay=0.1, wait=1.5)
        if not bot.find_and_click(bot.dirjoin(IMGS, 'ALR_INVA.png'), n_clicks=0, ignore_fatal=True):
            break
        bot.press_keys('enter')

    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_SIST.png'))
    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_RRHH.png'))
    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_VACA.png'), wait=0.1)


    TimeCounter().total()
    stenvmsg('On main vacations screen.')
    bot.press_keys('space')
    bot.press_keys('enter')
    bot.press_keys('enter')
    bot.press_keys('enter')
    bot.press_keys('enter')

    time.sleep(1)

    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_MANN.png'))
    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_CMAC.png'))
    bot.find_and_click(bot.dirjoin(IMGS, 'BTN_INGR.png'), n_clicks=2, wait=1.5)
    bot.DataFrameIterator().load_from_file(auth['xlsxi'])
    found, x, y = bot.find_image(bot.dirjoin(IMGS, 'PLH_TRAB.png'))
    
    TimeCounter().total()
    stenvmsg('On vacations inputer screen.')
    if found:
        while bot.DataFrameIterator().next_row():
            RegisterTracker().catch(bot.DataFrameIterator().get_by_letter('A'))
            stdebug(f"Inserting employee {YLW}#{RegisterTracker().code}{WHT}.")
            bot.click(x, y, n_clicks=2)
            bot.press_keys('del')
            bot.write_text(RegisterTracker().code)#CODIGO DE TRABAJADOR
            bot.press_keys('tab')
            bot.write_text(bot.DataFrameIterator().get_by_letter('B'))#PERIODO VACACIONAL
            bot.press_keys('tab')
            if wait_for_error():
                continue
            bot.press_keys('tab')
            bot.write_text(bot.DataFrameIterator().get_by_letter('C'))#TIPO VAC
            bot.press_keys('tab')

            if wait_for_error():
                continue
            bot.write_text(bot.DataFrameIterator().get_by_letter('D'))#FECHA INICIAL
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('E'))#No DIAS
            bot.press_keys('tab')

            if wait_for_error(['MSG_LTDF.png', 'MSG_SASU.png', 'MSG_SFDM.png']):
                continue
            
            bot.write_text(bot.DataFrameIterator().get_by_letter('F'))#AÑO
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('G'))#PERIODO
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('H'))#CORRELATIVO
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('I'))#REEMPLAZO
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('J'))#AUTORIZA
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('D'))#FECHA INICIAL X2
            bot.press_keys('tab')

            if wait_for_error():
                continue

            bot.write_text(bot.DataFrameIterator().get_by_letter('K'))# OBSERVACION
            TimeCounter().total()
            if wait_for_error(['MSG_RXVF.png']):
                continue

            elif bot.find_and_click(bot.dirjoin(IMGS, 'BTN_SAVE.png'), wait=0.3, ignore_fatal=True):
                bot.press_keys('enter')
                #bot.find_and_click(bot.dirjoin(IMGS, 'BTN_ISOK.png'), wait=0.2)
        stenvmsg('On report generation.')
        bot.save_dataframe(auth['xlsxo'], RegisterTracker().to_dataframe())
        
    TimeCounter().total()