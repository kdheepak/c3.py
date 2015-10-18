"""
git log live
"""

from flask import Flask
from flask import render_template
from flask import render_template_string
from flask import request

from networkx.readwrite import json_graph
import networkx as nx

import git
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def form_post():
    if request.method == 'POST':
        repo_path = request.form['text']
        return render_template("index.html", repo_path=repo_path)
    else:
        return render_template("index.html")

def branch_name(node, repo):
    for b in repo.branches:
        if b.commit.hexsha == node:
            return b.name
    return None

def head_name(node, repo):
    if node == repo.head.commit.hexsha:
        return "HEAD"
    else:
        return None


def breadth_first_add(networkx_graph, commit, N):
    """
    Traverse a graph breadth first and add commits on the way

    N is number of commmits you want to traverse
    """
    # add the commit to a queue
    queue = []
    queue.append(commit)

    # add the commit to the graph
    networkx_graph.add_node(commit.hexsha, message=commit.message.split("\n")[0])

    while len(networkx_graph.nodes()) < N:

        # if queue is empty -> break
        if len(queue)==0:
            break

        # get the commit in the queue and add all its parents to the graph and to the queue
        commit = queue.pop()
        for c in commit.parents:
            networkx_graph.add_edge(commit.hexsha, c.hexsha)
            networkx_graph.add_node(c.hexsha, message=c.message.split("\n")[0])
            queue.append(c)

@app.route("/data")
def data():
    try:
        repo_path = request.args.get('repo_path', '')
    except:
        repo_path = '../c3.py/'
        
    repo = git.Repo(repo_path)

    networkx_graph = nx.DiGraph()

    commit = repo.head.commit

    diff = commit.diff(create_patch=True)   
    workingdiff = commit.diff(None, create_patch=True)     
    
    breadth_first_add(networkx_graph, commit, 200)

    position=nx.graphviz_layout(networkx_graph, prog='dot')

    add_diff_to(networkx_graph, position, workingdiff, diff)
    
    data = json_graph.node_link_data(networkx_graph)

    store_branch_labels(data, position, repo)


    # store_diff_in(data, diff, workingdiff)

    j = json.dumps(data)
    return(j)

def add_diff_to(networkx_graph, position, workingdiff=[], diff=[]):
    
    maximumX, maximumY = find_max_xy(position)

    for i in range(0, len(workingdiff)):
        d = workingdiff[i]
        networkx_graph.add_node(d.b_path, message=len(d.diff), color='pink')
        position[d.b_path] = [200,maximumY+(i)*25+100]
        
    for i in range(0, len(diff)):
        d = diff[i]
        networkx_graph.add_node(d.b_path, message=len(d.diff), color='blue')
        position[d.b_path] = [200+300,maximumY+(i)*25+100]

def find_max_xy(position):
    tempx = 0
    tempy = 0
    for node in position:
        tempx = max(position[node][0], tempx)
        tempy = max(position[node][1], tempy)
    return tempx, tempy

def store_branch_labels(data, position, repo):
    data['labels'] = []

    # search all the nodes if they are either "HEAD" or branch names
    for node in data['nodes']:
        if branch_name(node['id'], repo):

            # e.g. data["master"] = 8e007c2a86789b88ffe5ce350746750bf78bfdfb
            data[branch_name(node['id'], repo)] = node['id']

            # e.g. data['labels'] = ['HEAD', 'master']
            data['labels'].append(branch_name(node['id'], repo))

        if head_name(node['id'], repo):

            # e.g. data["HEAD"] = 8e007c2a86789b88ffe5ce350746750bf78bfdfb
            data[head_name(node['id'], repo)] = node['id']

        # store the position of every node
        node['pos'] = position[node['id']]

if __name__ == "__main__":
    import os

    port = 5000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    app.config['DEBUG'] = True
    app.debug = True
    app.run(port=port)

