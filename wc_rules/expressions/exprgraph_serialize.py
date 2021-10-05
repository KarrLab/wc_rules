from .exprgraph_utils import dfs_iter, dfs_visit, dfs_print


def serialize(graph):
	print(dfs_print(graph))