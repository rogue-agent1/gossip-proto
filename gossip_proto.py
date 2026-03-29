#!/usr/bin/env python3
"""gossip_proto - Gossip protocol simulation for membership and state dissemination."""
import sys, random, time

class Member:
    ALIVE, SUSPECT, DEAD = "alive", "suspect", "dead"
    
    def __init__(self, node_id):
        self.id = node_id
        self.state = self.ALIVE
        self.heartbeat = 0
        self.timestamp = time.time()

class GossipNode:
    def __init__(self, node_id, fanout=2):
        self.id = node_id
        self.members = {node_id: Member(node_id)}
        self.fanout = fanout
        self.data = {}  # key -> (value, version)
        self.round = 0
    
    def join(self, seed_state):
        """Join cluster using seed node's state."""
        for mid, m in seed_state.items():
            if mid not in self.members:
                self.members[mid] = Member(mid)
                self.members[mid].heartbeat = m.heartbeat
    
    def heartbeat(self):
        self.members[self.id].heartbeat += 1
        self.members[self.id].timestamp = time.time()
        self.round += 1
    
    def select_targets(self):
        peers = [m for m in self.members if m != self.id and self.members[m].state != Member.DEAD]
        return random.sample(peers, min(self.fanout, len(peers)))
    
    def prepare_digest(self):
        return {mid: {"heartbeat": m.heartbeat, "state": m.state, "data": dict(self.data)}
                for mid, m in self.members.items()}
    
    def merge_digest(self, digest):
        updates = 0
        for mid, info in digest.items():
            if mid not in self.members:
                self.members[mid] = Member(mid)
                updates += 1
            m = self.members[mid]
            if info["heartbeat"] > m.heartbeat:
                m.heartbeat = info["heartbeat"]
                m.state = info["state"]
                m.timestamp = time.time()
                updates += 1
            # Merge data
            for k, (v, ver) in info.get("data", {}).items():
                if k not in self.data or ver > self.data[k][1]:
                    self.data[k] = (v, ver)
                    updates += 1
        return updates
    
    def set_data(self, key, value):
        ver = self.data.get(key, (None, 0))[1] + 1
        self.data[key] = (value, ver)
    
    def detect_failures(self, timeout=5):
        now = time.time()
        for mid, m in self.members.items():
            if mid == self.id:
                continue
            if m.state == Member.ALIVE and now - m.timestamp > timeout:
                m.state = Member.SUSPECT
            elif m.state == Member.SUSPECT and now - m.timestamp > timeout * 2:
                m.state = Member.DEAD
    
    def alive_members(self):
        return [m for m in self.members.values() if m.state == Member.ALIVE]

def simulate_gossip(n_nodes=5, rounds=10, seed=42):
    random.seed(seed)
    nodes = {i: GossipNode(i) for i in range(n_nodes)}
    
    # All nodes know about node 0
    for i in range(1, n_nodes):
        nodes[i].join(nodes[0].members)
    
    # Node 0 sets some data
    nodes[0].set_data("config", "v1")
    
    convergence = []
    for r in range(rounds):
        for nid, node in nodes.items():
            node.heartbeat()
            targets = node.select_targets()
            digest = node.prepare_digest()
            for tid in targets:
                nodes[tid].merge_digest(digest)
        
        # Check convergence
        with_data = sum(1 for n in nodes.values() if "config" in n.data)
        convergence.append(with_data)
    
    return convergence

def test():
    # Basic gossip
    n1 = GossipNode(0)
    n2 = GossipNode(1)
    n3 = GossipNode(2)
    
    n2.join(n1.members)
    n3.join(n1.members)
    n1.join(n2.members)
    n1.join(n3.members)
    
    assert len(n1.members) == 3
    assert len(n2.members) >= 2
    
    # Data dissemination
    n1.set_data("key", "value")
    digest = n1.prepare_digest()
    n2.merge_digest(digest)
    assert n2.data.get("key") == ("value", 1)
    
    # Heartbeat
    n1.heartbeat()
    assert n1.members[0].heartbeat == 1
    
    # Simulation
    conv = simulate_gossip(5, 10)
    assert conv[-1] == 5  # All nodes have the data
    assert conv[0] < 5    # Not all have it in round 1
    
    print(f"Convergence: {conv}")
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: gossip_proto.py test")
