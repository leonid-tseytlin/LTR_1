from multiprocessing import Process, Queue, Lock
import SuVoc
import SuParser
import SuFront
import json
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)-19s:%(lineno)-3d]  || %(message)s",
                        datefmt="%Y-%m-%d:%H:%M:%S",
                        )
    logging.info('SuVoc started')

    front_to_voc_q = Queue()
    voc_to_front_q = Queue()

    p_voc = Process(target=SuVoc.su_voc_main_func, args=(front_to_voc_q, voc_to_front_q))
    p_voc.start()
#    p_voc.join()
    p_front = Process(target=SuFront.su_front_main_func, args=(voc_to_front_q, front_to_voc_q))
    p_front.start()

#    p_front.join()

