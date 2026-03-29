#!/usr/bin/env python3
"""gossip_proto - Gossip protocol simulation for distributed state propagation."""
import sys, random

class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.state = {}
        self.peers = []
        self.version = {}
    def update(self, key, value):
        self.version[key] = self.version.get(key, 0) + 1
        self.state[key] = (value, self.version[key], self.id)
    def gossip_digest(self):
        return {k: (v[1], v[2]) for k, v in self.state.items()}
    def receive_gossip(self, digest, sender):
        updates_needed = []
        for key, (ver, origin) in digest.items():
            my = self.state.get(key)
            if my is None or my[1] < ver:
                updates_needed.append(key)
        return updates_needed
    def apply_updates(self, updates):
        for key, (value, version, origin) in updates.items():
            my = self.state.get(key)
            if my is None or my[1] < version:
                self.state[key] = (value, version, origin)
                self.version[key] = version

def simulate(nodes, rounds=10, fanout=2, seed=None):
    if seed is not None:
        random.seed(seed)
    for _ in range(rounds):
        for node in nodes:
            targets = random.sample([n for n in nodes if n.id != node.id], min(fanout, len(nodes)-1))
            for target in targets:
                digest = node.gossip_digest()
                needed = target.receive_gossip(digest, node)
                if needed:
                    updates = {k: node.state[k] for k in needed if k in node.state}
                    target.apply_updates(updates)

def test():
    nodes = [Node(f"n{i}") for i in range(5)]
    nodes[0].update("x", 42)
    nodes[2].update("y", "hello")
    simulate(nodes, rounds=10, seed=42)
    # all nodes should have both values
    for n in nodes:
        assert n.state.get("x", (None,))[0] == 42, f"{n.id} missing x"
        assert n.state.get("y", (None,))[0] == "hello", f"{n.id} missing y"
    # update propagation
    nodes[4].update("x", 100)
    simulate(nodes, rounds=10, seed=42)
    for n in nodes:
        assert n.state["x"][0] == 100
    print("OK: gossip_proto")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: gossip_proto.py test")
