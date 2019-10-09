#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/16 0:25
# @Author  : flyhawk
# @Site    : 
# @File    : question_shortest_path_graph_adj_matrix.py
# @Software: PyCharm Community Edition

from ClassGraphMatrix import GraphMatrix
from queue import Queue
import heapq as hq
import numpy as np
# import pandas as pd


# bfs_queue method
def shortest_path_unweighted_graph_adjacency_matrix(graph, start_v, end_v):
    """
	
	:param graph:
	:param start_v: string 'a'
	:param end_v:  string 'h'
	:return: distance, previous_vertex, visited_order
	"""

    def to_do_vertex(graph, vertex_index):
        visited_order.append(graph.vertices[vertex_index])
        print('visited vertex: %s' % graph.vertices[vertex_index])

    visited = [False] * g.num_vertices
    visited_order = []

    my_queue = Queue()
    # the distance from start vertex to current vertex
    distance = [0] * graph.num_vertices
    # the previous vertex that come to current vertex
    previous_vertex = [None] * graph.num_vertices

    current_vertex_index = graph.vertices.index(start_v)
    # set the start vertex distance as 0
    distance[current_vertex_index] = 0
    # marked with visited
    visited[current_vertex_index] = True
    # deal with the vertex
    to_do_vertex(graph, current_vertex_index)
    # push stack
    my_queue.enqueue(current_vertex_index)

    while not my_queue.isempty():
        # pop the first element as current vertex
        current_vertex_index = my_queue.dequeue()
        # find all the adjacent vertices
        for i in range(graph.num_vertices):
            if (0 < graph.matrix[current_vertex_index][i] < inf) and not visited[i]:
                # calculate the distance
                distance[i] = distance[current_vertex_index] + 1
                # mark the previous
                previous_vertex[i] = current_vertex_index
                # deal with the vertex
                to_do_vertex(graph, i)
                # mark the vertex
                visited[i] = True
                # check whether come to the end
                if graph.vertices[i] is end_v:
                    print('find the path from %s to %s' % (start_v, end_v))
                    return distance, previous_vertex, visited_order

                # enqueue the element
                my_queue.enqueue(i)

    print('can not find the path from %s to %s' % (start_v, end_v))
    return False


def dijkstra_graph_adjacency_matrix(graph, start_v):
    """
	 1 Dijkstra(G, W, s)　　　　　　//G表示图，W表示权值函数，s表示源顶点
	 2 　　d[s] ←0　　　　　　　　　　//源点到源点最短路为0
	 3 　　for each v ∈ V - {s}　　//3-8行均为初始化操作
	 4 　　　　　do d[v]←∞
	 5 　 　　　　  parent[v]←NIL
	 6 　　S←∅　　　　　　　　
	 7 　　Q←V　　　　　　　　//此处Q为优先队列，存储未进入S的各顶点以及从源点到这些顶点的估算距离，采用二叉堆（最小堆）实现，越小越优先
	 8 　　while Q≠∅
	 9 　　 do u←Extract-Min(Q)　　//提取估算距离最小的顶点，在优先队列中位于顶部，出队列，放入集合S中
	10 　　　  S←S∪{u}
	11 　　　　for each v ∈ Adj(u)　　//松弛操作，对与u相邻的每个顶点v，进行维持三角不等式成立的松弛操作。
	12 　　　　　　do if d[v] > d[u] + w(u, v)
	13 　　　　　　　　then d[v] = d[u] + w(u, v)　　//这一步隐含了更新优先队列中的值，DECREASE。
	14 　　　　　　　　　　  parent[v]←u　　　　　　//置v的前驱结点为u
	:param graph:
	:param start_v:
	:param end_v: 如果不提供 end_v， 则遍历，取得源点到所有节点的最短路径长度
	:return:processed　收录的节点的长度

	"""

    # 1.初始化
    # 未收录的节点
    unprocessed = {}
    # 已收录的节点
    processed = {}
    # 前驱节点 the predecessor vertex that come to current vertex
    predecessor = {}

    # 未收录节点全部初始化为无穷
    for i in range(graph.num_vertices):
        unprocessed[i] = inf
    # 起点
    current_vertex_index = graph.vertices.index(start_v)
    unprocessed[current_vertex_index] = 0  # 这样第一次从未收录节点中取最小值,即可取到起点
    predecessor[current_vertex_index] = None  # 起点无前驱
    current_distance = 0

    # 所有点遍历
    while unprocessed:
        # 2.选择未被收录的节点中的最短路径节点 收录，并作为当前节点
        candidates = []
        for v in unprocessed.items():
            if v[1] < inf:
                candidates.append(v)
        # 如果 candidates 为空，说明所有节点都已经松弛过，或者图不连通，则退出循环
        if len(candidates) == 0:
            break
        # (1) 提取估算距离最小的顶点方法1,使用列表排序,效率相对低，但容易理解
        # 将目前未收录，可以用来松弛的点, 按 距离 进行排序, 取最小值作为当前的节点和距离
        # current_vertex_index, current_distance = sorted(candidates, key=lambda x: x[1])[0]

        # (2) 提取估算距离最小的顶点方法2，使用优先队列（元组）,效率相对高一些
        t = hq.nsmallest(1, candidates, key=lambda x: x[1])
        current_vertex_index, current_distance = t[0]

        processed[current_vertex_index] = current_distance
        unprocessed.pop(current_vertex_index)  # 字典(dict)删除元素, 可以选择两种方式, dict.pop(key)和del dict[key].

        # 3.前的节点，更新所有邻居的距离
        # 遍历所有邻居
        for v_index in range(graph.num_vertices):
            # 未被收录的邻居
            if v_index in unprocessed:
                new_distance = processed[current_vertex_index] + graph.matrix[current_vertex_index][v_index]
                # 如果新路径更短
                if new_distance < unprocessed[v_index]:
                    # 更新距离
                    unprocessed[v_index] = new_distance
                    # 更新前驱
                    predecessor[v_index] = current_vertex_index

    return processed, predecessor


