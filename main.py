import sys
import os
import operator
import csv
from tabulate import tabulate

OP_MAP = {
	"==": operator.eq,
	"!=": operator.ne,
	">": operator.gt,
	"<": operator.lt,
	">=": operator.ge,
	"<=": operator.le,
}

def safe_input(prompt):
	value = input(prompt)
	if value.strip().lower() == "exit":
		print("Cancelled by user.")
		return None
	return value

def resolve_column_name(data, input_col):
	if not data:
		return None
	actual_cols = data[0].keys()
	for col in actual_cols:
		if col.lower() == input_col.lower():
			return col
	return None

def read_csv(file_path):
	try:
		if not os.path.exists(file_path):
			print(f"ERROR: File '{file_path}' does not exist.")
			return None

		with open(file_path, 'r') as file:
			lines = file.readlines()

		if not lines:
			print("ERROR: File is empty.")
			return None

		header = lines[0].strip().split(',')
		data_lines = lines[1:]

		data = []
		for line in data_lines:
			values = line.strip().split(',')
			row_dict = dict(zip(header, values))
			data.append(row_dict)

		print(f"Success: File loaded. Total Rows: {len(data)}")
		print(f"Sample Row:\n{data[0]}")
		return data

	except Exception as e:
		print(f"ERROR: An error occured: {e}")
		return None

def filter_data(data, column_name, value):
	if not data:
		print("ERROR: No data to filter.")
		return

	column_name = resolve_column_name(data, column_name)
	if not column_name:
		print(f"ERROR: Column not found.")
		return

	filtered = [row for row in data if row.get(column_name, "").lower() == value.lower()]

	if not filtered:
		print("Warning:  No matching records found.")
		return

	print(f"\nMatch: Found {len(filtered)} matching rows:\n")
	print(tabulate(filtered, headers="keys", tablefmt="grid"))
	return filtered

def multi_filter_data(data):
	if not data:
		print("ERROR: No data to filter.")
		return

	conditions = []
	while True:
		col = safe_input("~ Enter column to filter (or 'done' to apply filters): ")
		if col is None or col.lower() == "done":
			break

		resolved = resolve_column_name(data, col)
		if not resolved:
			print(f"ERROR: Column '{col}' does not exist.")
			continue
		val = safe_input(f"~~ Enter value for '{resolved}': ")
		if val is None:
			break
		conditions.append((resolved,val))

	if not conditions:
		print("Warning:  No filters provided.")
		return

	filtered = data
	for col, val in conditions:
		filtered = [
			row for row in filtered
			if row.get(col) and row.get(col).strip().lower() == val.strip().lower()]

	if not filtered:
		print("Warning:  No matching records found.")
		return

	print(f"\nMatch: Found {len(filtered)} matching rows with all conditions:\n")
	print(tabulate(filtered, headers="keys", tablefmt="grid"))
	return filtered

def filter_with_operator(data):
	if not data:
		print("ERROR: No data loaded.")
		return

	col = safe_input("Enter column to filer by (or 'exit' to cancel): ")
	if col is None:
		return

	col = col.strip()
	col_match = next((c for c in data[0] if c.lower() == col.lower()), None)
	if not col_match:
		print(f"Column '{col}' not found.")
		return

	op_symbol = safe_input("Enter operator (==, !=, >, <, >=, <=): ")
	if op_symbol is None:
		return

	if op_symbol not in OP_MAP:
		print("ERROR: Invalid operator.")
		return

	value = safe_input("Enter value to compare against: ")
	if value is None:
		return

	op_func = OP_MAP[op_symbol]
	try:
		filtered = [row for row in data if op_func(float(row[col_match]), float(value))]
	except ValueError:
		filtered = [row for row in data if op_func(row[col_match], value)]

	if not filtered:
		print("WARNING: No matching records found.")
		return

	print(f"\nFound {len(filtered)} matching rows:\n")
	print(tabulate(filtered, headers="keys", tablefmt="grid"))
	return filtered

