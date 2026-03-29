#!/usr/bin/env python3
"""Gossip protocol simulation for peer-to-peer information dissemination."""
import sys, random

class GossipNode:
    def __init__(self, node_id):
        self.id, self.data, self.version = node_id, {}, {}
        self.peers, self.messages_sent = [], 0
    def update(self, key, value):
        self.version[key] = self.version.get(key, 0) + 1
        self.data[key] = value
    def gossip_round(self, fanout=2):
        targets = random.sample(self.peers, min(fanout, len(self.peers)))
        for t in targets:
            for k, v in self.data.items():
                ver = self.version[k]
                if k not in t.version or t.version[k] < ver:
                    t.data[k] = v; t.version[k] = ver
                    self.messages_sent += 1
    def merge(self, other_data, other_versions):
        for k, v in other_data.items():
            over = other_versions.get(k, 0)
            if k not in self.version or self.version[k] < over:
                self.data[k] = v; self.version[k] = over

def simulate(n_nodes, n_rounds, fanout=2):
    nodes = [GossipNode(i) for i in range(n_nodes)]
    for n in nodes: n.peers = [x for x in nodes if x is not n]
    nodes[0].update("key1", "hello")
    for _ in range(n_rounds):
        for n in nodes: n.gossip_round(fanout)
    return nodes

def main():
    if len(sys.argv) < 2: print("Usage: gossip_proto.py <demo|test>"); return
    if sys.argv[1] == "test":
        nodes = simulate(10, 5, fanout=3)
        spread = sum(1 for n in nodes if "key1" in n.data)
        assert spread == 10, f"Only {spread}/10 got the data"
        assert all(n.data.get("key1") == "hello" for n in nodes)
        # Version conflict resolution
        n0, n1 = GossipNode(0), GossipNode(1)
        n0.update("x", "v1"); n1.merge(n0.data, n0.version)
        assert n1.data["x"] == "v1"
        n0.update("x", "v2"); n1.merge(n0.data, n0.version)
        assert n1.data["x"] == "v2"
        print("All tests passed!")
    else:
        nodes = simulate(20, 10)
        spread = sum(1 for n in nodes if "key1" in n.data)
        print(f"After 10 rounds: {spread}/20 nodes have the data")
        total_msgs = sum(n.messages_sent for n in nodes)
        print(f"Total messages: {total_msgs}")

if __name__ == "__main__": main()
