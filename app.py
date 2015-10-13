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
    import os

    port = 5000

    # Open a web browser pointing at the app.
    os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run(port=port)
