#!/usr/bin/env python3
"""Gossip protocol simulation for peer-to-peer information spread."""
import sys, random

class GossipNode:
    def __init__(self, nid):
        self.nid = nid
        self.data = {}
        self.peers = []
        self.version = {}
    def add_peer(self, peer):
        if peer not in self.peers:
            self.peers.append(peer)
    def update(self, key, value):
        ver = self.version.get(key, 0) + 1
        self.data[key] = value
        self.version[key] = ver
    def gossip(self):
        if not self.peers: return 0
        target = random.choice(self.peers)
        updated = 0
        for key in self.data:
            my_ver = self.version.get(key, 0)
            their_ver = target.version.get(key, 0)
            if my_ver > their_ver:
                target.data[key] = self.data[key]
                target.version[key] = my_ver
                updated += 1
        return updated

def simulate(n_nodes, rounds, seed=None):
    if seed: random.seed(seed)
    nodes = [GossipNode(i) for i in range(n_nodes)]
    for n in nodes:
        peers = [p for p in nodes if p.nid != n.nid]
        random.shuffle(peers)
        for p in peers[:3]:
            n.add_peer(p)
    nodes[0].update("msg", "hello world")
    for _ in range(rounds):
        for n in nodes:
            n.gossip()
    return nodes

def test():
    nodes = simulate(10, 20, seed=42)
    spread = sum(1 for n in nodes if n.data.get("msg") == "hello world")
    assert spread >= 8, f"Only {spread}/10 nodes got the message"
    n = GossipNode(0)
    n.update("x", 1)
    assert n.data["x"] == 1 and n.version["x"] == 1
    n.update("x", 2)
    assert n.version["x"] == 2
    print("  gossip_proto: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Gossip protocol simulation")
