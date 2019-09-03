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

3. To convert FEKO impedance matrix to a Matlab data file:
```
python fekomat.py <input_file> <output_file> --type mat
```

4. Use the --help argument to check for other options

## TODO
+ [ ] add option to buffer and read impedance matrix files (will be useful for large files)
