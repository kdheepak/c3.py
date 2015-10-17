from flask import Flask
from flask import render_template
from flask import render_template_string
from flask import request

import git
import json

app = Flask(__name__)

repo_path = '.'
import networkx as nx
G = nx.DiGraph()

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def my_form_post():
    if request.method == 'POST':
        repo_path = request.form['text']
        return render_template("index.html", repo_path=repo_path)
    else:
        return render_template("index.html")

def branch_name(node, repo):
    for b in repo.branches:
        if b.commit.hexsha == node:
            return b.name
        else:
            pass
    return False

def head_name(node, repo):
    if node == repo.head.commit.hexsha:
        return "HEAD"


def breadth_first_add(G, commit, N):
    queue = []
    queue.append(commit)
    G.add_node(commit.hexsha, message=commit.message.split("\n")[0])

    while len(G.nodes()) < N:
        if len(queue)==0:
            break
        commit = queue.pop()
        for c in commit.parents:
            G.add_edge(commit.hexsha, c.hexsha)
            G.add_node(c.hexsha, message=c.message.split("\n")[0])
            queue.append(c)

@app.route("/data")
def data():
    repo_path = request.args.get('repo_path', '')

    repo = git.Repo(repo_path)

    G = nx.DiGraph()

    commit = repo.head.commit

    diff = commit.diff(create_patch=True)   
    workingdiff = commit.diff(None, create_patch=True)     
    
    breadth_first_add(G, commit, 200)

    pos=nx.graphviz_layout(G, prog='dot')

    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)

    data['labels'] = []

    for node in data['nodes']:
        if branch_name(node['id'], repo):
            data[branch_name(node['id'], repo)] = node['id']
            data['labels'].append(branch_name(node['id'], repo))
        if head_name(node['id'], repo):
            data[head_name(node['id'], repo)] = node['id']
            #data['labels'].append(head_name(node['id'], repo))

        node['pos'] = pos[node['id']]

    try:
        data['diff'] = diff[0].diff
    except:
        data['diff'] = ''

    try:
        data['wdiff'] = workingdiff[0].diff
    except:
        data['wdiff'] = ''
        
    if data['diff'] != data['wdiff']:
        data['wdiff'] = workingdiff[0].diff
    else:
        data['wdiff'] = ''
        
    j = json.dumps(data)
    return(j)

if __name__ == "__main__":
    import os

    port = 5000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.config['DEBUG'] = True
    app.debug = True
    app.run(port=port)
