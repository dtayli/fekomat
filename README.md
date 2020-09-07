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

3. Use the python `Pipenv` to install the `fekomat` package
```
pipenv install
```

4. Open `pipenv` shell
```
pipenv shell
```

5. (Optional) Test `fekomat` script
```
pytest test_fekomat.py
```

6. To convert FEKO impedance matrix to a Matlab data file:
```
python fekomat.py <input_file> <output_file> --type mat
```

7. Use the --help argument to check for other options
