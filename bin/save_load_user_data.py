import work_materials.globals
import time, pickle
import logging, sys

log = logging.getLogger("Save load user data")

def loadData():
    try:
        f = open('backup/userdata', 'rb')
        work_materials.globals.dispatcher.user_data = pickle.load(f)
        f.close()
        print("Data picked up")
    except FileNotFoundError:
        logging.error("Data file not found")
    except Exception:
        logging.error(sys.exc_info()[0])


def saveData():
    need_exit = 0
    while need_exit == 0:
        for i in range(0, 5):
            time.sleep(5)
            if work_materials.globals.processing == 0:
                    need_exit = 1
                    break
        # Before pickling
        log.debug("Writing data, do not shutdown bot...\r")
        if need_exit:
            log.warning("Writing data last time, do not shutdown bot...")

        try:
            f = open('backup/userdata', 'wb+')
            pickle.dump(work_materials.globals.dispatcher.user_data, f)
            f.close()
            log.debug("Data write completed\b")
        except Exception:
            logging.error(sys.exc_info()[0])
