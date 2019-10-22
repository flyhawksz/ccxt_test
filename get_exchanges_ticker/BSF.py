# -*- coding: utf-8 -*-
# @Time    : 2019-10-17 16:55
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : BSF.py
# @Software: PyCharm

from ClassGraphMatrix import GraphMatrix
from queue import Queue
import numpy as np


def BFS(graph:GraphMatrix, start, value):
    """
    广度遍历
    每次访问邻居，更新value, 如果更大，则邻居的value 放新的值
    :param graph: 图
    :param start: 开始的序号
    :param value: 开始的金额
    :return:
    """
    #初始化
    # queue本质上是堆栈，用来存放需要进行遍历的数据
    # order里面存放的是具体的访问路径
    inf = float('inf')
    queue = Queue()
    visited = [False]*graph.num_vertices
    pre_node = [None]*graph.num_vertices
    currency_value = dict()
    currency_value[start] = value

    for v in range(graph.num_vertices):
        currency_value[v] = -inf

    # 首先将初始遍历的节点放到queue中，表示将要从这个点开始遍历
    # 由于是广度优先，也就是先访问初始节点的所有的子节点，所以可以
    currency_value[start] = value
    queue.put(start)
    visited[start] = True

    queue.put(start)
    while not queue.empty():
        # 队列的方式出元素，就是先进先出，而下面的for循环将节点v的所有子节点
        # 放到queue中，所以queue.pop(0)就实现了每次访问都是先将元素的子节点访问完毕，而不是优先叶子节点
        current_node = queue.get()
        current_value = currency_value[current_node]
        print(graph.vertices[current_node])
        for node in graph.vertex_neighbors_index[current_node]:
            node_value = currency_value[node]
            # 如果可以兑换
            if graph.matrix[current_node][node] > 0:
                # 兑换后的值
                new_value = current_value * graph.matrix[current_node][node]
                # 如果兑换后的值比原有的值大，更新值，并设下一个节点为未访问，可以重新按新值测算
                if new_value > node_value:
                    currency_value[node] = new_value
                    # 避免出现负环情况（在此处是正环）
                    # if node != start:
                    #     visited[node] = False
                    # 更新前序为当前节点
                    pre_node[node] = current_node
                    if node == start:
                        return currency_value, pre_node
                # 将需访问节点加入队列
                if not visited[node]:
                    print('下一个后续是： {}'.format(graph.vertices[node]))
                    visited[node] = True
                    queue.put(node)
                    print('前序是： {}'.format(graph.vertices[current_node]))
    print('遍历完毕')
    return currency_value, pre_node


def load_from_txt():
    vertices_txt = 'vertices.txt'
    matrix_txt = 'matrix.txt'
    nodes = np.loadtxt(vertices_txt, dtype=bytes).astype(str)
    # print(nodes)
    matrix = np.loadtxt(matrix_txt, dtype=bytes, delimiter=',').astype(float)
    # print(matrix)
    my_graph = GraphMatrix(list(nodes), list(matrix))
    # print(my_graph)
    return my_graph


if __name__ == '__main__':
    g = load_from_txt()
    currency_value, pre_node = BFS(g, 0, 1000)
    print('*'*30)
    print(currency_value)
    print('-'*30)
    print(pre_node)
