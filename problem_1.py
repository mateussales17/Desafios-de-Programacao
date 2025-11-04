import csv

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Optional


def parse_date(date_str: str) -> datetime.date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def reconcile_accounts(list1: [list[list[str]]], list2: [list[list[str]]]) -> tuple[list[list[str]], list[list[str]]]:

    hashmap_list2 = defaultdict(list)
    _ = [hashmap_list2[(dpt, vl, bnf)].append((parse_date(dt), i)) for i, (dt, dpt, vl, bnf) in enumerate(list2)]

    for key in hashmap_list2:
        hashmap_list2[key].sort(key=lambda x: x[0])

    out_list1 = list1.copy()
    out_list2 = list2.copy()

    transactions_found = set()

    def find_match(date: datetime.date, department: str, value: str, beneficiary: str) -> Optional[int]:
        key = (department, value, beneficiary)
        for d, i in hashmap_list2.get(key, []):
            if i in transactions_found:
                continue
            if abs((d - date).days) <= 1:
                return i
        return None

    for t in out_list1:
        t_date = parse_date(t[0])
        t_department, t_value, t_beneficiary = t[1], t[2], t[3]

        match_idx = find_match(t_date, t_department, t_value, t_beneficiary)
        if match_idx is not None:
            t.append('FOUND')
            out_list2[match_idx].append('FOUND')
            transactions_found.add(match_idx)
        else:
            t.append('MISSING')

    _ = [out_list2[i].append('MISSING') for i in range(len(out_list2)) if i not in transactions_found]

    return out_list1, out_list2

if __name__ == '__main__':
    transactions1 = list(csv.reader(Path('test_data/transactions1.csv').open()))
    transactions2 = list(csv.reader(Path('test_data/transactions2.csv').open()))
    out1, out2 = reconcile_accounts(transactions1, transactions2)
    pprint(out1)
    pprint(out2)