import sys, os, time
from epics import caget


def feedback_auto_off(wait_time_sec = 0.5):
    
    beam_current = "SR:C03-BI{DCCT:1}I:Real-I"
    fe_xbpm_current = "SR:C03-BI{XBPM:1}Ampl:CurrTotal-I"
    fe_shutter_status = "XF:03ID-PPS{Sh:FE}Enbl-Sts"
    ugap = "SR:C3-ID:G1{IVU20:1-Ax:Gap}-Mtr.RBV"

    b_feeback_x = "XF:03ID-BI{EM:BPM1}fast_pidX.FBON"
    b_feeback_y = "XF:03ID-BI{EM:BPM1}fast_pidY.FBON"


    while caget(beam_current)<10 or caget(fe_xbpm_current)<10 or caget(fe_shutter_status)==0:

        if caget(b_feeback_x) == 1 or caget(b_feeback_y) == 1:
            caput(b_feeback_x,0)
            caput(b_feeback_y,0)
            logger.info("feedback disabled")

        else:
            pass
        
        time.sleep(wait_time_sec)






