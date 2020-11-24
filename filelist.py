# parse configs for access and distribution switches
# you should theoretically add all switches in the DC

entiredc = {'agg': {"conf": ['config/AGGSNANGDC-1.nxos', 'config/AGGSNANGDC-2.nxos'],
                    "intstatus": ['config/AGGSNANGDC-1.intstatus', 'config/AGGSNANGDC-2.intstatus']},
            'aggp': {"conf": ['config/AGGSNANGDCP-1.nxos', 'config/AGGSNANGDCP-2.nxos'],
                     "intstatus": ['config/AGGSNANGDCP-1.intstatus', 'config/AGGSNANGDCP-2.intstatus']},
            'core': {"conf": ['config/CORESNANGDC-1.nxos', 'config/CORESNANGDC-2.nxos'],
                     "intstatus": ['config/CORESNANGDC-1.intstatus', 'config/CORESNANGDC-2.intstatus']},
            'H1-2': {"conf": ['config/SWISNA-NGDC5K-H1.nxos', 'config/SWISNA-NGDC5K-H2.nxos'],
                     "intstatus": ['config/SWISNA-NGDC5K-H1.intstatus', 'config/SWISNA-NGDC5K-H2.intstatus']},
            'H3-4': {"conf": ['config/SWISNA-NGDC5K-H3.nxos', 'config/SWISNA-NGDC5K-H4.nxos'],
                     "intstatus": ['config/SWISNA-NGDC5K-H3.intstatus', 'config/SWISNA-NGDC5K-H4.intstatus']},
            'L1-2': {"conf": ['config/SWISNA-NGDC5K-L1.nxos', 'config/SWISNA-NGDC5K-L2.nxos'],
                     "intstatus": ['config/SWISNA-NGDC5K-L1.intstatus', 'config/SWISNA-NGDC5K-L2.intstatus']},
            'L3-4': {"conf": ['config/SWISNA-NGDC5K-L3.nxos', 'config/SWISNA-NGDC5K-L4.nxos'],
                     "intstatus": ['config/SWISNA-NGDC5K-L3.intstatus', 'config/SWISNA-NGDC5K-L4.intstatus']},
            'L5-6': {"conf": ['config/SWISNA-NGDC5K-L5.nxos', 'config/SWISNA-NGDC5K-L6.nxos'],
                     "intstatus": ['config/SWISNA-NGDC5K-L5.intstatus', 'config/SWISNA-NGDC5K-L6.intstatus']},
            }
