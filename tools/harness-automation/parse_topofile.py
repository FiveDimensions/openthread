#!/usr/bin/env python
#
# Copyright (c) 2020, The OpenThread Authors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""
parse_topofile.py
-----------------
This script is used to parse TopologyConfig.txt file to list vendor device info
when preparing for the Thread Certification testbed

usage: parse_topofile.py [-h] [-f TOPO_FILE] [-c CASE_LIST [CASE_LIST ...]]

    parse TopologyConfig file and list all devices by case

    optional arguments:
      -h, --help            show this help message and exit
      -f TOPO_FILE          Topology config file (default: C:/GRL/Thread1.1/Thread
                            _Harness/TestScripts/TopologyConfig.txt)
      -c CASE_LIST [CASE_LIST ...]
                            Test case list (e.g. 5.1.1 9.2.1, default: all)

Examples:
    1. Get case 5.1.1 vendor info
       cmd:   python parse_topofile.py -f TopologyConfig.txt -c 5.1.1
       output:
       case 5.1.1:
            role-vendor pair: [('Leader', 'ARM'), ('Router_1', 'ARM')]
            vendor devices  : {'ARM': 2}

       Testbed needed vendor devices:{'ARM': 2}

    2. Get case 5.1.1 and 5.2.1 vendor info
       cmd:    python parse_topofile.py -f TopologyConfig.txt -c 5.1.1 5.2.1
       output:
       case 5.1.1:
           role-vendor pair: [('Leader', 'ARM'), ('Router_1', 'ARM')]
           vendor devices  : {'ARM': 2}
       case 5.2.1:
           role-vendor pair: [('Leader', 'OpenThread'), ('REED_1', 'Kirale'), ('MED_1', 'SiLabs')]
           vendor devices  : {'OpenThread': 1, 'Kirale': 1, 'SiLabs': 1}

       Testbed needed vendor devices:{'ARM': 2, 'OpenThread': 1, 'Kirale': 1, 'SiLabs': 1}

    3. Get all cases vendor info
       cmd:    python parse_topofile.py -f TopologyConfig.txt
       output:
           ... ... ...

       Testbed needed vendor devices:{'ARM': 4, 'NXP': 5, 'OpenThread': 5, 'Kirale': 6, 'SiLabs': 5, 'Any': 7}

"""

import argparse
import logging
import re
from collections import Counter

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
MAX_VENDOR_DEVICE = 32


def device_calculate(topo_file, case_list):
    testbed_vendor_dict = Counter()
    with open(topo_file, 'r') as f:
        for line in f:

            case_vendor_dict = Counter()

            if not line:
                break
            line = line.strip()

            try:
                if re.match(r'\s*#.*', line):
                    continue

                matched_case = re.match(r'(.*)-(.*)', line, re.M | re.I)

                if 'all' not in case_list and matched_case.group(
                        1) not in case_list:
                    continue

                logging.info('case %s:' % matched_case.group(1))
                if 'all' not in case_list:
                    case_list.remove(matched_case.group(1))
                role_vendor_str = matched_case.group(2)
                role_vendor_raw_list = re.split(',', role_vendor_str)
                role_vendor_list = []

                for device_pair in role_vendor_raw_list:
                    device_pair = re.split(':', device_pair)
                    role_vendor_list.append(tuple(device_pair))
                logging.info('\trole-vendor pair: %s' % role_vendor_list)
            except Exception as e:
                logging.info('Unrecognized format: %s\n%s' % (line, format(e)))
                raise

            for _, vendor in role_vendor_list:
                case_vendor_dict[vendor] += 1
                testbed_vendor_dict[vendor] = max(testbed_vendor_dict[vendor],
                                                  case_vendor_dict[vendor])

            logging.info('\tvendor devices  : %s' % dict(case_vendor_dict))

    if case_list and 'all' not in case_list:
        logging.info('Case %s not found' % str(case_list)[1:-1])

    # vendor 'Any' stands for any other vendors
    # override 'Any' counter when overlapping with other vendors
    count_any = MAX_VENDOR_DEVICE
    for key in testbed_vendor_dict:
        if key != 'Any':
            count_any -= testbed_vendor_dict[key]
        if 'Any' in testbed_vendor_dict:
            testbed_vendor_dict['Any'] = count_any

    logging.info('\nTestbed needed vendor devices:%s' %
                 dict(testbed_vendor_dict))


def main():
    parser = argparse.ArgumentParser(
        description='parse TopologyConfig file and list all devices by case')
    parser.add_argument(
        '-f',
        dest='topo_file',
        default='C:/GRL/Thread1.1/Thread_Harness/TestScripts/TopologyConfig.txt',
        help=
        'Topology config file (default: C:/GRL/Thread1.1/Thread_Harness/TestScripts/TopologyConfig.txt)',
    )

    parser.add_argument('-c',
                        dest='case_list',
                        nargs='+',
                        default=['all'],
                        help='Test case list (e.g. 5.1.1 9.2.1, default: all) ')
    args = parser.parse_args()
    device_calculate(args.topo_file, args.case_list)


if __name__ == '__main__':
    main()
