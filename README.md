# 🩸 NOUR – Blood Bank Management System

**NOUR (Network for Organised Units & Records)**

A Data Structures mini project developed using Python. This project provides a simple Blood Bank Management System to manage donors, blood donations, blood stock, emergency requests, compatibility checking, reports and blood demand forecasting.

---

## 📸 Project Screenshots

### 1. Dashboard
<img src="Nour/nour_project/Screenshot/Dashboard.png" width="650">

### 2. Blood Group Compatibility
<img src="Nour/nour_project/Screenshot/Compatibility.png" width="650">

### 3. Donors
<img src="Nour/nour_project/Screenshot/Donars.png" width="650">

### 4. Donor Records
<img src="Nour/nour_project/Screenshot/Donars2.png" width="650">

### 5. Donor Stocks
<img src="Nour/nour_project/Screenshot/DonarsStocks.png" width="650">

### 6. Reports
<img src="Nour/nour_project/Screenshot/Reports.png" width="650">

### 7. Blood Requests
<img src="Nour/nour_project/Screenshot/Request.png" width="650">

### 8. Request Details
<img src="Nour/nour_project/Screenshot/Request2.png" width="650">

## ✨ Features

- Donor Registration and Management
- Blood Donation Records
- Blood Stock Management
- Blood Group Compatibility Checking
- Emergency Blood Requests
- Routine Blood Request Management
- Expiry Alerts
- Donor History
- Reports and Sorting
- Blood Demand Forecasting

---

## 🧠 Data Structures Used

| Data Structure | Application |
|---|---|
| Hash Table | Fast donor searching |
| Linked List | Maintaining donation history |
| Min Heap | Managing blood stock by expiry |
| Max Heap | Managing emergency requests |
| Circular Queue | Managing routine requests |
| Stack | Undo operation |
| Graph | Blood group compatibility |
| BFS | Finding compatible blood groups |
| Binary Search Tree | Donor search comparison |
| Sorting Algorithms | Sorting records and reports |

---

## 🛠️ Technologies Used

- Python 3.8+
- HTML
- CSS
- JavaScript
- Python Standard Library

---

## 📂 Project Structure

```text
NOUR/
│
├── screenshots/
│   ├── Dashboard.png
│   ├── Compatibility.png
│   ├── Donars.png
│   ├── Donars2.png
│   ├── DonarsStocks.png
│   ├── Reports.png
│   ├── Request.png
│   └── Request2.png
│
├── web/
│   └── index.html
│
├── blood_bank.py
├── hash_table.py
├── linked_list.py
├── heap.py
├── circular_queue.py
├── stack.py
├── compatibility.py
├── bst.py
├── sorting.py
├── forecast.py
├── benchmark.py
├── main.py
├── server.py
├── test_nour.py
├── test_server.py
│
└── README.md
