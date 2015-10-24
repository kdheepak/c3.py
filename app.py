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
        # Get repo_path from the text field
        repo_path = request.form['text']
        # pass repo_path as a variable to index.html
        return render_template("index.html", repo_path=repo_path)
    else:
        return render_template("index.html")

@app.route("/data")
def data():
    try:
        repo_path = request.args.get('repo_path', '')
    except:
        repo_path = '../c3.py/'
        
    # create a git repo
    repo = git.Repo(repo_path)

    # create a networkx graph
    networkx_graph = nx.DiGraph()

    # find the head commit
    commit = repo.head.commit

    # find diff between staged and index
    diff = commit.diff(create_patch=True)   
    # find diff between working dir and index
    workingdiff = commit.diff(None, create_patch=True)     
    
    # add all the commits before `commit` to the networkx_graph till we have reached 200 spots.
    # add using breath_first_search
    breadth_first_add(networkx_graph, commit, 200)

    # create a graphviz vertical layout
    position=nx.graphviz_layout(networkx_graph, prog='dot')

    # Add the diff to the networkx graph without linking them to the graph
    add_diff_to(networkx_graph, position, workingdiff, diff)
    
    # Convert to data
    data = json_graph.node_link_data(networkx_graph)

    # Add all branch labels to the data
    store_branch_labels(data, position, repo)

    # return a json dump of data to /data
    j = json.dumps(data)
    return(j)

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


def add_diff_to(networkx_graph, position, workingdiff=[], diff=[]):
    """
    Add the diff nodes to the tree

    workingdiff contains list of diff objects of all tracked files
    diff contains list of diff objects of all staged files
    """
    maximumX, maximumY = find_max_xy(position)

    # e.g. workingdiff = [git.Diff.diff, git.Diff.diff] 
    # where git.Diff.diff is the diff object for a particular file
    # len(workingdiff) is number of files that have been changed
    # store diff.blob.hexsha as id
    for i in range(0, len(workingdiff)):
        d = workingdiff[i]
        key = d.b_blob.hexsha
        networkx_graph.add_node(key, message=d.b_blob.path, color='pink')
        position[key] = [100,maximumY+(i)*25+100]
        
    for i in range(0, len(diff)):
        d = diff[i]
        key = d.b_blob.hexsha
        networkx_graph.add_node(key, message=d.b_blob.path, color='blue')
        position[key] = [100,maximumY+(i)*25+100]

def find_max_xy(position):
    tempx = 0
    tempy = 0
    for node in position:
        tempx = max(position[node][0], tempx)
        tempy = max(position[node][1], tempy)
    return tempx, tempy

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

def is_diff_name(node, repo):
    # Check all commits if commit.hexsha == node
    for commit in repo.iter_commits():
        if commit.hexsha == node:
            return True
    return False

def store_branch_labels(data, position, repo):
    data['labels'] = []

    # search all the nodes if they are either "HEAD" or branch names
    working_bool = False
    staged_bool = False

    for node in data['nodes']:

        # store labels for staged and working nodes
        if not is_diff_name(node['id'], repo):
            if node['color'] == 'pink':
                data['working'] = node['id']
                working_bool = True
            if node['color'] == 'blue':
                staged_bool = True
                data['staged'] = node['id']

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

    if staged_bool: 
        data['labels'].append('staged')
    if working_bool: 
        data['labels'].append('working')

if __name__ == "__main__":
    import os

    port = 5000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    app.config['DEBUG'] = True
    app.debug = True
    app.run(port=port)

