
import io

def open(file, mode='r', **kwargs):
    if not "b" in mode:
        if not "encoding" in kwargs:
            kwargs["encoding"] = 'utf-8'
        if (not "r" in mode or '+' in mode) and not "newline" in kwargs:
            kwargs["newline"] = "\n"
    return io.open(file, mode, **kwargs)

load_api = {}

def load_file(file_, head_exist=True, file_type=None, **kwargs):
    if file_type is None:
        if file_.endswith((".json",".dict")):
            file_type = "json"
        elif file_.endswith(".tsv"):
            file_type = "tsv"
        elif file_.endswith(".csv"):
            file_type = "csv"
        elif file_.endswith(".xlsx"):
            file_type = "xlsx"
        elif file_.endswith(".xls"):
            file_type = "xls"
    if file_type == "json":
        if "json" not in load_api:
            from .json_dict import load_dict
            load_api["json"] = load_dict
    elif file_type == "tsv":
        if "tsv" not in load_api:
            from .text_file import load_tsv
            load_api["tsv"] = load_tsv
    elif file_type == "csv":
        if "csv" not in load_api:
            from .csv_rw import load_csv
            load_api["csv"] = load_csv
    elif file_type == "xlsx":
        if "xlsx" not in load_api:
            from .xlsx_rw import load_xlsx
            load_api["xlsx"] = load_xlsx
    elif file_type == "xls":
        if "xls" not in load_api:
            from .xls_read import load_xls
            load_api["xls"] = load_xls
    else:
        raise RuntimeError("type not supported")
    data_l, fields = load_api[file_type](file_, head_exist, **kwargs)
    return (data_l, fields) if head_exist else data_l
