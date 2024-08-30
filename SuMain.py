from multiprocessing import Process, Queue, Lock
import SuVoc
import json
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)-11s:%(lineno)-3d]  || %(message)s",
                        datefmt="%Y-%m-%d:%H:%M:%S",
                        )
    logging.info('SuVoc started')

    voc_inp_q = Queue()
    voc_outp_q = Queue()

    p_voc = Process(target=SuVoc.SuVocMainFunc, args=(voc_inp_q, voc_outp_q))
    p_voc.start()

    voc_inp_q.put("ky")

    p_voc.join()

