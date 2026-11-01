"""NOUR: Network for Organised Units & Records.

A menu-driven blood bank built on core data structures.
Run this file in PyCharm (right-click main.py, then Run 'main').
"""
from blood_bank import (BloodBank, EMERGENCY_PRIORITY, HIGH_STOCK, MIN_STOCK, QUEUE_SIZE)
from compatibility import CAN_DONATE_TO, GROUPS, bfs_donors, rank_fallbacks
import benchmark
import forecast

REASONS = {
    "1": ("Scheduled transfusion", 1),
    "2": ("Chronic anaemia", 2),
    "3": ("Elective surgery", 3),
    "4": ("Emergency surgery", 4),
    "5": ("Trauma", 5),
}

MENU = """
==================== NOUR ====================
  1. Register donor            7. Undo last action
  2. Record donation           8. Check stock / expiry alerts
  3. View donor history        9. Compatibility lookup
  4. Search donor             10. Sort and report / benchmark
  5. Raise blood request      11. Demand forecast (AI)
  6. Process next request     12. Show data structure internals
                               0. Exit
==============================================="""


# ---------- input helpers ----------
def ask(prompt, default=None):
    text = input(prompt + (" [%s]" % default if default is not None else "") + ": ").strip()
    return text if text else (default if default is not None else "")


def ask_int(prompt, low, high, default=None):
    while True:
        raw = ask(prompt, default)
        try:
            value = int(raw)
            if low <= value <= high:
                return value
        except ValueError:
            pass
        print("  Enter a whole number from %d to %d." % (low, high))


def ask_group(prompt="Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)"):
    while True:
        value = ask(prompt).upper().replace(" ", "")
        if value in GROUPS:
            return value
        print("  Not a valid blood group.")


def ask_donor_id():
    raw = ask("Donor ID, for example D1042").upper()
    return raw if raw.startswith("D") else "D" + raw


def heading(text):
    print("\n--- %s ---" % text)


def fmt_date(d):
    return d.strftime("%d %b %Y")


def days(n):
    return "%d day%s" % (n, "" if n == 1 else "s")


# ---------- menu actions ----------
def register_donor(bank):
    heading("Register donor")
    donor_id = ask_donor_id()
    name = ask("Full name")
    if not name:
        print("  A name is required.")
        return
    group = ask_group()
    try:
        bank.register_donor(donor_id, name, group)
        _, bucket, _ = bank.find_donor(donor_id)
        print("  Registered %s in hash bucket %d." % (name, bucket))
    except ValueError as err:
        print("  Rejected:", err)


def record_donation(bank):
    heading("Record donation")
    donor_id = ask_donor_id()
    try:
        unit = bank.record_donation(donor_id)
        print("  Donation recorded. Unit %s (%s) expires on %s."
              % (unit.id, unit.group, fmt_date(unit.expiry)))
    except ValueError as err:
        print("  Not recorded:", err)


def show_history(bank):
    heading("Donor history")
    donor, bucket, comparisons = bank.find_donor(ask_donor_id())
    if donor is None:
        print("  No donor with that ID.")
        return
    print("  %s  (%s, %s)   bucket %d, %d comparison(s)"
          % (donor.name, donor.id, donor.group, bucket, comparisons))
    dates = list(donor.history)
    if dates:
        print("  History (linked list): " + " -> ".join(fmt_date(d) for d in dates) + " -> NULL")
    else:
        print("  History (linked list): NULL, no donations yet")
    ok, since, next_date = bank.eligibility(donor)
    if ok:
        print("  Eligible to donate now.")
    else:
        print("  Not eligible: last donation %d days ago. Eligible again on %s."
              % (since, fmt_date(next_date)))


def search_donor(bank):
    heading("Search donor")
    donor_id = ask_donor_id()
    donor, bucket, comparisons = bank.find_donor(donor_id)
    print("  Hash(%s) = %s mod 11 = bucket %d" % (donor_id, donor_id[1:], bucket))
    if donor:
        print("  Found %s, group %s, after %d comparison(s)." % (donor.name, donor.group, comparisons))
    else:
        print("  Not found after %d comparison(s)." % comparisons)


