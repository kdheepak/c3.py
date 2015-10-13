from flask import Flask
from flask import render_template
app = Flask(__name__)
app.config['DEBUG'] = True

repo_path = '../ames-py'

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/data")
def data():
    import json
    import git

    import networkx as nx
    G = nx.DiGraph()

    parent = None

    g = git.Git(repo_path) 
    repo = git.Repo(repo_path)

    loginfo = g.log()

    def get_hash(commit):
        return commit.split("\n")[0]

    commits = loginfo.split("\n\ncommit ")
    commits[0] = commits[0].replace("commit ", '')

    for item in commits[:20]:
        node = "{}".format(get_hash(item))
        commit = repo.commit(get_hash(item))
        G.add_node(node, message=commit.message.split("\n")[0])
        for parent in commit.parents:
            G.add_node(parent.hexsha, message=parent.message.split("\n")[0])
            G.add_edge(node, parent.hexsha)

    pos=nx.graphviz_layout(G, prog='dot')

    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)
    
    for node in data['nodes']:
        node['pos'] = pos[node['id']]

    j = json.dumps(data)
    return(j)

if __name__ == "__main__":
    app.run()