def advanced_multi_filter(data):
	if not data:
		print("ERRORL No data loaded.")
		return

	conditions = []

	while True:
		col = safe_input("Enter column (or 'done' to apply filters): ")
		if col is None or col.lower() == "done":
			break

		col = col.strip().lower()

		col_map = {c.lower(): c for c in data[0]}
		if col not in col_map:
			print(f"Column '{col}' not found.")
			continue

		col_match = col_map[col]

		if not col_match:
			print(f"Column '{col}' not found.")
			continue

		op = safe_input("Enter operator (==, !=, >, <, >=, <=): ")
		if op not in OP_MAP:
			print("Invalid Operator.")
			continue

		val = safe_input(f"Enter value to compare with: ")
		if val is None:
			break

		conditions.append((col_match, op, val))

	if not conditions:
		print("No valid filters provided.")
		return

	logic = safe_input("Use 'AND' or 'OR' between conditions? ").strip().lower()
	if logic not in ["and", "or"]:
		print("Invalid logic operator. Use 'AND' or 'OR'.")
		return

	op_func_list = []
	for col, op, val in conditions:
		func = OP_MAP[op]
		def make_condition(col=col, func=func, val=val):
			def condition(row):
				left = row.get(col)
				if left is None:
					return False
				try:
					return func(float(row[col]), float(val))
				except ValueError:
					return func(str(left).strip().lower(), str(val).strip().lower())
			return condition
		op_func_list.append(make_condition())

	if logic == "and":
		filtered = [row for row in data if all(cond(row) for cond in op_func_list)]
	else:
		filtered = [row for row in data if any(cond(row) for cond in op_func_list)]

	if not filtered:
		print("No matching records found.")
		return

	print(tabulate(filtered, headers="keys", tablefmt="grid"))
	return filtered

def list_column(data):
	if not data:
		print("ERROR: No data loaded.")
		return

	columns = data[0].keys()
	print("\n🧾 Columns available in the file:")
	for col in columns:
		print(f" - {col}")

def show_unique_values(data, column_name):
	if not data:
		print("ERROR: No data loaded.")
		return

	column_name = resolve_column_name(data, column_name)
	if not column_name:
		print(f"ERROR: Column not found.")
		return

	unique_vals = set(row[column_name] for row in data)
	print(f"\nStats: Unique values in '{column_name}':")
	for val in unique_vals:
		print(f" - {val}")

def show_stats(data, column_name):
	column_name = resolve_column_name(data, column_name)
	if not column_name:
		print(f"ERROR: Column not found.")
		return

	values = [row.get(column_name) for row in data if column_name in row]

	if not values:
		print(f"Warning:  Column '{column_name}' not found in any row.")
		return

	unique_values = set(values)
	print(f"Stats: Stats for column '{column_name}':")
	print(f"Total: Total Values: {len(values)}")
	print(f"Unique: Unique Values: {len(unique_values)}")

	try:
		numeric_values = [float(val) for val in values]
		print(f"Min: Min: {min(numeric_values)}")
		print(f"Max: Max: {max(numeric_values)}")
		print(f"Stats: Average: {sum(numeric_values) / len(numeric_values):.2f}")
	except ValueError:
		print("Note: Values are non-numeric, skipping min/max/average.")

def show_all_rows(data, limit=20):
	if not data:
		print("ERROR: No data loaded.")
		return

	print(f"\nShowing: Showing up to {limit} rows:\n")
	for i, row in enumerate(data[:limit], 1):
		print(f"{i}. {row}")
	if len(data) > limit:
		print(f"Important Note: Note: Only showing first {limit} rows out of {len(data)}.")

def export_to_csv(data):
	if not data:
		print("ERROR: No data to export.")
		return

	filename = safe_input("Enter filename to export (e.g., output.csv): ")
	if filename is None:
		return

	if not filename.endswith(".csv"):
		filename += ".csv"

	if os.path.exists(filename):
		confirm = safe_input(f"File '{filename}' already exists. Overwrite? (y/n): ")
		if confirm is None or confirm.lower() != 'y':
			print("Export cancelled.")
			return

	try:
		with open(filename, 'w', newline='') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
			writer.writeheader()
			writer.writerows(data)

		print(f"Data exported successfully to '{filename}'.")
	except Exception as e:
		print(f"Failed to export: {e}")

