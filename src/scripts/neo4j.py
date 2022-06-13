#!/usr/bin/env python
# coding: utf-8
import json
import multiprocessing
from functools import partial
from multiprocessing import Pool

from py2neo import Graph
from py2neo.bulk import create_relationships
from semantic_version import SimpleSpec, Version

# graph = Graph('bolt://localhost:7687', auth=('neo4j', 'softwareThatMatters'))
#
# input_data: dict[str, dict[str, dict]]
# with open('../../data/output/neo4j_data.json', 'r') as file:
#     input_data = json.load(file)
#
# keys = ['name', 'version', 'timestamp']
# nodes: list[list] = []
# for package in input_data.values():
#     for version_name, version_data in package['versions'].items():
#         nodes.append([package['name'], version_name, version_data['timestamp']])


# In[7]:


# batch_size = 1_000_000
#
# batches = np.array_split(nodes, batch_size)
#
# for batch in batches:
#     create_nodes(graph.auto(), batch.tolist(), labels={"NameVersion"}, keys=keys)

# while True:
#     batch = islice(stream, batch_size)
#     if batch:
#         create_nodes(graph.auto(), batch, labels={"NameVersion"}, keys=keys)
#     else:
#         break


# In[8]:


def create_relationship_data(inp: dict[str, dict[str, dict]]):
    graph = Graph('bolt://localhost:7687', auth=('neo4j', 'softwareThatMatters'))
    keys = set(inp.keys())
    relationship_data = []
    for index, (pack_name, pack) in enumerate(inp.items()):
        
        for version_name, version_data in pack['versions'].items():
            dependent_info = (pack_name, version_name, version_data['timestamp'])
            for dependency_name, dependency_version_constraint in version_data['dependencies'].items():

                try:
                    spec = SimpleSpec(dependency_version_constraint)
                except ValueError:
                    # Ignore dependencies with non-standard formats
                    continue
                if dependency_name in keys:
                    for dependency_version in inp[dependency_name]['versions'].keys():

                        try:
                            semver_version = Version(dependency_version)
                        except ValueError:
                            continue

                        if spec.match(semver_version):
                            dependency_info = (dependency_name, dependency_version,
                                               inp[dependency_name]['versions'][dependency_version]['timestamp'])
                            relationship_data.append((dependent_info, {}, dependency_info))

        if index % 10_000:
            print((index / len(inp)) * 100, "% done!")
            create_relationships(graph.auto(), relationship_data, "DEPENDS_ON",
                                 start_node_key=('NameVersion', 'name', 'version', 'timestamp'),
                                 end_node_key=('NameVersion', 'name', 'version', 'timestamp'))
            relationship_data.clear()


# In[ ]:


# This could be converted to a multiprocessing pool
# for package in input_data.values():
if __name__ == "__main__":
    input_data: dict[str, dict[str, dict]]
    with open('../../data/output/neo4j_data.json', 'r') as file:
        input_data = json.load(file)

    # global graph
    # graph = Graph('bolt://localhost:7687', auth=('neo4j', 'softwareThatMatters'))
    # global k
    # k = list(input_data.keys())
    #
    # with Pool(multiprocessing.cpu_count()) as pool:
    #     partial_function = partial(create_relationship_data, keys=k, g=graph)
    #     # results = pool.map(create_relationship_data, input_data.values())
    #     pool.map(partial_function, input_data.values())

    create_relationship_data(input_data)


# flat_results = sum(results, [])
# compatible_dependency_versions = spec.filter((Version.coerce(version) for version in input_data[dependency_name]['versions'].keys()))
# for compatible_dependency_version in compatible_dependency_versions:
#     compatible_dependency_version_str = str(compatible_dependency_version)
#     dependency_info = (dependency_name, compatible_dependency_version_str, input_data[dependency_name]['versions'][compatible_dependency_version_str]['timestamp'])
#     relationship_data.append((dependent_info, {}, dependency_info))
# flat_results[:100]