def raise_request(bank):
    heading("Raise blood request")
    patient = ask("Patient name")
    if not patient:
        print("  A patient name is required.")
        return
    group = ask_group()
    units = ask_int("Units needed (1-4)", 1, 4, 1)
    print("  Reason: " + ", ".join("%s=%s" % (k, v[0]) for k, v in REASONS.items()))
    reason, priority = REASONS[str(ask_int("Reason number", 1, 5, 1))]
    try:
        req, where = bank.raise_request(patient, group, units, reason, priority)
        print("  %s added to the %s queue (priority %d)." % (req.id, where, priority))
    except OverflowError as err:
        print("  Overflow:", err, "Process a request first.")


def process_next(bank):
    heading("Process next request")
    try:
        req, source, issued, missing = bank.process_next()
    except IndexError as err:
        print("  Underflow:", err)
        return
    print("  %s for %s, %d x %s (%s, priority %d)"
          % (req.id, req.patient, req.units, req.group, source, req.priority))
    for unit in issued:
        note = "" if unit.group == req.group else "  (fallback from compatibility graph)"
        print("    issued %s %s, %s left%s" % (unit.group, unit.id, days(bank.days_left(unit)), note))
    if missing:
        print("  Short by %d unit(s). The request could only be partly filled." % missing)


def undo(bank):
    heading("Undo")
    try:
        print("  Undone:", bank.undo())
    except IndexError as err:
        print("  Nothing to undo:", err)
    except OverflowError as err:
        print("  Cannot undo yet:", err)


def stock_report(bank):
    heading("Blood stock")
    print("  %-6s %6s  %-6s %s" % ("Group", "Units", "Status", "Next out"))
    for g in GROUPS:
        top = bank.stock[g].peek()
        nxt = "%s (%s)" % (days(bank.days_left(top)), top.id) if top else "empty"
        print("  %-6s %6d  %-6s %s" % (g, len(bank.stock[g]), bank.status(g), nxt))
    print("  LOW is under %d units, HIGH is %d or more." % (MIN_STOCK, HIGH_STOCK))
    heading("Alerts")
    soon = bank.expiring_soon()
    if soon:
        print("  Expiring within 3 days (merge sorted):")
        for u in soon:
            print("    %s %s expires %s (%s)" % (u.group, u.id, fmt_date(u.expiry), days(bank.days_left(u))))
    else:
        print("  No units expiring within 3 days.")
    low = bank.low_groups()
    print("  Below minimum: " + (", ".join("%s (%d)" % (g, len(bank.stock[g])) for g in low) if low else "none"))


def compatibility(bank):
    heading("Compatibility lookup")
    recipient = ask_group("Recipient blood group")
    print("  %s can give to: %s" % (recipient, ", ".join(CAN_DONATE_TO[recipient])))
    print("  BFS over reversed edges, who can give to %s:" % recipient)
    for group, depth in bfs_donors(recipient):
        tag = "exact match" if depth == 0 else "fallback, depth %d" % depth
        print("    %-4s %-20s %d in stock" % (group, tag, len(bank.stock[group])))
    ranked = rank_fallbacks(recipient, bank.counts())
    available = [g for g in ranked if len(bank.stock[g])]
    print("  Best fallback order (rare donors kept for last): " + (", ".join(available) or "none in stock"))


