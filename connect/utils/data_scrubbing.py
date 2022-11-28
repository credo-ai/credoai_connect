from copy import deepcopy

import numpy as np
import pandas as pd


class Scrubber:
    @staticmethod
    def remove_NaNs(obj):
        if isinstance(obj, pd.DataFrame):
            return Scrubber._df_remove_NaNs(obj)
        elif isinstance(obj, np.ndarray):
            return Scrubber._array_remove_NaNs(obj)
        elif isinstance(obj, dict):
            return Scrubber._dict_remove_NaNs(obj)
        elif isinstance(obj, list):
            return Scrubber._list_remove_NaNs(obj)

    @staticmethod
    def _df_remove_NaNs(data: pd.DataFrame):
        # Assume DataFrame is well-formed: does not contain lists, DFs, or other complex objects
        # returns copy of object --> no deep copy concern
        name = getattr(data, "name", None)
        scrubbed = data.fillna(np.nan).replace([np.nan], [None])
        if name:
            scrubbed.name = name
        return scrubbed

    @staticmethod
    def _list_remove_NaNs(data: list):
        return_list = deepcopy(data)
        for idx, item in enumerate(return_list):
            if isinstance(item, pd.DataFrame):
                return_list[idx] = Scrubber._df_remove_NaNs(item)
            elif isinstance(item, np.ndarray):
                return_list[idx] = Scrubber._array_remove_NaNs(item)
            elif isinstance(item, dict):
                return_list[idx] = Scrubber._dict_remove_NaNs(item)
            elif isinstance(item, list):
                return_list[idx] = Scrubber._list_remove_NaNs(item)
            else:
                # Assume no other iterable data types could be stored in list
                if item is np.nan:
                    return_list[idx] = None
        return return_list

    @staticmethod
    def _array_remove_NaNs(data: np.ndarray):
        # Assume array is well-formed: does not contain lists or other complex objects
        # returns copy of object --> no deep copy concern
        return np.where(np.isnan(data), None, data)

    @staticmethod
    def _dict_remove_NaNs(data: dict):
        return_dict = deepcopy(data)
        for key, val in return_dict.items():
            if isinstance(val, pd.DataFrame):
                return_dict[key] = Scrubber._df_remove_NaNs(val)
            elif isinstance(val, np.ndarray):
                return_dict[key] = Scrubber._array_remove_NaNs(val)
            elif isinstance(val, dict):
                return_dict[key] = Scrubber._dict_remove_NaNs(val)
            elif isinstance(val, list):
                return_dict[key] = Scrubber._list_remove_NaNs(val)
            else:
                # Assume no other iterable data types could be stored in dictionary
                if val is np.nan:
                    return_dict[key] = None
        return return_dict
