# NOUR: Network for Organised Units & Records

A menu-driven blood bank built on core data structures. AI use case: healthcare, with a blood demand forecast.
Pure Python 3.8 or newer. No packages to install.

## Run the website (connected to your Python code)

1. Right-click `server.py` and choose **Run 'server'**.
2. Your browser opens at http://127.0.0.1:8000. If it does not, type that address in the browser yourself.
3. Use the website normally. Every button runs your own `blood_bank.py`, so the hash table, heaps, circular queue, stack, BFS, sorting and benchmark you wrote are what the page shows.
4. Stop it with the red Stop button in PyCharm.

No packages are needed, it uses only Python's standard library. The page is `web/index.html`. The fonts load from Google when you are online and fall back to normal system fonts when you are offline. If port 8000 is busy, set the environment variable `NOUR_PORT` to another number in the Run configuration.

Everything the website shows is in memory, so restarting `server.py` resets the sample data.

## Run the console menu in PyCharm

1. Unzip `nour_project.zip`.
2. In PyCharm choose **File > Open** and select the `nour_project` folder.
3. Make sure an interpreter is set (**Settings > Project > Python Interpreter**, any Python 3.8+).
4. Right-click `main.py` and choose **Run 'main'**.
5. To run the tests, right-click `test_nour.py` and choose **Run 'Python tests in test_nour'**.

Type the menu number in the Run window and press Enter. Sample data loads automatically.

## Files and the concept each one covers

| File | Concept | Used for |
|---|---|---|
| `hash_table.py` | Hash table, separate chaining | Donor lookup by ID, duplicate check |
| `linked_list.py` | Singly linked list with tail pointer | Donation history, one node per visit |
| `heap.py` | Min-heap and max-heap | Stock by expiry (min), emergency requests (max) |
| `circular_queue.py` | Circular queue, fixed size | Routine requests, overflow and underflow |
| `stack.py` | Stack | Undo last action |
| `compatibility.py` | Directed graph, BFS | Who can donate to whom, fallback groups |
| `sorting.py` | Bubble, insertion, merge, quick sort, binary search | Reports and comparisons |
| `bst.py` | Binary search tree | Compared against the hash table |
| `blood_bank.py` | Ties all of the above together | All business rules |
| `forecast.py` | Exponential smoothing | AI demand forecast |
| `benchmark.py` | Timing comparisons | Report analysis |
| `main.py` | Console menu | Run for the text version |
| `server.py` | Website back end | Run for the website |
| `web/index.html` | Website page | Opened by `server.py` |
| `test_nour.py` | Unit tests | 18 tests |
| `test_server.py` | Website back end tests | 5 tests |

## Time complexity table for the report

| Operation | Structure | Complexity |
|---|---|---|
| Donor lookup | Hash table | O(1) average, O(n) worst case |
| Add a donation to history | Linked list (tail pointer) | O(1) |
| Remove last history node (undo) | Singly linked list | O(n) |
| Issue the earliest-expiry unit | Min-heap | O(log n) |
| Add a unit to stock | Min-heap | O(log n) |
| Next emergency request | Max-heap | O(log n) |
| Enqueue / dequeue routine request | Circular queue | O(1) |
| Undo | Stack | O(1) |
| Compatibility search | BFS on 8 nodes | O(V + E) |
| Sort donors or units | Merge sort / quick sort | O(n log n) |
| Bubble / insertion sort | | O(n^2) |
| Find a unit by days left | Binary search | O(log n) |
| Search in an unbalanced BST | BST | O(log n) random, O(n) sorted input |

## How the pieces connect

1. **Donor registers:** the hash table checks whether the ID already exists.
2. **Eligibility:** the last donation date is compared with the gap rule (90 days, configurable with `min_gap`).
3. **Donation recorded:** a node is added to the donor's linked list and a new unit goes into that group's min-heap.
4. **Request arrives:** priority 4 and 5 go to the emergency max-heap, the rest to the routine circular queue.
5. **Process next:** the exact group is tried first, the earliest-expiry unit is popped, and the action is pushed onto the undo stack.
6. **Stock out:** BFS over the compatibility graph finds fallback groups. Rare donors such as O- are used last.
7. **Alerts:** units expiring within 3 days, and groups below 6 units (LOW) or at 14 and above (HIGH).

## Menu

```
 1. Register donor            7. Undo last action
 2. Record donation           8. Check stock / expiry alerts
 3. View donor history        9. Compatibility lookup
 4. Search donor             10. Sort and report / benchmark
 5. Raise blood request      11. Demand forecast (AI)
 6. Process next request     12. Show data structure internals
                              0. Exit
```

Option 12 prints the hash buckets, a heap array, the circular queue slots and the emergency heap. It is the best option for screenshots and for explaining the structures in the oral.

## Sample benchmark (your numbers will differ)

| Test | Result |
|---|---|
| 1,000 lookups in 10,000 donors | Linear 119 ms, binary 2.8 ms, BST 1.9 ms, hash 2.4 ms |
| BST with sorted insert order | Height 2000, about 78 times slower than a random-order BST |
| Sort 2,000 records | Bubble 258 ms, insertion 103 ms, merge 4.1 ms, quick 2.9 ms |
| 3,000 units, issue in expiry order | Sorted array 287 ms, min-heap 15 ms |

At 10,000 records, a balanced BST and a hash table are close in plain Python. State this honestly in the report: the hash table's advantage is O(1) on average and it does not degrade on sorted IDs, which the BST does.

## Limitations and future scope

- Data is held in memory only. Add a file or database to keep it between runs.
- The forecast uses sample weekly history. Replace it with real issue records and a trained ML model.
- Future scope: SMS alerts to eligible donors, multi-hospital networks, expiry-aware transfer between banks.
