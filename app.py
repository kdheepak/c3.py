from flask import Flask
from flask import render_template
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/data")
def data():
    import json
    import git

    import networkx as nx
    tree = nx.DiGraph()

    parent = None

    g = git.Git(repo_path) 
    repo = git.Repo(repo_path)

    loginfo = g.log()

    def get_hash(commit):
        return commit.split("\n")[0]

    commits = loginfo.split("\n\ncommit ")
    commits[0] = commits[0].replace("commit ", '')

    for item in commits[:5]:
        node = "{}".format(get_hash(item))
        tree.add_node(node)
        commit = repo.commit(get_hash(item))
        for parent in commit.parents:
            tree.add_edge(node, parent.hexsha)

    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(tree)
    j = json.dumps(data)
    return(j)

if __name__ == "__main__":
    app.run()
