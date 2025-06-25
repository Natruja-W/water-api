from flask import Flask, request, jsonify
import networkx as nx
import os

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    households = data.get("households", [])
    available_liters = data.get("available_liters", 0)

    # ตรวจสอบน้ำ
    total_requested = sum(h.get("liters", 0) for h in households)

    allocations = []
    if total_requested <= available_liters:
        for h in households:
            allocations.append({
                "name": h["name"],
                "requested": h["liters"],
                "allocated": h["liters"]
            })
    else:
        weights = [h["people"] * 2 for h in households]
        weight_sum = sum(weights) or 1
        for h, w in zip(households, weights):
            allocations.append({
                "name": h["name"],
                "requested": h["liters"],
                "allocated": round(w / weight_sum * available_liters, 2)
            })

    # สร้าง MST
    graph = nx.Graph()
    for h in households:
        graph.add_node(h["name"], pos=tuple(h["location"]))
    for i in range(len(households)):
        for j in range(i + 1, len(households)):
            h1, h2 = households[i], households[j]
            dx = h1["location"][0] - h2["location"][0]
            dy = h1["location"][1] - h2["location"][1]
            dist = (dx**2 + dy**2)**0.5
            graph.add_edge(h1["name"], h2["name"], weight=dist)
    mst = nx.minimum_spanning_tree(graph)
    mst_plan = [{"from": u, "to": v, "distance": round(d["weight"], 2)}
                for u, v, d in mst.edges(data=True)]

    return jsonify({
        "allocations": allocations,
        "mst_plan": mst_plan
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
