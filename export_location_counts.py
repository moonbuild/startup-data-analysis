import pandas as pd

def clean_city(city):
    if pd.isna(city):
        return None
    city = str(city).split('/')[0].strip()
    city = city.replace('Bangalore', 'Bengaluru')
    city = city.replace('Gurgaon', 'Gurugram')
    city = city.replace('New Delhi', 'Delhi')
    if 'Delhi' in city: return 'Delhi'
    return city

def export_counts(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    headquarters_col = [c for c in df.columns if 'Headquarters' in c or 'Location' in c][0]
    df['Location'] = df[headquarters_col].apply(clean_city)
    location_counts = df['Location'].value_counts()
    
    # coordinates of citys only
    city_coords = {
        'Bengaluru': [12.9716, 77.5946],
        'Delhi': [28.6139, 77.2090],
        'Gurugram': [28.4595, 77.0266],
        'Mumbai': [19.0760, 72.8777],
        'Pune': [18.5204, 73.8567],
        'Hyderabad': [17.3850, 78.4867],
        'Chennai': [13.0827, 80.2707],
        'Noida': [28.5355, 77.3910],
        'Ahmedabad': [23.0225, 72.5714],
        'Jaipur': [26.9124, 75.7873],
        'Kolkata': [22.5726, 88.3639],
        'Indore': [22.7196, 75.8577],
        'Chandigarh': [30.7333, 76.7794],
        'Kochi': [9.9312, 76.2673],
        'Surat': [21.1702, 72.8311],
        'Vadodara': [22.3072, 73.1812],
        'Lucknow': [26.8467, 80.9462],
        'Coimbatore': [11.0168, 76.9558],
        'Thiruvananthapuram': [8.5241, 76.9366],
        'Bhubaneswar': [20.2961, 85.8245],
        'Nagpur': [21.1458, 79.0882],
        'Visakhapatnam': [17.6868, 83.2185],
        'Bhopal': [23.2599, 77.4126],
        'Patna': [25.5941, 85.1376],
        'Raipur': [21.2514, 81.6296],
        'Goa': [15.2993, 74.1240],
        'Dehradun': [30.3165, 78.0322]
    }

    output_df = location_counts.reset_index()
    output_df.columns = ['Location', 'Startup_Count']
    
    output_df['Shown_On_Map'] = output_df['Location'].apply(lambda x: 'Yes' if x in city_coords else 'No')
    
    output_df['Latitude'] = output_df['Location'].apply(lambda x: city_coords.get(x, [None, None])[0])
    output_df['Longitude'] = output_df['Location'].apply(lambda x: city_coords.get(x, [None, None])[1])
    
    output_file = 'location_counts.csv'
    output_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
    print(output_df.head(10))

if __name__ == "__main__":
    export_counts('Startup_funding_2025.csv')