def bellman_ford_graph_adjacency_matrix(graph, start_v):
    """
	与 dijkstra 算法的区别是这里采用对边进行遍历比较
	Ford算法的每次迭代遍历所有边, 并对边进行松弛(relax)操作. 对边e进行松弛是指: 若从源点通过e.start到达e.stop的路径长小于
	已知最短路径, 则更新已知最短路径.
	若路径中不存在负环, 则进行n-1次迭代后不存在可以进行松弛的边. 因此再遍历一次边, 若存在可松弛的边说明图中存在负环.
	:param graph:
	:param start_v:
	:param end_v: 如果不提供 end_v， 则遍历，取得源点到所有节点的最短路径长度
	:return:processed　收录的节点的长度

	"""

    # 1.初始化
    num_vertex = graph.num_vertices
    edges = graph.edges_array

    # 与源点的距离
    distance = [inf] * num_vertex
    # 前驱节点 the predecessor vertex that come to current vertex
    predecessor = [0] * num_vertex

    current_vertex_index = graph.vertices.index(start_v)
    distance[current_vertex_index] = 0  # 这样第一次从未收录节点中取最小值,即可取到起点
    # predecessor[current_vertex_index] = None  # 起点无前驱

    # 所有点遍历
    for i in range(num_vertex):
        for edge in edges:
            tail_index = graph.vertices.index(edge[0])
            head_index = graph.vertices.index(edge[1])
            # print ('head index: %d' % head_index)
            edge_cost = edge[2]
            new_distance = distance[tail_index] + edge_cost

            # 在某边中，如果 tail 的距离 加上 该边的距离，小于 head 的距离
            if new_distance < distance[head_index]:
                # 将当前边的　head 的距离更新为新的距离　
                distance[head_index] = new_distance
                # 记录 head 的前躯为当前边的 tail
                predecessor[head_index] = edge[0]

    # 再次遍历检查是否存在负环　check negative loop
    flag = False
    for edge in edges:
        tail_index = graph.vertices.index(edge[0])
        head_index = graph.vertices.index(edge[1])
        edge_cost = edge[2]
        new_distance = distance[tail_index] + edge_cost

        # 在某边中，如果 tail 的距离 加上 该边的距离，小于 head 的距离
        if new_distance < distance[head_index]:
            # 存在负环,退出
            flag = True
            break
    if flag:  # 如果存在负环，返回错误，各距离值无效
        return False
    return distance, predecessor


