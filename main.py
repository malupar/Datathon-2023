import pandas as pd
import numpy as np

class Element:
    def __init__(self, row):
        self.color = row['cod_color_code']
        self.id = row['cod_modelo_color']
        self.imgfile = row['des_filename']
        self.type = row['des_product_type']
        self.category = row['des_product_category']
         
    def _get_color(self):
        return self.color
    
    def _get_id(self):
        return self.id
    
    def _get_img(self):
        return self.imgfile
    
    def _get_type(self):
        return self.type

    def _get_category(self):
        return self.category

def get_data(file_path):
    df= pd.read_csv(file_path, header=0)
    return df

df = get_data("datathon/dataset/product_data.csv")

for row in df.index:
    Element(df.loc[row,:])

    
