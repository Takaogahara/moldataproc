# **Molecular Dataset Processing**

<p align="center">
    <a href="https://moldataproc.streamlit.app/" alt="Streamlit App">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg"/> </a>
</p>

_____________________________________________________________________________________


### **Latest version: 0.0.2**
<br/>

## Features of this package
- [x] Select desired columns from dataset
- [x] Remove columns with NaN values
- [x] Filter molecules with undesired atoms
- [x] Standardize Smiles
- [x] Remove duplicates

_____________________________________________________________________________________
<br/>

## ⚙️ **Installation**

1. Install Python3-tk and python3-dev with the command:

    ```console
    sudo apt install python3-dev python3-tk
    ```

2. Clone the repo using the following command:

    ```console
    git clone git@github.com:Takaogahara/molproc.git
    ```

3. Create and activate your `virtualenv` with Python, for example as described [here](https://docs.python.org/3/library/venv.html).

4. Install required libraries using:

    ```console
    python -m pip install -r requirements.txt
    ```

_____________________________________________________________________________________
<br/>

## 🔎 **Usage**
With all parameters configured correctly and with the `virtualenv` activated, you can proceed to the execution.

From the root folder, open the terminal and run:

  ```console
  streamlit run run.py
  ```