def floyd_warshall_graph_adjacency_matrix(graph):
    def make_mat(m, n, fill=None):
        mat = []
        for i in range(m):
            mat.append([fill] * n)
        return mat

    length = graph.num_vertices

    # 距离矩阵， 用用来记录每个点作为起点时，到每个点的距离 行下标即起点，列即为起点到该列所在点的距离
    distance = make_mat(length, length, fill=inf)
    predecessor = make_mat(length, length, fill=None)

    for i in range(length):
        for j in range(length):
            # 保i到顶点j的已知最短路径, 初始化为直接连接
            distance[i][j] = graph.matrix[i][j]
            # 保存从顶点i到顶点j的已知最短路径上下一个顶点, 初始化为j
            predecessor[i][j] = j

    for k in range(length):
        for i in range(length):
            for j in range(length):
                # 如果 i，j 通过 k 连接的距离小于 i,j 直接连接，则更新距离
                if distance[i][k] + distance[k][j] < distance[i][j]:
                    distance[i][j] = distance[i][k] + distance[k][j]
                    # 更新前驱为 中介 k
                    predecessor[i][j] = predecessor[i][k]

    return distance, predecessor


def test_shortest_path_unweighted_graph_adjacency_matrix(g, start_v, end_v):
    # shortest path for graph adjacency matrix
    print('-' * 100)
    print('traverse graph')
    print('-' * 100)
    dist, predecessor, visited = shortest_path_unweighted_graph_adjacency_matrix(g, start_v, end_v)
    print('the distance from %s to %s is %s: ' % (start_v, end_v, dist[g.vertices.index(end_v)]))

    _v = g.vertices.index(end_v)
    print(g.vertices[_v])
    while not predecessor[_v] is None:
        # if pre_v[_v]:
        v = predecessor[_v]
        print(g.vertices[v])
        _v = v


def test_dijkstra_graph_adjacency_matrix(g, start_v):
    print('-' * 100)
    print('dijkstra_graph_adjacency_matrix')
    print('-' * 100)

    distance, predecessor = dijkstra_graph_adjacency_matrix(g, start_v)
    print(distance)

    for end_v in g.vertices:
        print('distance and path for %s ---------------------------------------------' % end_v)
        show_path(g, predecessor, distance, g.vertices.index(end_v))


def test_bellman_ford_graph_adjacency_matrix(g, start_v):
    print('-' * 100)
    print('bellman_ford_graph_adjacency_matrix')
    print('-' * 100)

    t = bellman_ford_graph_adjacency_matrix(g, start_v)
    # 如果没有负环
    if t:
        distance, predecessor = t
        print(distance)

        _v = g.vertices.index(end_v)
        print('%s index: %s  distance: %s' % (g.vertices[_v], _v, distance[_v]))

    else:
        print('there is a negative cycle')


def test_floyd_graph_adjacency_matrix(g):
    print('-' * 100)
    print('floyd_graph_adjacency_matrix')
    print('-' * 100)
    distance, predecessor = floyd_warshall_graph_adjacency_matrix(g)

    print(distance)
    print(predecessor)


def show_path(graph, predecessor, distance, end_vertice_index):
    if predecessor[end_vertice_index]:
        v = predecessor[end_vertice_index]
        show_path(graph, predecessor, distance, v)
        print('%s index: %s  distance: %s' % (
        g.vertices[end_vertice_index], end_vertice_index, distance[end_vertice_index]))
    else:
        # print(g.vertices[end_vertice_index])
        print('%s index: %s  distance: %s' % (
        g.vertices[end_vertice_index], end_vertice_index, distance[end_vertice_index]))


def load_from_txt():
    vertices_txt = 'vertices.txt'
    matrix_txt = 'matrix.txt'
    nodes = np.loadtxt(vertices_txt, dtype=bytes).astype(str)
    print(nodes)
    matrix = np.loadtxt(matrix_txt, dtype=bytes, delimiter=',').astype(float)
    print(matrix)
    my_graph = GraphMatrix(nodes, matrix)
    print(my_graph)
    return my_graph


if __name__ == '__main__':
    _graph = GraphMatrix()
    g = load_from_txt()

    # g.draw_directed_graph()

    start_v = 'A'
    end_v = 'G'

    inf = float('inf')

    # 1.测试无权重最短路径
    # test_shortest_path_unweighted_graph_adjacency_matrix(g, start_v, end_v)

    # 2.测试有权重最短路径 Dijkstra
    start_v = 'v0'
    # end_v = 'v45'
    test_dijkstra_graph_adjacency_matrix(g, start_v)

    # test_floyd_graph_adjacency_matrix(g)

# 3.测试存在负边 bellman-ford
# g = create_directed_matrix_with_negative_edge(_graph)
# # g.draw_directed_graph()
# test_bellman_ford_graph_adjacency_matrix(g, start_v)
