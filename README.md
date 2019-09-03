# fekomat

`fekomat` is a simple python tool to convert FEKO impedance matrices to Matlab, Numpy and CSV files.

## Usage

1. Clone the repository
```
git clone https://github.com/dtayli/fekomat.git fekomat
```

2. Change to fekomat directory
```
cd fekomat
```

3. (Optional) Test `fekomat` script
```
pytest test_fekomat.py
```

4. To convert FEKO impedance matrix to a Matlab data file:
```
python fekomat.py <input_file> <output_file> --type mat
```

5. Use the --help argument to check for other options
