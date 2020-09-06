#!/usr/bin/env python
#
# Copyright (c) 2019 Doruk Tayli
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


def read_mat_header(mat_file):
    """Reads the header data in FEKO impedance matrix file"""
    mat_header = {
        "version": ("=iii", (4, 4), 12),
        "md5": ("=i32ci", (32, 32), 40),
        "precision": ("=iii", (4, 4), 12),
        "rows": ("=iii", (4, 4), 12),
        "cols": ("=iii", (4, 4), 12),
    }
    mat_precision = {0: "d", -1: "f"}
    header_values = []
    for key, (fmt, check, size) in mat_header.items():
        data = mat_file.read(size)
        packet = struct.unpack(fmt, data)
        assert (
            packet[0],
            packet[-1],
        ) == check, "Beginning and ending size is incorrect"
        header_values.append(packet[1:-1])
    header = dict(zip(mat_header.keys(), header_values))
    header["version"] = header["version"][0]
    try:
        assert header["version"] == 5
    except AssertionError:  # pragma: no cover
        print(
            "Warning: FEKO impedance matrix file version is not supported!\
              Please check output filefor correctness."
        )
    header["precision"] = mat_precision[header["precision"][0]]
    header["rows"] = header["rows"][0]
    header["cols"] = header["cols"][0]
    return header


def read_mat_data(mat_file, header):
    """Reads the complex matrix data in the FEKO impedance matrix file"""
    rows, cols, precision = header["rows"], header["cols"], header["precision"]
    numpy_type, temp_type = (
        (np.cdouble, np.double) if precision == "d" else (np.csingle, np.single)
    )
    mat_data = np.zeros((rows, cols), dtype=numpy_type)
    fmt_data = 2 * cols * precision
    check = struct.calcsize(fmt_data)
    fmt = "=i" + fmt_data + "i"
    size = struct.calcsize(fmt)
    for i in range(rows):
        data = mat_file.read(size)
        packet = struct.unpack(fmt, data)
        assert (packet[0], packet[-1]) == (
            check,
            check,
        ), "Beginning and ending data size is incorrect"
        temp = np.asarray(packet[1:-1], dtype=temp_type)
        mat_data[i, :] = temp[::2] + 1j * temp[1::2]
    return mat_data


def main(input_file, output_file, file_type):
    assert os.path.isfile(input_file), "Input file does not exist!"
    assert file_type in ("mat", "npy", "csv"), "File type is not one of mat, npy, csv"
    print("Processing input file:", input_file)
    with open(input_file, "rb") as mat_file:
        header = read_mat_header(mat_file)
        mat_data = read_mat_data(mat_file, header)
    if file_type == "mat":
        scipy.io.savemat(output_file, dict(Zmat=mat_data))
    elif file_type == "npy":
        np.save(output_file, mat_data)
    else:
        np.savetxt(output_file, mat_data, delimiter=",")
    print("Written output file:", output_file)


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
             Convert a FEKO matrix file to a Matlab (*.mat) or Python (*.npy) or CSV file

             Example use:
             ------------
             python fekomat.py in.mat out.mat --type mat"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input", type=str, nargs=1, help="Input FEKO matrix file")
    parser.add_argument("output", type=str, nargs=1, help="Output file name")
    parser.add_argument(
        "--type",
        type=str,
        default="mat",
        help=textwrap.dedent(
            """\
                              output file type can be of three types:
                              'mat', Matlab file (default)
                              'npy', Numpy file
                              'csv', comma seperated values"""
        ),
    )
    args = parser.parse_args()
    main(args.input[0], args.output[0], args.type)
