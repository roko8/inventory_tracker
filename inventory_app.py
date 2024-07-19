from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Path to the inventory CSV file
inventory_file = 'data/inventory.csv'

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Initialize the inventory file if it doesn't exist
if not os.path.exists(inventory_file):
    df = pd.DataFrame(columns=['Item ID', 'Item Name', 'Quantity', 'Price'])
    df.to_csv(inventory_file, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_id = str(request.form['item_id'])
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        df = pd.read_csv(inventory_file, dtype={'Item ID': str})
        print("Before append:\n", df)  # Debug print
        new_row = pd.DataFrame([{'Item ID': item_id, 'Item Name': item_name, 'Quantity': quantity, 'Price': price}])
        df = pd.concat([df, new_row], ignore_index=True)
        print("After append:\n", df)  # Debug print
        df.to_csv(inventory_file, index=False)
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/inventory', methods=['GET', 'POST'])
def view_inventory():
    if request.method == 'POST':
        action = request.form['action']
        item_id = str(request.form['item_id'])
        quantity = int(request.form.get('quantity', 0))

        df = pd.read_csv(inventory_file, dtype={'Item ID': str})
        print("Before modification:\n", df)  # Debug print

        if action == 'remove':
            if item_id in df['Item ID'].values:
                df.loc[df['Item ID'] == item_id, 'Quantity'] -= quantity
                df = df[df['Quantity'] > 0]
            else:
                print(f"Item ID {item_id} not found.")
        elif action == 'delete':
            if item_id in df['Item ID'].values:
                df = df[df['Item ID'] != item_id]
            else:
                print(f"Item ID {item_id} not found.")

        print("After modification:\n", df)  # Debug print
        df.to_csv(inventory_file, index=False)
        return redirect(url_for('view_inventory'))

    df = pd.read_csv(inventory_file, dtype={'Item ID': str})
    inventory = df.to_dict('records')
    return render_template('view_inventory.html', inventory=inventory)

@app.route('/visualize')
def visualize_inventory():
    df = pd.read_csv(inventory_file)
    plot_url = generate_plot(df)
    return render_template('visualize.html', plot_url=plot_url)

def generate_plot(data):
    plt.figure(figsize=(10, 6))
    
    # Use a bar plot
    plt.bar(data['Item Name'], data['Quantity'], color='skyblue', edgecolor='black')
    
    # Add title and labels
    plt.title('Inventory Quantity by Item', fontsize=16, fontweight='bold')
    plt.xlabel('Item Name', fontsize=14)
    plt.ylabel('Quantity', fontsize=14)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right', fontsize=12)
    
    # Add grid for better visualization
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout to make room for the rotated x-axis labels
    plt.tight_layout()
    
    # Save the plot to a file
    plot_file = 'static/inventory_plot.png'
    plt.savefig(plot_file)
    plt.close()
    return plot_file

# inventory_app.py
if __name__ == "__main__":
    app.run(debug=False)
