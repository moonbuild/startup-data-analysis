import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import numpy as np

# settting a base style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
OUTPUT_DIR = 'visualizations'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_amount(amount):
    if pd.isna(amount) or amount == 'Undisclosed' or amount == 'undisclosed':
        return np.nan
    
    amount = str(amount).replace(',', '')
    
    multiplier = 1
    if 'Rs' in amount or '₹' in amount:
        # taking approx: 1 USD = 83 INR
        multiplier = 0.012 
        amount = amount.replace('Rs', '').replace('₹', '').strip()
        if 'crore' in amount.lower() or 'cr' in amount.lower():
            multiplier *= 10000000
            amount = re.sub(r'crore|cr', '', amount, flags=re.IGNORECASE)
        elif 'lakh' in amount.lower():
            multiplier *= 100000
            amount = re.sub(r'lakh', '', amount, flags=re.IGNORECASE)
    elif '$' in amount:
        amount = amount.replace('$', '').strip()
        if 'M' in amount:
            multiplier = 1000000
            amount = amount.replace('M', '')
        elif 'Mn' in amount:
            multiplier = 1000000
            amount = amount.replace('Mn', '')
        elif 'B' in amount:
            multiplier = 1000000000
            amount = amount.replace('B', '')
        elif 'K' in amount:
            multiplier = 1000
            amount = amount.replace('K', '')
    
    try:
        val = float(amount)
        return val * multiplier
    except ValueError:
        return np.nan

def clean_city(city):
    if pd.isna(city):
        return 'Unknown'
    city = city.split('/')[0].strip()
    city = city.split(',')[0].strip()
    return city

