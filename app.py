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
    tree = nx.DiGraph()

    parent = None

    g = git.Git(repo_path) 
    repo = git.Repo(repo_path)

    loginfo = g.log()

    def get_hash(commit):
        return commit.split("\n")[0]

    commits = loginfo.split("\n\ncommit ")
    commits[0] = commits[0].replace("commit ", '')

    for item in commits[:15]:
        node = "{}".format(get_hash(item))
        tree.add_node(node)
        commit = repo.commit(get_hash(item))
        for parent in commit.parents:
            tree.add_edge(node, parent.hexsha)

    G = tree

    # same layout using matplotlib with no labels
    pos=nx.graphviz_layout(G, prog='dot')
    #nx.draw(G, pos, with_labels=False, arrows=False)

    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(tree)

    tree_data=[]
    for key in pos:
        tree_data.append({'id': key,
                  'pos': pos[key]})

    data = {'tree': tree_data, 'node_link_data': data}
    j = json.dumps(data)

    return(j)

if __name__ == "__main__":
    app.run()