def reports(bank):
    heading("Sort, search and benchmark")
    print("  1. Donors by last donation (merge sort)")
    print("  2. Units by expiry (quick sort)")
    print("  3. Find first unit with at least N days left (binary search)")
    print("  4. Run timing benchmark (takes a few seconds)")
    choice = ask_int("Choose", 1, 4, 1)
    if choice == 1:
        print("  %-18s %-6s %-12s %s" % ("Donor", "Group", "Last donation", "Days ago"))
        for d in bank.donors_by_last_donation():
            last = d.last_donation()
            print("  %-18s %-6s %-13s %d" % (d.name, d.group, fmt_date(last), (bank.today - last).days))
    elif choice == 2:
        units = bank.units_by_expiry()
        print("  %d units, earliest first (showing 15):" % len(units))
        for u in units[:15]:
            print("    %s %-4s %2d days" % (u.id, u.group, bank.days_left(u)))
    elif choice == 3:
        n = ask_int("Minimum days left", 0, 60, 20)
        unit, steps, total = bank.first_unit_with_days_left(n)
        if unit:
            print("  First unit with %d+ days: %s (%s, %d days). Binary search used %d steps, "
                  "a linear scan could need up to %d."
                  % (n, unit.id, unit.group, bank.days_left(unit), steps, total))
        else:
            print("  No unit has %d or more days left. Binary search used %d steps." % (n, steps))
    else:
        print("  Running, please wait...")
        benchmark.print_report(benchmark.run_all())


def demand_forecast(bank):
    heading("Demand forecast, next 7 days (exponential smoothing)")
    history = forecast.sample_weekly_history()
    result = forecast.forecast_all(history)
    print("  %-6s %-30s %8s %7s %9s  %s" % ("Group", "Last 8 weeks (units issued)", "Forecast", "Stock", "Covers", "Status"))
    for g in GROUPS:
        stock = len(bank.stock[g])
        cover = forecast.coverage_days(stock, result[g])
        weeks = " ".join("%4.1f" % x for x in history[g][-4:])
        print("  %-6s ...%-27s %8.1f %7d %6.1f d  %s"
              % (g, weeks, result[g], stock, cover, "SHORTFALL" if stock < result[g] else "covered"))
    alpha_rows = [(a, sum(forecast.backtest_mae(history[g], a) for g in GROUPS) / len(GROUPS))
                  for a in (0.2, 0.4, 0.6, 0.8)]
    print("  Average backtest error by alpha: " + ", ".join("%.1f -> %.2f" % r for r in alpha_rows))


def internals(bank):
    heading("Data structure internals")
    print("  Hash table (11 buckets, chaining):")
    for i, chain in enumerate(bank.donors.buckets):
        print("    [%2d] %s" % (i, " -> ".join(k for k, _ in chain) if chain else "empty"))
    group = ask_group("Show the min-heap array for which group")
    heap = bank.stock[group]
    print("  Min-heap for %s, array order (days left): %s"
          % (group, [bank.days_left(u) for u in heap.to_list()] or "empty"))
    print("  Circular queue (%d slots, F=front, R=rear):" % QUEUE_SIZE)
    rear = bank.routine.rear_index()
    for i, slot in enumerate(bank.routine.slots):
        marks = ("F" if i == bank.routine.front and bank.routine.count else "") + ("R" if i == rear else "")
        print("    [%d] %-3s %s" % (i, marks, "%s %s" % (slot.id, slot.patient) if slot else "empty"))
    print("  Emergency max-heap, most urgent first:")
    for r in bank.emergency.in_order():
        print("    %s priority %d %s (%s, %d units)" % (r.id, r.priority, r.patient, r.group, r.units))
    if not len(bank.emergency):
        print("    empty")
    print("  Undo stack depth: %d" % len(bank.undo_stack))
    print("  Recent activity:")
    for line in bank.activity[:6]:
        print("    " + line)


ACTIONS = {
    "1": register_donor, "2": record_donation, "3": show_history, "4": search_donor,
    "5": raise_request, "6": process_next, "7": undo, "8": stock_report,
    "9": compatibility, "10": reports, "11": demand_forecast, "12": internals,
}


def main():
    bank = BloodBank().load_sample_data()
    print("NOUR loaded with sample data: %d donors, %d units, %d pending requests."
          % (len(bank.donors), len(bank.all_units()), len(bank.emergency) + bank.routine.count))
    while True:
        print(MENU)
        try:
            choice = ask("Choose an option")
            if choice == "0":
                print("Goodbye.")
                return
            action = ACTIONS.get(choice)
            if action:
                action(bank)
            else:
                print("Please choose a number from 0 to 12.")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return


if __name__ == "__main__":
    main()
