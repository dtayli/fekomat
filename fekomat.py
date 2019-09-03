#!/usr/bin/env python
#
# MIT License
#
# Copyright (c) 2019 Doruk Tayli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# fekomat.py: Converts FEKO impedance matrix files to Matlab (*.mat),
#             Python numpy (*.npy), or CSV.

import os
import argparse
import textwrap
import sys
import struct
import numpy as np
import scipy.io


def read_mat_header(data):
    ''' Reads the header data in FEKO impedance matrix file'''
    mat_header = {'version': ('=iii', (4, 4), 12),
                  'md5': ('=i32ci', (32, 32), 40),
                  'precision': ('=iii', (4, 4), 12),
                  'rows': ('=iii', (4, 4), 12),
                  'cols': ('=iii', (4, 4), 12)}
    mat_precision = {0: 'd', -1: 'f'}
    location = 0
    header_values = []
    for key, (fmt, check, size) in mat_header.items():
        packet = struct.unpack_from(fmt, data, offset=location)
        assert (packet[0], packet[-1]) == check, "Beginning and ending size is incorrect"
        header_values.append(packet[1:-1])
        location += size
    header = dict(zip(mat_header.keys(), header_values))
    header['version'] = header['version'][0]
    header['precision'] = _MAT_PRECISION[header['precision'][0]]
    header['rows'] = header['rows'][0]
    header['cols'] = header['cols'][0]
    return header, location


def read_mat_data(data, header, location):
    ''' Reads the complex matrix data in the FEKO impedance matrix file'''
    rows, cols, precision = header['rows'], header['cols'], header['precision']
    numpy_type, temp_type = (np.cdouble, np.double) if precision == 'd' else (np.csingle, np.single)
    mat_data = np.zeros((rows, cols), dtype=numpy_type)
    fmt_data = 2 * cols * precision
    check = struct.calcsize(fmt_data)
    fmt = '=i' + fmt_data + 'i'
    size = struct.calcsize(fmt)
    for i in range(rows):
        packet = struct.unpack_from(fmt, data, offset=location)
        assert (packet[0], packet[-1]) == (check, check), "Beginning and ending data size is incorrect"
        temp = np.asarray(packet[1:-1], dtype=temp_type)
        mat_data[i, :] = temp[::2] + 1j * temp[1::2]
        location += size
    return mat_data


def main(input_file, output_file, file_type):
    assert os.path.isfile(input_file), "Input file does not exist!"
    assert file_type in ('mat', 'npy', 'csv'), "File type is not one of mat, npy, csv"
    print('Processing input file:', input_file)
    with open(input_file, "rb") as mat_file:
        binary_data = mat_file.read()
    header, location = read_mat_header(binary_data)
    mat_data = read_mat_data(binary_data, header, location)
    if file_type == 'mat':
        scipy.io.savemat(output_file, dict(zip("Zmat", mat_data)))
    elif file_type == 'npy':
        np.save(output_file, mat_data)
    else:
        np.savetxt(output_file, mat_data)
    print('Written output file:', output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''\
             Convert a FEKO matrix file to a Matlab (*.mat) or Python (*.npz) or CSV file

             Example use:
             ------------
             python fekomat.py in.mat out.mat --type mat'''),
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', type=str, nargs=1, help='Input FEKO matrix file')
    parser.add_argument('output', type=str, nargs=1, help='Output file name')
    parser.add_argument('--type', type=str, default='mat',
                        help=textwrap.dedent('''\
                              output file type can be of two types:
                              'mat', Matlab file
                              'npy', Numpy file
                              'csv', comma seperated values'''))
    args = parser.parse_args()
    main(args.input[0], args.output[0], args.type)

