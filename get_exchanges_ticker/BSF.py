# -*- coding: utf-8 -*-
# @Time    : 2019-10-17 16:55
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : BSF.py
# @Software: PyCharm

from ClassGraphMatrix import GraphMatrix
from queue import Queue
import numpy as np


def BFS(graph:GraphMatrix, start):
    # queue本质上是堆栈，用来存放需要进行遍历的数据
    # order里面存放的是具体的访问路径
    queue = Queue()
    visited = [False]*graph.num_vertices
    order = []
    # 首先将初始遍历的节点放到queue中，表示将要从这个点开始遍历
    # 由于是广度优先，也就是先访问初始节点的所有的子节点，所以可以
    queue.put(start)
    order.append(start)
    visited[start] = True
    while queue:
        # queue.pop(0)意味着是队列的方式出元素，就是先进先出，而下面的for循环将节点v的所有子节点
        # 放到queue中，所以queue.pop(0)就实现了每次访问都是先将元素的子节点访问完毕，而不是优先叶子节点
        v = queue.pop(0)
        for w in self.sequense[v]:
            if w not in order:
                # 这里可以直接order.append(w) 因为广度优先就是先访问节点的所有下级子节点，所以可以
                # 将self.sequense[v]的值直接全部先给到order
                order.append(w)
                queue.append(w)
    return order


# ————————————————
# 版权声明：本文为CSDN博主「changyuanchn」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/changyuanchn/article/details/79008760

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

def main():
    pass


if __name__ == '__main__':
    pass
