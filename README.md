# Colour Me If You Can 🎨

### **Overview**

This repository contains the solution for the **CSP (Constraint Satisfaction Problem) Tournament Assignment**, where the goal is to build an **intelligent agent** that can solve a graph colouring problem under **partial observability**. The challenge is to colour all nodes with minimal backtracking and movement costs.

---

## 🧩 **Objective**

Develop an **AI agent** that colours all nodes of a graph such that:

* No two connected nodes share the same colour.
* The agent can only see a **limited portion** of the graph.
* The agent minimises **reassignments** (backtracking) and **moves** to maximise its score.

## 🧾 **Assignment Guidelines**

✅ Implement backtracking CSP in `[YourRollNumber].py`
✅ Keep logic within a single file
✅ Optimise for fewer moves and reassignments
❌ Do not modify engine or runner files
❌ Do not submit multiple files

---

## ⚙️ **How My Agent Works**

1. **Domain Filtering and Constraint Propagation:**

   * The agent enforces **graph colouring constraints** by ensuring no two connected nodes share the same colour.
   * It uses **AC-3 (Arc Consistency Algorithm 3)** to propagate these constraints:

   * If one node’s domain changes, it updates neighbouring nodes to remove conflicting colours.
   * This continuous pruning helps eliminate invalid choices early, reducing backtracking later.
   * The domains remain consistent at all times — meaning every colour assignment made is locally valid.

---

2. **Movement Decision Strategy:**

   * When deciding where to move next, the agent balances **exploration** (to discover unknown nodes) and **exploitation** (to colour visible nodes efficiently).
   * If uncoloured nodes are visible, it selects one using the **Minimum Remaining Values (MRV)** heuristic — moving toward the node with the **fewest valid colours left**, since those are most constrained.
   * If all visible nodes are already colored, it moves strategically toward nodes with **unseen neighbours** or **higher connectivity**, to expand its visible graph and gather more information.
   * This ensures minimal unnecessary movement and fewer move penalties.

---

3. **Colour Assignment Strategy:**

   * Before choosing a colour, the agent recalculates the domains of all visible nodes to reflect the latest knowledge.
   * It applies **AC-3** again to maintain arc consistency between neighbouring nodes.
   * Then it uses **backtracking search** with **forward checking**, where:

     * The agent assigns a colour tentatively to a node.
     * It checks if that colour leaves all neighbouring domains non-empty.
     * If a conflict arises, it undoes the assignment (backtracks) and tries the next colour.
   * Heuristics used include:

     * **MRV (Minimum Remaining Values):** Prioritise colouring the node with the smallest domain (most constrained).
     * **LCV (Least Constraining Value):** Choose a colour that leaves the maximum options open for neighbouring nodes.
   * This makes the agent both systematic and efficient in handling conflicts.

---

4. **Fallback Mechanism/Greedy:**

   * In rare cases where backtracking fails or the current subproblem is unsolvable (due to limited visibility), the agent applies a **fallback colouring strategy**.
   * It assigns the first colour that does not conflict with the currently colored neighbors.
   * This prevents the agent from getting stuck and allows continuous progress.

---

## 🏗️ **Project Structure**

| File                  | Description                                    |
| --------------------- | ---------------------------------------------- |
| `[YourRollNumber].py` | Your implementation file (submit only this).   |
| `game_engine.py`      | Core CSP and validation logic (do not modify). |
| `game_runner.py`      | Manages tournament flow and scoring.           |
| `level1.json`         | Sample level configuration.                    |

---

## 📊 **Scoring System**

| Action               | Points | Description                         |
| -------------------- | ------ | ----------------------------------- |
| Correct Coloring     | +100   | For a valid, complete colouring     |
| Move Penalty         | -1     | For every move the agent makes      |
| Reassignment Penalty | -1     | For every colour change (backtrack) |
| Perfection Bonus     | +10    | For zero reassignments              |
| Failure              | -∞     | For incomplete or invalid colouring |

**Final Score = 100 - Moves - Reassignments + Perfection Bonus**

---

## 🚀 **How to Run**

1. **Clone this repository:**

```bash
git clone https://github.com/Asta1729/AI_Assignment.git
cd AI_Assignment
```

2. **Run the assignment:**

```bash
python game_runner.py
```

---

## 🧠 **Example Gameplay**

```
--- Step 1 ---
Agent starts at node A.
Agent colors node A with 'Red'.

--- Step 2 ---
Agent moves to node B (Move penalty: -1).
Agent colors node B with 'Green'.

--- Final ---
All nodes colored correctly!
Score: 102 points
```

---

**Developed for the CSP Tournament Assignment — "Colour Me If You Can" 🧠🎨**