def analyze_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print("Cleaning data...")
    

    amount_col = [c for c in df.columns if 'Amount' in c]
    if amount_col:
        df['Cleaned_Amount_USD'] = df[amount_col[0]].apply(clean_amount)
    else:
        print("Could not find Amount column.")
        return

    hq_col = [c for c in df.columns if 'Headquarters' in c or 'Location' in c]
    if hq_col:
        df['Cleaned_City'] = df[hq_col[0]].apply(clean_city)
        city_map = {
            'Bangalore': 'Bengaluru',
            'Gurgaon': 'Gurugram',
            'New Delhi': 'Delhi'
        }
        df['Cleaned_City'] = df['Cleaned_City'].replace(city_map)
    
    sector_col = [c for c in df.columns if 'Sector' in c or 'Industry' in c][0]
    
    stage_col = [c for c in df.columns if 'Round' in c or 'Stage' in c]
    if stage_col:
        def clean_stage(stage):
            if pd.isna(stage): return 'Unknown'
            stage = str(stage).lower()
            if 'seed' in stage: return 'Seed'
            if 'series a' in stage: return 'Series A'
            if 'series b' in stage: return 'Series B'
            if 'series c' in stage: return 'Series C'
            if 'debt' in stage: return 'Debt'
            if 'angel' in stage: return 'Angel'
            if 'pre-series a' in stage: return 'Pre-Series A'
            return stage.title()
            
        df['Cleaned_Stage'] = df[stage_col[0]].apply(clean_stage)

    # Visualizations 
    
    # Top 10 Startup Hubs (by Count)
    plt.figure(figsize=(12, 6))
    top_cities = df['Cleaned_City'].value_counts().head(10)
    sns.barplot(x=top_cities.index, y=top_cities.values, palette='viridis')
    plt.title('Top 10 Startup Hubs (by Count)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/top_cities_count.png')
    plt.close()

    # Top 10 Cities by Total Funding (Million USD)
    if 'Cleaned_Amount_USD' in df.columns:
        plt.figure(figsize=(12, 6))
        city_funding = df.groupby('Cleaned_City')['Cleaned_Amount_USD'].sum().sort_values(ascending=False).head(10)
        sns.barplot(x=city_funding.index, y=city_funding.values / 1e6, palette='magma')
        plt.title('Top 10 Cities by Total Funding (Million USD)')
        plt.ylabel('Total Funding ($M)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/top_cities_funding.png')
        plt.close()

    # Top 15 Sectors by Number of Startups
    plt.figure(figsize=(12, 8))
    top_sectors = df[sector_col].value_counts().head(15)
    sns.barplot(y=top_sectors.index, x=top_sectors.values, palette='crest')
    plt.title('Top 15 Sectors by Number of Startups')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/top_sectors_count.png')
    plt.close()

    # Top 15 Sectors by Total Funding (Million USD)
    if 'Cleaned_Amount_USD' in df.columns:
        plt.figure(figsize=(12, 8))
        sector_funding = df.groupby(sector_col)['Cleaned_Amount_USD'].sum().sort_values(ascending=False).head(15)
        sns.barplot(y=sector_funding.index, x=sector_funding.values / 1e6, palette='rocket')
        plt.title('Top 15 Sectors by Total Funding (Million USD)')
        plt.xlabel('Total Funding ($M)')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/top_sectors_funding.png')
        plt.close()

    # Distribution of Funding Stages
    if 'Cleaned_Stage' in df.columns:
        plt.figure(figsize=(10, 10))
        stage_counts = df['Cleaned_Stage'].value_counts()
        # Filter out tiny values for cleaner pie chart
        stage_counts = stage_counts[stage_counts > stage_counts.sum() * 0.01] 
        plt.pie(stage_counts.values, labels=stage_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Funding Stages')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/funding_stages_pie.png')
        plt.close()

    # Top investors
    investors_list = []
    investor_col = [c for c in df.columns if 'Investor' in c or 'Invest' in c]
    investor_col = [c for c in investor_col if 'Type' not in c]
    
    if investor_col:
        for item in df[investor_col[0]].dropna():
            invs = re.split(r',|/', str(item))
            for inv in invs:
                inv = inv.strip()
                if inv and inv != '-' and len(inv) > 2:
                    investors_list.append(inv)
        
        investor_counts = pd.Series(investors_list).value_counts().head(15)
        plt.figure(figsize=(12, 8))
        sns.barplot(y=investor_counts.index, x=investor_counts.values, palette='mako')
        plt.title('Top 15 Active Investors')
        plt.xlabel('Number of Investments')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/top_investors.png')
        plt.close()

    # Distribution of Funding Amounts (Log Scale)
    if 'Cleaned_Amount_USD' in df.columns:
        plt.figure(figsize=(10, 6))
        amounts = df['Cleaned_Amount_USD'].dropna()
        amounts = amounts[amounts > 0]
        sns.histplot(amounts, log_scale=True, kde=True, color='green')
        plt.title('Distribution of Funding Amounts (Log Scale)')
        plt.xlabel('Funding Amount (USD)')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/funding_distribution.png')
        plt.close()


    # Network graph: Investors <-> Startups
    try:
        import networkx as nx
        plt.figure(figsize=(15, 15))
        G = nx.Graph()
        
        # top 20 investors 
        top_investors_set = set(investor_counts.head(20).index)
        
        # build edges
        if investor_col:
            for idx, row in df.iterrows():
                startup = row['Company']
                inv_raw = str(row[investor_col[0]])
                if inv_raw and inv_raw != '-':
                    invs = re.split(r',|/', inv_raw)
                    for inv in invs:
                        inv = inv.strip()
                        if inv in top_investors_set:
                            G.add_edge(inv, startup)
        
        if len(G.nodes) > 0:
            pos = nx.spring_layout(G, k=0.3, iterations=50)
            
            # investor nodes
            investor_nodes = [n for n in G.nodes if n in top_investors_set]
            nx.draw_networkx_nodes(G, pos, nodelist=investor_nodes, node_color='red', node_size=300, label='Investors')
            
            # startup nodes
            startup_nodes = [n for n in G.nodes if n not in top_investors_set]
            nx.draw_networkx_nodes(G, pos, nodelist=startup_nodes, node_color='skyblue', node_size=100, label='Startups', alpha=0.7)
            
            nx.draw_networkx_edges(G, pos, alpha=0.3)
            
            nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
            
            plt.title('Network Graph: Top 20 Investors and their Portfolio Companies')
            plt.legend()
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(f'{OUTPUT_DIR}/investor_network.png')
            plt.close()
    except ImportError:
        print("NetworkX not installed. Skipping network graph.")
    except Exception as e:
        print(f"Error creating network graph: {e}")

    # Heatmap: Sector vs Location
    if sector_col and 'Cleaned_City' in df.columns:
        plt.figure(figsize=(14, 10))

        top_locs = df['Cleaned_City'].value_counts().head(10).index
        top_secs = df[sector_col].value_counts().head(10).index
        
        heatmap_data = df[df['Cleaned_City'].isin(top_locs) & df[sector_col].isin(top_secs)]
        pivot_table = pd.crosstab(heatmap_data[sector_col], heatmap_data['Cleaned_City'])
        
        sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlGnBu')
        plt.title('Startup Density Heatmap: Sector vs. Location')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/sector_location_heatmap.png')
        plt.close()

    print("\n--- Analysis Summary ---")
    print(f"Total Startups Analyzed: {len(df)}")
    print(f"Total Funding Recorded: ${df['Cleaned_Amount_USD'].sum()/1e9:.2f} Billion USD")
    print(f"\nTop 5 Cities by Count:\n{top_cities.head(5).to_string()}")
    print(f"\nTop 5 Sectors by Count:\n{top_sectors.head(5).to_string()}")
    if 'Cleaned_Stage' in df.columns:
        print(f"\nTop Funding Stages:\n{df['Cleaned_Stage'].value_counts().head(5).to_string()}")

if __name__ == "__main__":
    analyze_data(r'c:\Users\mp\LAB\data-analysis\Startup_funding_2025.csv')
