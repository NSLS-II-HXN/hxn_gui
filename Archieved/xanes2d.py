
def zp_list_xanes2d(e_list,dets1,mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t):
    

    ic_0 = sclr2_ch4.get()
    zpssx_i = zpssx.position 
    zpssy_i = zpssy.position

    for i in range (len(e_list)):


        yield from bps.mov(e,e_list[i][0])
        yield from bps.sleep(1)
        yield from bps.mov(ugap, e_list[i][1])
        yield from bps.sleep(1)
        yield from mov_zpz1(e_list[i][2])
        yield from bps.sleep(1)
        yield from bps.mov(crl.p,e_list[i][3])
        yield from bps.sleep(1)

        while (sclr2_ch4.get() < (0.1*ic_0)):
            yield from bps.sleep(60)
            print('IC3 is lower than 10000, waiting...')

        if (sclr2_ch4.get() < (0.9*ic_0)):
            yield from peak_bpm_y(-5,5,5)
            yield from peak_bpm_x(-15,15,5)
            yield from peak_bpm_y(-5,5,5)
        '''
        yield from fly1d(dets1,zpssx,-2, 2,50,0.1)
        xcen = return_line_center(-1,'P',0.75)
        if abs(xcen)<0.5:
            yield from bps.mov(zpssx, xcen)
        '''
        yield from fly2d(dets1, mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t)
        yield from bps.sleep(1)

        insert_xrf_map_to_pdf('Fe', 'sclr1_ch4') 
        insert_xrf_map_to_pdf('P', 'sclr1_ch4')
        
    save_page()