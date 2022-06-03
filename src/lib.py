import json
import re
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests
import csv
from bs4 import BeautifulSoup

# Saving the absolute path of the current script file to be able to use relative file paths.
# This is necessary because the scripts in this file will be executed from different directories.
from pandas.core.groupby import DataFrameGroupBy

path = Path(__file__).parent


def get_all_packages_names(force_update=False):
    if not force_update and Path(f'{path}/../output/all_libraries.csv').is_file():
        with open(f'{path}/../output/all_libraries.csv', 'r') as file:
            reader = csv.reader(file)
            return list(reader)

    url = 'https://pypi.org/simple/'
    response = requests.get(url)

    souped_response = BeautifulSoup(response.text, 'lxml')
    links = souped_response.find_all('a')
    names_list = [link.get_text() for link in links]

    # Save the list of names to a file, separated by commas.
    with open(f'{path}/../output/all_libraries.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(names_list)
    return names_list


# def get_json_for_package(package_name):
#     url = f'https://pypi.org/pypi/{package_name}/json'
#     response = requests.get(url)
#     json_content_raw = response.text
#     json_content_parsed = json.loads(json_content_raw)
#     return json_content_parsed['info']['requires_dist']


def get_json_for_package(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    response = requests.get(url)
    json_content = response.json()
    return json_content


def get_and_save_dependencies_for_package(package_name):
    dependencies = get_json_for_package(package_name)['info']['requires_dist']
    with open(f'{path}/../output/dependencies/{package_name}.json', 'w') as file:
        json.dump(dependencies, file)


def read_all_packages_metadata_from_file():
    with open('../data/repology/pypicache.json', 'r') as file:
        json_data = json.load(file)
    print(json.dumps(json_data, indent=4))


compiled_rx = re.compile(r'\((?P<version>(?:\w+|\.|=|!|>|<|,|\s)*)\)')


def deprecated_regex_extractor(s: str) -> str:

    found = compiled_rx.findall(s)
    return found[0] if found else "*"


def deprecated_extract_semantic_version(df: pd.DataFrame):
    output_df = df.copy()
    # print(output_df)
    return output_df.astype(str).apply(deprecated_regex_extractor)


def version_extractor(string: str) -> str:
    if not string:
        return '>=0.0.0'
    # Replace ) with ( to make splitting easier and more precise
    split = string.replace(')', '(').split('(')
    # Remove the trailing parenthesis
    return split[1] if len(split) > 1 else '>=0.0.0'


def name_extractor(string: str) -> Optional[str]:
    # If we can't find either symbol, then we assume that's the dependency name
    if not string:
        return None
    if '(' not in string and ';' not in string:
        return string
    # If there are no parenthesis, this will return the given string as a singleton list.
    # If there are parenthesis, get rid of them.
    no_parenthesis = string.split('(')[0]
    no_semicolon = no_parenthesis.split(';')[0].strip()

    return no_semicolon


def extract_name_and_version_from_list(dependencies: List[str]) -> [(str, str)]:
    print(dependencies)
    results: List[(str, str)] = []
    for el in dependencies:
        name = name_extractor(el)
        version = version_extractor(el)
        if name and version:
            results.append((name, version))

    return results


def deprecated_convert_to_normalized_format(grouped_df: DataFrameGroupBy):
    return_list = []
    for _, rows in grouped_df:
        inner_dict = {
            'name': rows['name'].values[0],
            'versions': {
                rows['version'].values[0]: {
                    'timestamp': rows['upload_time'].values[0],
                    'dependencies': {}
                }
            }
        }
        for dep, v in zip(rows['dependency_name'].values, rows['dependency_version'].values):
            inner_dict['versions'][rows['version'].values[0]]['dependencies'] |= {dep: v}
        return_list.append(inner_dict)
    return pd.DataFrame(return_list)


if __name__ == '__main__':
    # print(json.dumps(get_json_for_package('requests'), indent=4))
    read_all_packages_metadata_from_file()

