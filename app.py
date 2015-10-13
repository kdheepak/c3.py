from flask import Flask
from flask import render_template
from flask import render_template_string
from flask import request

app = Flask(__name__)
app.config['DEBUG'] = True

repo_path = ''

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def my_form_post():
    global repo_path
    if request.method == 'POST':
        repo_path = request.form['text']
        return render_template("index.html")
    else:
        return render_template_string("""
    <form action="." method="POST">
        <input type="text" name="text">
        <input type="submit" name="my-form" value="Send">
    </form>
                """)

def branch_name(node, repo):
    for b in repo.branches:
        if b.commit.hexsha == node:
            return b.name
        else:
            pass
    return False

def head_name(node, repo):
    if node == repo.active_branch.commit.hexsha:
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
    import json
    import git

    import networkx as nx
    G = nx.DiGraph()

    repo = git.Repo(repo_path)


    commit = repo.active_branch.commit

    breadth_first_add(G, commit, 10)

    nx.write_dot(G,'test.dot')
    pos=nx.graphviz_layout(G, prog='dot')

    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)

    data['labels'] = []

    for node in data['nodes']:
        if branch_name(node['id'], repo):
            data[branch_name(node['id'], repo)] = pos[node['id']]
            data['labels'].append(branch_name(node['id'], repo))
        if head_name(node['id'], repo):
            data[head_name(node['id'], repo)] = pos[node['id']]
            data['labels'].append(head_name(node['id'], repo))

        node['pos'] = pos[node['id']]

    j = json.dumps(data)
    return(j)

if __name__ == "__main__":
    import os

    port = 5000

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run(port=port)
