import sys
import os
import pandas as pd
import numpy as np

def check_arguments():
    if len(sys.argv) != 5:
        print("Usage: python topsis.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

def main():
    check_arguments()
    
    input_file = sys.argv[1]
    weights_str = sys.argv[2]
    impacts_str = sys.argv[3]
    result_file = sys.argv[4]
    
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
        
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(input_file)
        else:
            print("Error: Unsupported file format. Please use CSV or Excel.")
            sys.exit(1)
            
        if df.shape[1] < 3:
            print("Error: Input file must contain at least 3 columns.")
            sys.exit(1)
            
        data = df.iloc[:, 1:].values
        
        try:
            data = data.astype(float)
        except ValueError:
            print("Error: Columns from 2nd onwards must contain numeric values.")
            sys.exit(1)
            
        weights = [float(w) for w in weights_str.split(',')]
        impacts = impacts_str.split(',')
        
        num_cols = data.shape[1]
        
        if len(weights) != num_cols:
            print(f"Error: Number of weights ({len(weights)}) does not match number of criteria ({num_cols}).")
            sys.exit(1)
            
        if len(impacts) != num_cols:
            print(f"Error: Number of impacts ({len(impacts)}) does not match number of criteria ({num_cols}).")
            sys.exit(1)
            
        if not all(i in ['+', '-'] for i in impacts):
            print("Error: Impacts must be either '+' or '-'.")
            sys.exit(1)
            
        rss = np.sqrt(np.sum(data**2, axis=0))
        
        if (rss == 0).any():
             print("Error: A column has all zero values, cannot normalize.")
             sys.exit(1)

        normalized_data = data / rss
        
        weighted_data = normalized_data * weights
        
        ideal_best = []
        ideal_worst = []
        
        for i in range(num_cols):
            if impacts[i] == '+':
                ideal_best.append(np.max(weighted_data[:, i]))
                ideal_worst.append(np.min(weighted_data[:, i]))
            else:
                ideal_best.append(np.min(weighted_data[:, i]))
                ideal_worst.append(np.max(weighted_data[:, i]))
                
        ideal_best = np.array(ideal_best)
        ideal_worst = np.array(ideal_worst)
        
        dist_best = np.sqrt(np.sum((weighted_data - ideal_best)**2, axis=1))
        dist_worst = np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1))
        
        total_dist = dist_best + dist_worst
        
        score = np.divide(dist_worst, total_dist, out=np.zeros_like(dist_worst), where=total_dist!=0)

        df['Topsis Score'] = score
        
        df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)
        
        df.to_csv(result_file, index=False)
        print(f"Success: Result saved to {result_file}")
        
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
