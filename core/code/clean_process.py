import numpy as np
import pandas as pd
from rdkit import Chem
from molvs import Standardizer

VALID_ATOMS = ["C", "O", "N", "S", "P", "F", "I", "Br", "Cl"]
VALID_UNITS = ["ug.mL-1", "nM", "uM"]


class DataCleaner:
    def __init__(self, col_smiles, col_label):
        self.col_smiles = col_smiles
        self.col_label = col_label

    def clean(self, dataframe, task):
        """_summary_

        Args:
            dataframe (_type_): _description_
            task (_type_): _description_

        Returns:
            _type_: _description_
        """
        df = self.remove_nan(dataframe)
        df = self.filter_atoms(df)
        df = self.standardize_smiles(df)
        df = self.remove_duplicates(df, task)

        return df

    def remove_nan(self, dataframe):
        """_summary_

        Args:
            dataframe (_type_): _description_

        Returns:
            _type_: _description_
        """
        data = dataframe.dropna(inplace=False)

        return data

    def filter_atoms(self, dataframe):
        """_summary_

        Args:
            dataframe (_type_): _description_

        Returns:
            _type_: _description_
        """
        valid_molecule = []
        smiles_all = dataframe[self.col_smiles]

        for smiles in smiles_all.values:
            mol = Chem.MolFromSmiles(str(smiles))

            molecule = []
            for atom in mol.GetAtoms():
                atom_str = atom.GetSymbol()
                valid_atom = False

                if atom_str in VALID_ATOMS:
                    valid_atom = True

                molecule.append(valid_atom)

            if len(molecule) >= 2:
                if all(valid is True for valid in molecule):
                    valid_molecule.append(True)
                else:
                    valid_molecule.append(False)

            else:
                valid_molecule.append(False)

        dataframe = dataframe[valid_molecule]
        return dataframe

    def standardize_smiles(self, dataframe):
        """_summary_

        Args:
            dataframe (_type_): _description_

        Returns:
            _type_: _description_
        """
        smiles_all = dataframe[self.col_smiles]
        cols_order = dataframe.columns

        stdz = Standardizer()
        smiles_stdz = []

        for smiles in smiles_all.values:
            mol = Chem.MolFromSmiles(str(smiles))

            mol_stdz = stdz.standardize(mol)
            mol_stdz = stdz.fragment_parent(mol_stdz)

            smiles_stdz.append(Chem.MolToSmiles(mol_stdz))

        assert len(smiles_all) == len(smiles_stdz)

        df = dataframe.drop(columns=[self.col_smiles])
        df.insert(len(cols_order)-1, self.col_smiles, smiles_stdz)
        df = df[cols_order]

        return df

    def remove_duplicates(self, dataframe, task):
        """_summary_

        Args:
            dataframe (_type_): _description_
            task (_type_): _description_

        Returns:
            _type_: _description_
        """
        unique_smiles = dataframe[self.col_smiles].unique()
        df = pd.DataFrame()

        for uni_smiles in unique_smiles:
            selection = dataframe[dataframe[self.col_smiles] == uni_smiles]

            if len(selection) == 1:
                df = pd.concat([df, selection], axis=0)

            else:
                if task == "Classification":
                    selection = _remove_classification(selection,
                                                       self.col_smiles,
                                                       self.col_label)
                else:
                    selection = _remove_regression(selection,
                                                   self.col_smiles,
                                                   self.col_label)

                df = pd.concat([df, selection], axis=0)

        return df


def _remove_classification(selection, col_smiles, col_label):
    unique_labels = selection[col_label].unique()

    if len(unique_labels) == 1:
        dataframe = selection.drop_duplicates(subset=[col_smiles])

    else:
        dataframe = pd.DataFrame()

    return dataframe


def _remove_regression(selection, col_smiles, col_label):
    unique_labels = selection[col_label].unique()

    if len(unique_labels) == 1:
        dataframe = selection.drop_duplicates(subset=[col_smiles])

    else:
        mean_average = selection[col_label].mean()
        dataframe = selection.drop_duplicates(subset=[col_smiles])
        dataframe[col_label] = mean_average

    return dataframe