def sort_data(data):
	if not data:
		print("ERROR: No data to sort.")
		return

	col = safe_input("Enter column to sort by (or 'exit' to cancel): ")
	if col is None:
		return

	col_map = {c.lower(): c for c in data[0]}
	col = col.strip().lower()
	if col not in col_map:
		print(f"Column '{col}' not found.")
		return

	col = col_map[col]

	order = safe_input("Enter 'asc' for ascending or 'desc' for descending (default is asc): ")
	if order is None:
		return

	reverse = order.strip().lower() == "desc"

	try:
		sorted_data = sorted(data, key=lambda x: float(x.get(col, 0)), reverse=reverse)
	except ValueError:
		sorted_data = sorted(data, key=lambda x: str(x.get(col, "")).lower(), reverse=reverse)

	print(f"\nSorted data by column '{col}' ({'descending' if reverse else 'ascending'}):")
	for i, row in enumerate(sorted_data[:20], 1):
		print(f"{i}. {row}")

	return sorted_data

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Warning:  Please provide the CSV file path. Example: python main.py sample_data.csv")
		sys.exit()

	data = read_csv(sys.argv[1])
	working_data = data.copy()

	if not data:
		sys.exit()

	if "--stats" in sys.argv:
		stats_index = sys.argv.index("--stats")
		if stats_index + 1 < len(sys.argv):
			column_name = sys.argv[stats_index +1]
			show_stats(data, column_name)
		else:
			column_name = safe_input("📝 Enter the column name to show stats (or 'exit' to cancel): ")
			if column_name is None:
				sys.exit()

		show_stats(working_data, column_name)

	if "--filter" in sys.argv:
		index = sys.argv.index("--filter")
		if index + 2 < len(sys.argv):
			col = sys.argv[index+1]
			val = sys.argv[index+2]
			filter_data(working_data, col, val)
		else:
			print("ERROR: Please provide both column and value for --filter.")
		sys.exit()

	if "--filter-multi" in sys.argv:
		index = sys.argv.index("--filter-multi")
		pairs = sys.argv[index+1:]
		if len(pairs) % 2 != 0:
			print("ERROR: Please provide pairs of column and value.")
			sys.exit()

		conditions = []
		for i in range(0, len(pairs), 2):
			col = pairs[i]
			val = pairs[i+1]
			col_resolved = resolve_column_name(working_data, col)
			if not col_resolved:
				print(f"ERROR: Column '{col}' not found.")
				sys.exit()
			conditions.append((col_resolved, val))

		filtered = working_data
		for col, val in conditions:
			filtered = [
				row for row in filtered
				if row.get(col, "").strip().lower() == val.strip().lower()
			]

		if not filtered:
			print("Warning:  No matching records found.")

		else:
			print(f"\nMatch: Found {len(filtered)} matching rows with all conditions:\n")
			for row in filtered:
				print(row)

		sys.exit()

	if "--filter-op" in sys.argv:
		index = sys.argv.index("--filter-op")
		if index + 3 >= len(sys.argv):
			print("ERROR: Usage: --filter-op <column> <operator> <value>")
			sys.exit()

		col = sys.argv[index + 1]
		op_symbol = sys.argv[index + 2]
		val_input = sys.argv[index + 3]

		col_resolved = resolve_column_name(working_data, col)
		if not col_resolved:
			print(f"ERROR: Column '{col}' not found.")
			sys.exit()

		if op_symbol not in OP_MAP:
			print(f"ERROR: Unsupported operator '{op_symbol}'. Use one of: {', '.join(OP_MAP.keys())}. Remember to wrap them in quotes.")
			sys.exit()

		op_func = OP_MAP[op_symbol]
		filtered = []

		for row in working_data:
			cell_value = row.get(col_resolved, "").strip()

			try:
				cell_value = float(cell_value)
				val_input_cast = float(val_input)
			except ValueError:
				cell_value = cell_value.lower()
				val_input_cast = val_input.lower()

			if op_func(cell_value, val_input_cast):
				filtered.append(row)

		if not filtered:
			print("Warning:  No matching records found.")
		else:
			print(f"\nMatch: Found {len(filtered)} matching rows with '{col_resolved} {op_symbol} {val_input}':\n")
			for row in filtered:
				print(row)

		sys.exit()

	while True:
		print("\nImportant Note: What do you want to do?")
		print("1. Filter data (Single)")
		print("2. List Columns")
		print("3. Show Unique Values for a Column")
		print("4. Show All Rows")
		print("5. Filter Data (Multiple)")
		print("6. Export Last Filtered Data")
		print("7. Filter Data (with Operators)")
		print("8. Advanced Multi-Condition Filter (AND/OR)")
		print("9. Sort Data")
		print("10. Exit")
		print("11. Reset Working Data")

		choice = safe_input("Enter your choice (or 'exit' to cancel): ")
		if choice is None:
			print("Bye... Exiting...")
			break

		if choice == '1':
			col = safe_input("Enter column to filter by (or 'exit' to cancel): ")
			if col is None:
				continue
			val = safe_input("Enter value to match (or 'exit' to cancel): ")
			if val is None:
				continue
			result = filter_data(working_data, col, val)
			if result:
				working_data = result
		elif choice == '2':
			list_column(working_data)
		elif choice == '3':
			col = safe_input("Enter Column to inspect: ")
			if col is None:
				continue
			show_unique_values(working_data, col)
		elif choice == '4':
			show_all_rows(working_data)
		elif choice == '5':
			result = multi_filter_data(working_data)
			if result:
				working_data = result
		elif choice == '6':
			export_to_csv(working_data)
		elif choice == '7':
			result = filter_with_operator(working_data)
			if result:
				working_data = result
		elif choice == '8':
			result = advanced_multi_filter(working_data)
			if result:
				working_data = result
		elif choice == '9':
			result = sort_data(working_data)
			if result:
				working_data = result
		elif choice == '11':
			working_data = data.copy()
			print("Working data reset to full dataset.")
		elif choice == '10':
			print("Bye... Exiting...")
			break
		else:
			print("ERROR: Invalid choice. Please try again.")
