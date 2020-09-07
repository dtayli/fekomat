# Copyright (c) 2019 Doruk Tayli
# test_fekomat.py: Basic tests for reading FEKO impedance matrix files

import os
import struct
import binascii

import numpy as np
import scipy.io

import fekomat
import pytest


def create_test_mat_file(test_file_name, precision, version):
    if precision == np.double:
        mat_precision = 0
        fmt_precision = "d"
    else:
        mat_precision = -1
        fmt_precision = "f"

    header = [
        ((4, version, 4), "=iii"),  # version
        ((32,) + 32 * (b"c",) + (32,), "=i32ci"),  # md5
        ((4, mat_precision, 4), "=iii"),  # precision
        ((4, 3, 4), "=iii"),  # rows
        ((4, 3, 4), "=iii"),
    ]  # cols

    header_dict = {
        "version": 5,
        "md5": 32 * (b"c",),
        "precision": fmt_precision,
        "rows": 3,
        "cols": 3,
    }

    np.random.seed(seed=100)
    mat_data = np.random.randn(3, 6).astype(precision)
    fmt_data = 2 * 3 * fmt_precision
    fmt = "=i" + fmt_data + "i"
    size = struct.calcsize(fmt_data)

    with open(test_file_name, "wb") as test_file:
        for values, line_fmt in header:
            bdata = struct.pack(line_fmt, *values)
            test_file.write(bdata)
        for i in range(3):
            tmp = (
                [
                    size,
                ]
                + list(mat_data[i, :])
                + [
                    size,
                ]
            )
            bdata = struct.pack(fmt, *tmp)
            test_file.write(bdata)
    return header_dict, mat_data[:, ::2] + 1j * mat_data[:, 1::2]


def read_mat_file(test_mat):
    with open(test_mat, "rb") as mat_file:
        header = fekomat.read_mat_header(mat_file)
        mat_data = fekomat.read_mat_data(mat_file, header)
    return header, mat_data


@pytest.mark.parametrize("precision", [np.single, np.double])
def test_fekomat(precision):
    # Create test file
    test_file = "test_mat.mat"
    header, mat_data = create_test_mat_file(test_file, precision, 5)
    header_test, mat_data_test = read_mat_file(test_file)
    assert header == header_test, "Headers don't match!"
    assert np.all(mat_data == mat_data_test), "Matrix data doesn't match!"
    os.remove(test_file)


@pytest.mark.parametrize(
    "file_type, out_file",
    [("mat", "test_out.mat"), ("npy", "test_out.npy"), ("csv", "test_out.csv")],
)
def test_output_types(file_type, out_file):
    test_file = "test_mat.mat"
    header, mat_data = create_test_mat_file(test_file, np.double, 5)
    fekomat.main(test_file, out_file, file_type)
    if file_type == "mat":
        zmat = scipy.io.loadmat(out_file)["Zmat"]
    elif file_type == "npy":
        zmat = np.load(out_file)
    else:
        zmat = np.loadtxt(out_file, dtype=np.dtype("cdouble"), delimiter=",")
    assert np.allclose(mat_data, zmat)
    os.remove(out_file)
