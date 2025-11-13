import copy
from collections import deque

class B21CS062:
    def __init__(self, initial_state):
        self.known_nodes = set()
        self.adj = {}
        self.available_colors = list(initial_state["available_colors"])
        self.assignments = {}
        self.domains = {}
        self.current_node = initial_state["current_node"]
        self._ingest_observation(initial_state)
    
    def get_next_move(self, visible_state):
        self._ingest_observation(visible_state)
        current = visible_state["current_node"]
        self.current_node = current

        if self.assignments.get(current) is None:
            return {"action": "move", "node": current}
        visible_nodes = set(visible_state["visible_graph"]["nodes"])
        candidates = [n for n in visible_nodes if self.assignments.get(n) is None]

        if not candidates:
            best_node = current
            best_score = (-1, -1, -1)
            for n in visible_nodes:
                if n == current and len(visible_nodes) > 1:
                    continue

                unseen_neighbors = sum(1 for nb in self.adj.get(n, []) if nb not in self.known_nodes)
                boundary_conflicts = sum(1 for nb in self.adj.get(n, []) if self.assignments.get(nb) is not None)
                degree = len(self.adj.get(n, []))
                score = (unseen_neighbors, boundary_conflicts, degree)

                if score > best_score:
                    best_score = score
                    best_node = n
            return {"action": "move", "node": best_node}

        self._recompute_domains()

        def score_node(node):
            domain_size = len(self.domains.get(node, self.available_colors))
            degree = len(self.adj.get(node, []))
            return (domain_size, -degree)

        best = min(candidates, key=score_node)
        return {"action": "move", "node": best}

    def get_color_for_node(self, node_to_color, visible_state):
        self._ingest_observation(visible_state)
        self.current_node = visible_state["current_node"]

        if self.assignments.get(node_to_color) is not None:
            return {"action": "color", "node": node_to_color, "color": self.assignments[node_to_color]}

        self._recompute_domains()
        if not self._ac3_enforce():
            return self._fallback_color(node_to_color)
        plan = self._solve_known_subproblem()
        if plan and plan.get(node_to_color) is not None:
            chosen = plan[node_to_color]
            self.assignments[node_to_color] = chosen
            return {"action": "color", "node": node_to_color, "color": chosen}

        return self._fallback_color(node_to_color)


    def _fallback_color(self, node):
        neighbor_colors = {self.assignments.get(nb) for nb in self.adj.get(node, []) if self.assignments.get(nb) is not None}
        for c in self.available_colors:
            if c not in neighbor_colors:
                self.assignments[node] = c
                return {"action": "color", "node": node, "color": c}
        c = self.available_colors[0]
        self.assignments[node] = c
        return {"action": "color", "node": node, "color": c}

    def _ingest_observation(self, visible_state):
        nodes = visible_state["visible_graph"]["nodes"]
        edges = visible_state["visible_graph"]["edges"]
        colors_obs = visible_state["node_colors"]

        for n in nodes:
            if n not in self.adj:
                self.adj[n] = []
            self.known_nodes.add(n)

        for u, v in edges:
            if v not in self.adj[u]:
                self.adj[u].append(v)
            if u not in self.adj[v]:
                self.adj[v].append(u)

        for n in nodes:
            color = colors_obs.get(n)
            if color is not None:
                self.assignments[n] = color

        for n in self.known_nodes:
            if n not in self.domains:
                self.domains[n] = list(self.available_colors)

        self._recompute_domains()

    def _recompute_domains(self):
        for node in self.known_nodes:
            if self.assignments.get(node) is not None:
                self.domains[node] = [self.assignments[node]]
            else:
                illegal = {self.assignments.get(nb) for nb in self.adj.get(node, []) if self.assignments.get(nb) is not None}
                self.domains[node] = [c for c in self.available_colors if c not in illegal]


    def _ac3_enforce(self):
        queue = deque()
        for u in self.known_nodes:
            for v in self.adj.get(u, []):
                queue.append((u, v))

        while queue:
            xi, xj = queue.popleft()
            if self._revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.adj.get(xi, []):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, xi, xj):
        revised = False
        assigned_j = self.assignments.get(xj)
        if assigned_j is not None:
            if assigned_j in self.domains[xi] and len(self.domains[xi]) > 1:
                self.domains[xi] = [c for c in self.domains[xi] if c != assigned_j]
                return True


        to_remove = []
        for vi in self.domains[xi]:
            supported = any(vj != vi for vj in self.domains[xj])
            if not supported:
                to_remove.append(vi)
        if to_remove and len(self.domains[xi]) > len(to_remove):
            self.domains[xi] = [c for c in self.domains[xi] if c not in to_remove]
            revised = True
        return revised

    def _select_unassigned_var(self, assignments, domains):
        unassigned = [n for n in self.known_nodes if assignments.get(n) is None]
        if not unassigned:
            return None
        def key_fn(n):
            return (len(domains.get(n, self.available_colors)), -len(self.adj.get(n, [])))
        return min(unassigned, key=key_fn)

    def _order_domain_values(self, var, assignments, domains):
        values = list(domains.get(var, self.available_colors))
        def conflicts(color):
            conflict_count = 0
            for nb in self.adj.get(var, []):
                if assignments.get(nb) is None and color in domains.get(nb, self.available_colors):
                    conflict_count += 1
            return conflict_count
        values.sort(key=conflicts)
        return values

    def _forward_check(self, var, value, assignments, domains):
        for nb in self.adj.get(var, []):
            if assignments.get(nb) is None:
                if value in domains[nb]:
                    domains[nb] = [c for c in domains[nb] if c != value]
                    if not domains[nb]:
                        return False
        return True

    def _backtrack(self, assignments, domains):
        var = self._select_unassigned_var(assignments, domains)
        if var is None:
            return assignments
        for value in self._order_domain_values(var, assignments, domains):
            if any(assignments.get(nb) == value for nb in self.adj.get(var, [])):
                continue
            assignments[var] = value
            saved_domains = copy.deepcopy(domains)
            if self._forward_check(var, value, assignments, domains):
                result = self._backtrack(assignments, domains)
                if result is not None:
                    return result
            assignments[var] = None
            domains = saved_domains
        return None

    def _solve_known_subproblem(self):
        assignments = {n: self.assignments.get(n) for n in self.known_nodes}
        domains = {n: list(self.domains.get(n, self.available_colors)) for n in self.known_nodes}
        for n, c in assignments.items():
            if c is not None:
                domains[n] = [c]
        for u in self.known_nodes:
            cu = assignments.get(u)
            if cu is None:
                continue
            for v in self.adj.get(u, []):
                cv = assignments.get(v)
                if cv is not None and cv == cu:
                    return None
        return self._backtrack(assignments, domains)

