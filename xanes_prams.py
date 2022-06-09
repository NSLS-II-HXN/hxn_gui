import json

def createParamsDict(e_low=5.97, e_high=6.03,
                     ugap_low=6616, ugap_high=6665,
                     crl_low=12, crl_high=12, zpz1_low=-6.7657,
                     zpz1_high=-7.1197, crl_combo='8'):
    params = {}
    e_pos = {'low': e_low, 'high': e_high}
    ugap_pos = {'low': ugap_low, 'high': ugap_high}
    crl_pos = {'low': crl_low, 'high': crl_high}
    zpz1_pos = {'low': zpz1_low, 'high': zpz1_high}
    crl_num = {'crl_combo_num': crl_combo}

    params['mono_e'] = e_pos
    params['ugap'] = ugap_pos
    params['crl'] = crl_pos
    params['zpz1'] = zpz1_pos
    params['crl_combo'] = crl_num

    return params


Cr = createParamsDict(e_low=5.97, e_high=6.03,
                      ugap_low=6616, ugap_high=6665,
                      crl_low=12, crl_high=12,
                      zpz1_low=-6.7657, zpz1_high=-7.1197,
                      crl_combo='8')

Mn = createParamsDict(e_low=6.5398, e_high=6.5398 + 0.066,
                      ugap_low=7085, ugap_high=7145,
                      crl_low=-10, crl_high=-10,
                      zpz1_low=-10.9+(0.066*5.9), zpz1_high=-10.9,
                      crl_combo='9+6')

Fe = createParamsDict(e_low=7.1, e_high=7.2,
                      ugap_low=7585, ugap_high=7675,
                      crl_low=-5, crl_high=4,
                      zpz1_low=-9.284+(0.1*5.9), zpz1_high=-9.284,
                      crl_combo='12')

Ni = createParamsDict(e_low=8.355, e_high=8.455,
                      ugap_low=5802, ugap_high=5852,
                      crl_low=4, crl_high=6,
                      zpz1_low=-5.73+(0.1*5.9), zpz1_high=-5.73,
                      crl_combo='12')

Cu = createParamsDict(e_low=8.96, e_high=9.05,
                      ugap_low=6107, ugap_high=6157,
                      crl_low=8, crl_high=10,
                      zpz1_low=-20.5283+(0.09*5.9), zpz1_high=-20.5283,
                      crl_combo='NA')

Zn = createParamsDict(e_low=9.6, e_high=9.7,
                      ugap_low=6435, ugap_high=6485,
                      crl_low=2, crl_high=5,
                      zpz1_low=24.54+(0.1*5.9), zpz1_high=-24.54,
                      crl_combo='NA')

As = createParamsDict(e_low=11.8, e_high=11.9,
                      ugap_low=7590, ugap_high=7680,
                      crl_low=-5, crl_high=5,
                      zpz1_low=-4.15+(0.1*5.9), zpz1_high=-4.15,
                      crl_combo='NA')

Hf_L = createParamsDict(e_low=11.24, e_high=11.34,
                        ugap_low=7280, ugap_high=7335,
                        crl_low=8, crl_high=10,
                        zpz1_low=-34.186+(0.1*5.9), zpz1_high=-34.186,
                        crl_combo='22+8+3')

common_xanes_elem_param = {}

common_xanes_elem_param['Cr K'] = Cr
common_xanes_elem_param['Fe K'] = Fe
common_xanes_elem_param['Mn K'] = Mn
common_xanes_elem_param['Ni K'] = Ni
common_xanes_elem_param['Zn K'] = Zn
common_xanes_elem_param['Cu K'] = Cu
common_xanes_elem_param['As K'] = As
common_xanes_elem_param['Hf L'] = Hf_L

'''
with open('xanes_common_elem_params.json', 'w') as fp:
    json.dump(common_xanes_elem_param, fp, indent=4)
'''
with open('xanes_common_elem_params.json', 'r') as fp:
    XanesParam = json.load(fp)


def fillXanesParamBoxes(XanesParam: dict):
    e_low, e_high = XanesParam['mono_e']['low'], XanesParam['mono_e']['high']
    ugap_low, ugap_high = XanesParam['ugap']['low'], XanesParam['ugap']['high']
    crl_low, crl_high = XanesParam['crl']['low'], XanesParam['crl']['high']
    zpz1_low, zpz1_high = XanesParam['zpz1']['low'], XanesParam['zpz1']['high']
    crl_combo = XanesParam['crl_combo']['crl_combo_num']

    print(type(crl_combo))

fillXanesParamBoxes(XanesParam['Fe K'])