class BioCleaner:
    def __init__(self, col_smiles, col_strain, col_conv):
        self.col_smiles = col_smiles
        self.col_strain = col_strain
        self.col_conv = col_conv

        self.col_standard = col_conv[0]

    def bio_clean(self, dataframe, strains, threshold):
        """_summary_

        Args:
            dataframe (_type_): _description_
            strains (_type_): _description_
            threshold (_type_): _description_
            task (_type_): _description_

        Returns:
            _type_: _description_

        """

        dclean = DataCleaner(self.col_smiles, self.col_standard)

        df = self.select_strains(dataframe, strains)
        df = dclean.remove_nan(df)
        df = dclean.filter_atoms(df)
        df = self.convert_units(df, threshold)
        # df = self.remove_outlier(df)
        df = dclean.standardize_smiles(df)
        df = self.remove_bioduplicates(df)

        return df

    def select_strains(self, dataframe, strains):
        """_summary_

        Args:
            dataframe (_type_): _description_
            strains (_type_): _description_

        Returns:
            _type_: _description_
        """
        df = dataframe[dataframe[self.col_strain].isin(strains)]

        return df

    def convert_units(self, dataframe, threshold):
        """Convert Standard Value to nM

        Args:
            dataframe (_type_): _description_
            threshold (_type_): _description_

        Returns:
            _type_: _description_
        """
        mol_weight = self.col_conv[0]
        standard_relation = self.col_conv[1]
        standard_value = self.col_conv[2]
        standard_units = self.col_conv[3]

        dataframe = dataframe[dataframe[standard_units].isin(VALID_UNITS)]
        list_weight = list(dataframe[mol_weight])
        list_relations = list(dataframe[standard_relation])
        list_values = list(dataframe[standard_value])
        list_units = list(dataframe[standard_units])

        converted_values = []
        for idx, unit in enumerate(list_units):
            if unit == "ug.mL-1":
                val = (list_values[idx] / float(list_weight[idx])) * 1000
            elif unit == "uM":
                val = list_values[idx] * 1000
            elif unit == "nM":
                val = list_values[idx]

            converted_values.append(val)

        # Create activity lists
        converted_units = ["nM"] * len(list_values)
        converted_activity = ["Inactive"] * len(list_values)
        converted_activity_bin = [0] * len(list_values)

        # Check activity
        for idx, value in enumerate(converted_values):
            # Bellow threshold
            if (">" not in list_relations[idx]) and (value < threshold):
                converted_activity[idx] = "Active"
                converted_activity_bin[idx] = 1

        # Create activity column
        last_col = len(dataframe.columns)
        dataframe.insert(last_col, "Converted Value", converted_values)
        dataframe.insert(last_col+1, "Converted Units", converted_units)
        dataframe.insert(last_col+2, "Activity", converted_activity)
        dataframe.insert(last_col+3, "Bin Activity", converted_activity_bin)

        # Remove inconclusive ">" relations
        dataframe = dataframe[~((dataframe[standard_relation] == "'>'") &
                                (dataframe["Converted Value"] < threshold))]
        dataframe = dataframe[~((dataframe[standard_relation] == "'>='") &
                                (dataframe["Converted Value"] < threshold))]

        return dataframe

    def remove_outlier(self, dataframe):
        """_summary_

        Args:
            dataframe (_type_): _description_

        Returns:
            _type_: _description_
        """
        df_sel = dataframe[self.col_standard]
        q3 = df_sel.quantile(0.75)
        q1 = df_sel.quantile(0.25)

        # IQR filter: within 2.22 IQR (equiv. to z-score < 3)
        iqr = q3 - q1
        diff = df_sel - df_sel.median()
        mask = np.abs(diff / iqr) < 2.22

        # replace outliers with nan
        dataframe.loc[:, self.col_standard] = df_sel.where(mask, np.nan)
        df = dataframe.dropna(subset=self.col_standard, inplace=False)

        return df

    def remove_bioduplicates(self, dataframe):
        """_summary_

        Args:
            dataframe (_type_): _description_

        Returns:
            _type_: _description_
        """
        unique_smiles = dataframe[self.col_smiles].unique()
        df = pd.DataFrame()

        for uni_smiles in unique_smiles:
            selection = dataframe[dataframe[self.col_smiles] == uni_smiles]

            if len(selection) == 1:
                df = pd.concat([df, selection], axis=0)

            else:
                selection = _remove_bio(selection,
                                        self.col_smiles,
                                        "Converted Value")

                df = pd.concat([df, selection], axis=0)

        return df


def _remove_bio(selection, col_smiles, col_value):
    df_sub = selection[col_value]
    unique_labels = df_sub.unique()

    if len(unique_labels) == 1:
        dataframe = selection.drop_duplicates(subset=[col_smiles])

    else:
        # Check biological activity
        if len(selection["Activity"].unique()) == 1:
            dataframe = selection[df_sub == df_sub.max()]
            dataframe = dataframe.iloc[:1]

        else:
            dataframe = pd.DataFrame()

    return dataframe
