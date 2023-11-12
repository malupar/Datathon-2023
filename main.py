import pandas as pd
import numpy as np
import random
from collections import defaultdict
from PIL import Image
import streamlit as st

class Element:
    def __init__(self, row):
        self.familycolor = row['des_agrup_color_eng']
        self.color = row['des_color_specification_esp']
        self.id = row['cod_modelo_color']
        self.imgfile = row['des_filename']
        self.type = row['des_product_type']
        self.category = row['des_product_category']
        self.aggregated = row['des_product_aggregated_family']
        self.family = row['des_product_family']
         
    def _get_color(self):
        return self.color
    
    def _get_familycolor(self):
        return self.familycolor

    def _get_id(self):
        return self.id
    
    def _get_img(self):
        return self.imgfile
    
    def _get_type(self):
        return self.type

    def _get_category(self):
        return self.category
    
    def _get_family(self):
        return self.family

    def _get_aggregated(self):
        return self.aggregated
    
def create_categoria(A):
    categorias = {}
    des_product_category = []

    for x in A['des_product_category']:
        if x not in des_product_category:
            des_product_category.append(x)

    for x in des_product_category:
        categorias[x] = {}

    for x in categorias.keys():
        for y in A.loc[A["des_product_category"] == x, "des_product_aggregated_family"]:
            categorias[x][y] = {}

    for x in categorias.keys():
        for y in categorias[x].keys():
            for z in A.loc[(A["des_product_aggregated_family"] == y) & (A["des_product_category"] == x), "des_product_family"]:
                categorias[x][y][z] = {}

    for x in categorias.keys():
        for y in categorias[x].keys():
            for z in categorias[x][y].keys():
                for w in A.loc[(A["des_product_aggregated_family"] == y) & (A["des_product_category"] == x) & (A["des_product_family"] == z), "des_product_type"]:
                    categorias[x][y][z][w] = []
    return categorias

def create_color_cat(A):
    categorias = {}
    des_product_category = []
    for x in A['des_agrup_color_eng']:
        if x not in des_product_category:
            des_product_category.append(x)

    for x in des_product_category:
        categorias[x] = {}

    for x in categorias.keys():
        for y in A.loc[A["des_agrup_color_eng"] == x, "des_color_specification_esp"]:
            categorias[x][y] = []

    return categorias

class outfitinator:
    def __init__(self, elements, alpha = 2.5, alpha2 = 5, beta = 1, beta2 = 0.25, gamma = 0.5, gamma2 = 1, same_color = 10000):
        self.color_graph = defaultdict(dict)
        self.alpha = alpha
        self.alpha2 = alpha2
        self.family_graph = defaultdict(dict)
        self.familycolor = defaultdict(dict)
        self.graphtype = defaultdict(dict)
        self.graphaggregated = defaultdict(dict)
        self.graphcategory = defaultdict(dict)
        self.beta = beta
        self.beta2 = beta2
        self.gamma = gamma
        self.gamma2 = gamma2
        self.same_color = same_color
        self.elements = elements
        self.compatible = {}

    def _create_edge(self, a, b):
        a2, b2 = self.elements[a], self.elements[b]
        color1, color2 = a2._get_color(), b2._get_color()
        color11, color12 = a2._get_familycolor(), b2._get_familycolor()
        type1, type2 = a2._get_type(), b2._get_type()
        agg1, agg2 = a2._get_aggregated(), b2._get_aggregated()
        fam1, fam2 = a2._get_family(), b2._get_family()
        cat1, cat2 = a2._get_category(), b2._get_category()

        if (color1 in self.color_graph) & (color2 in self.color_graph[color1]):
            self.color_graph[color1][color2] += self.alpha
        else:
            self.color_graph[color1][color2] = self.alpha
            
        if (color11 in self.familycolor) & (color12 in self.familycolor[color11]):
            self.familycolor[color11][color12] += self.alpha2
        else:
            self.familycolor[color11][color12] = self.alpha2

        if (type1 in self.graphtype) & (type2 in self.graphtype[type1]):
            self.graphtype[type1][type2] += self.beta
        else:
            self.graphtype[type1][type2] = self.beta
        if (agg1 in self.graphaggregated) & (agg2 in self.graphaggregated[agg1]):
            self.graphaggregated[agg1][agg2] += self.beta2
        else:
            self.graphaggregated[agg1][agg2] = self.beta2
        if (fam1 in self.family_graph) & (fam2 in self.family_graph[fam1]):
            self.family_graph[fam1][fam2] += self.gamma
        else:
            self.family_graph[fam1][fam2] = self.gamma
        if (cat1 in self.color_graph) & (cat2 in self.color_graph[cat1]):
            self.graphcategory[cat1][cat2] += self.gamma2
        else:
            self.graphcategory[cat1][cat2] = self.gamma2


        if a in self.compatible.keys():
            self.compatible[a] += 1
        else:
            self.compatible[a] = 1
        
        if b in self.compatible.keys():
            self.compatible[b] += 1
        else:
            self.compatible[b] = 1

    def _gen_outfit(self, df):
        outfits = {}
        
        for row in df.index:
            cur_outfit = df.loc[row, 'cod_modelo_color']
            outfit_id = df.loc[row, 'cod_outfit']
            if outfit_id in outfits.keys():
                outfits[outfit_id].append(cur_outfit)
            else:
                outfits[outfit_id] = [cur_outfit]

        for outfit in outfits:
            bad_outfit = False
            for elem in outfits[outfit]:
                if bad_outfit:
                    break
                a = self.elements[elem]
                if (a._get_category() == 'Home' or a._get_category() == 'Beauty'):
                    bad_outfit = True
                    break
                if a._get_category() == 'Accesories, Swim and Intimate' or a._get_category() == 'Outerwear':
                    continue
                for elem2 in outfits[outfit]:
                    if elem2 == elem:
                        break
                    b = self.elements[elem2]
                    if a._get_category() == b._get_category():
                        bad_outfit = True
                        break
            if bad_outfit:
                continue
            else:
                for elem in outfits[outfit]:
                    for elem2 in outfits[outfit]:
                        if elem == elem2:
                            break
                        self._create_edge(elem, elem2)

    def _possible(self, elem, top, bottom, dress, shoe):
        cat = elem._get_category()
        if cat == 'Tops':
            if dress != -1:
                return False, top, bottom, dress, shoe
            else :
                if top == -1:
                    top = 0
                return True, top, bottom, dress, shoe
        if cat == 'Bottoms':
            if dress != -1:
                return False, top, bottom, dress, shoe
            else :
                if bottom == -1:
                    bottom = 0
                return True, top, bottom, dress, shoe
        if cat == 'Dresses, jumpsuits and Complete set':
            if top != -1 or bottom != -1:
                return False, top, bottom, dress, shoe
            else:
                if dress == -1:
                    dress = 0
                return True, top, bottom, dress, shoe
        tip = elem._get_family()
        if tip == 'Footwear':
            if shoe == -1:
                shoe = 0
            return True, top, bottom, dress, shoe
        return True, top, bottom, dress, shoe
    
    def _compute_compatibility(self, a2, b2):
        color1, color2 = a2._get_color(), b2._get_color()
        color11, color12 = a2._get_familycolor(), b2._get_familycolor()
        type1, type2 = a2._get_type(), b2._get_type()
        agg1, agg2 = a2._get_aggregated(), b2._get_aggregated()
        fam1, fam2 = a2._get_family(), b2._get_family()
        cat1, cat2 = a2._get_category(), b2._get_category()
        if cat1 == cat2 and cat1 != 'Accesories, Swim and Intimate':
            return -1
        if agg1 == agg2 and agg1 == 'Accessories' and (fam1 != 'Footwear' and fam2 != 'Footwear'):
            return -1
        ans = 0
        if (color1 in self.color_graph) & (color2 in self.color_graph[color1]):
            ans += self.color_graph[color1][color2]     
        if (color11 in self.familycolor) & (color12 in self.familycolor[color11]):
            ans += self.familycolor[color11][color12]
        if (type1 in self.graphtype) & (type2 in self.graphtype[type1]):
            ans += self.graphtype[type1][type2]
        if (agg1 in self.graphaggregated) & (agg2 in self.graphaggregated[agg1]):
            ans += self.graphaggregated[agg1][agg2]
        if (fam1 in self.family_graph) & (fam2 in self.family_graph[fam1]):
            ans += self.family_graph[fam1][fam2]
        if (cat1 in self.color_graph) & (cat2 in self.color_graph[cat1]):
            ans += self.graphcategory[cat1][cat2]
        if color1 == color2:
            ans += self.same_color
        return ans
    
    def _choose_first_piece(self, restriccions):
        sum = 0
        for el in self.compatible:
            if (self.elements[el]._get_category() == 'Home' or self.elements[el]._get_category() == 'Beauty'):
                continue
            if self.elements[el]._get_aggregated() == 'Swim and intimate':
                continue
            if not restriccions:
                sum += 1
            elif self.elements[el]._get_familycolor() in restriccions:
                sum += 1
        target = np.random.uniform(0, sum)
        sum2 = 0
        for el in self.compatible:
            if (self.elements[el]._get_category() == 'Home' or self.elements[el]._get_category() == 'Beauty'):
                continue
            if self.elements[el]._get_aggregated() == 'Swim and intimate':
                continue
            if not restriccions:
                sum2 += 1
            elif self.elements[el]._get_familycolor() in restriccions:
                sum2 += 1
            if sum2 >= target:
                return el
        return None
    
    def _choose_hot_first_piece(self, restriccions):
        sum = 0
        for el in self.compatible:
            if (self.elements[el]._get_category() == 'Home' or self.elements[el]._get_category() == 'Beauty'):
                continue
            if self.elements[el]._get_aggregated() == 'Swim and intimate':
                continue
            if not restriccions:
                sum += self.compatible[el]
            elif self.elements[el]._get_familycolor() in restriccions:
                sum += self.compatible[el]
        target = np.random.uniform(0, sum)
        sum2 = 0
        for el in self.compatible:
            if (self.elements[el]._get_category() == 'Home' or self.elements[el]._get_category() == 'Beauty'):
                continue
            if self.elements[el]._get_aggregated() == 'Swim and intimate':
                continue
            if not restriccions:
                sum2 += self.compatible[el]
            elif self.elements[el]._get_familycolor() in restriccions:
                sum2 += self.compatible[el]
            if sum2 >= target:
                return el
        return None
    
    def _genera_outfit(self, restriccions, popular, input=None):
        final_outfit = {}
        other_outfit = {}
        f_el = None
        if input is None:
            if not popular:
                f_el = self._choose_first_piece(restriccions)
            else:
                f_el = self._choose_hot_first_piece(restriccions)
        else:
            f_el = input
        if self.elements[f_el]._get_family() == 'Footwear':
            final_outfit['Footwear'] = (self.elements[f_el]._get_img())
        elif self.elements[f_el]._get_aggregated() == 'Accessories':
            final_outfit['Accessories'] = (self.elements[f_el]._get_img())
        else:
            final_outfit[self.elements[f_el]._get_category()] = (self.elements[f_el]._get_img())
        top, bottom, dress, shoe = -1, -1, -1, -1
        _, top, bottom, dress, shoe = self._possible(self.elements[f_el], top, bottom, dress, shoe)
        outerwear_bool, outerwear = False, -1
        acc_bool, acc = False, -1
        if 'Accessories' in final_outfit:
            acc_bool = True
        else:
            acc_bool = random.randint(0, 1)
        if 'Outerwear' in final_outfit:
            outerwear_bool = True
        else:
            outerwear_bool = random.randint(0, 1)

        for el in self.elements:
            elem = self.elements[el]
            pos, top, bottom, dress, shoe = self._possible(elem, top, bottom, dress, shoe)
            if (pos):
                if (restriccions and elem._get_familycolor() in restriccions) or not restriccions:
                    best = self._compute_compatibility(self.elements[f_el], elem)
                    if best == -1:
                        continue
                    cat = elem._get_category()
                    tip = elem._get_family()
                    agg = elem._get_aggregated()
                    if outerwear_bool and cat == 'Outerwear':
                        if outerwear < best:
                            if 'Outerwear' in final_outfit:
                                other_outfit['Outerwear'] = ''+final_outfit['Outerwear']
                            final_outfit['Outerwear'] = elem._get_img()
                            outerwear = max(outerwear, best)
                    elif cat == 'Tops':
                        if top < best:
                            if 'Tops' in final_outfit:
                                other_outfit['Tops'] = ''+(final_outfit['Tops'])
                            final_outfit['Tops'] = elem._get_img()
                            top = max(top, best)
                    elif cat == 'Bottoms':
                        if best > bottom:
                            if 'Bottoms' in final_outfit:
                                other_outfit['Bottoms'] = ''+final_outfit['Bottoms']
                            final_outfit['Bottoms'] = elem._get_img()
                            bottom = max(bottom, best)
                    elif cat == 'Dresses, jumpsuits and Complete set':
                        if best > dress:
                            if 'Dresses, jumpsuits and Complete set' in final_outfit:
                                other_outfit['Dresses, jumpsuits and Complete set'] = ''+final_outfit['Dresses, jumpsuits and Complete set']
                            final_outfit['Dresses, jumpsuits and Complete set'] = elem._get_img()
                            dress = max(dress, best)
                    elif tip == 'Footwear':
                        if best > shoe:
                            if 'Footwear' in final_outfit:
                                other_outfit['Footwear'] = ''+(final_outfit['Footwear'])
                            final_outfit['Footwear'] = elem._get_img()
                            shoe = max(shoe, best)
                    elif acc_bool and agg == 'Accessories':
                        if best > acc:
                            if 'Accessories' in final_outfit:
                                other_outfit['Accessories'] = ''+final_outfit['Accessories']
                            final_outfit['Accessories'] = elem._get_img()
                            acc = max(acc, best)

        list_img, list2_img = [], []
        for x in final_outfit:
            y = final_outfit[x]
            img = Image.open(y)
            list_img.append(img)
        st.image(list_img)
        st.write('Other pieces that might interest you are:')
        for x in other_outfit:
            y = other_outfit[x]
            img = Image.open(y)
            list2_img.append(img)
        st.image(list2_img)

def get_data(file_path):
    df= pd.read_csv(file_path, header=0)
    return df

def print_categorized_elements(categorias):
    for x in categorias.keys():
        print(x)
        for y in categorias[x].keys():
            print("---", y)
            for z in categorias[x][y].keys():
                print("------", z)
                for w in categorias[x][y][z].keys():
                    print("---------", w)
                    print(categorias[x][y][z][w])


df = get_data("datathon/dataset/product_data.csv")
outfits = get_data("datathon/dataset/outfit_data.csv")

elements = {}
category_elements = {}
category_list = []
categoria_dict = create_categoria(df)
color_dict = create_color_cat(df)
color_list = []
for color in color_dict.keys():
    color_list.append(color)
for row in df.index:
    el = Element(df.loc[row,:])
    elements[el._get_id()] = el
    x = el._get_category()
    y = el._get_aggregated()
    z = el._get_family()
    w = el._get_type()
    a = el._get_familycolor()
    c = el._get_color()
    categoria_dict[x][y][z][w].append(el._get_id())
    color_dict[a][c].append(el._get_id())

#print_categorized_elements(categoria_dict)

ultimate_outfit = outfitinator(elements)
ultimate_outfit._gen_outfit(outfits) #genera aristas grafo

st.write("Generate an outfit")

restriccions = st.multiselect('Choose your favourite colors for your outfit', color_list)
col1, col2 = st.columns([1,1])
with col1:
    b = st.button('Click me to generate an outfit!')
with col2:
    b2 = st.button('Click me to generate one of the most popular outfits right now!')
text_input = st.text_input(
        "Enter some text ->",
        label_visibility="visible",
        disabled=False,
        placeholder="or enter the code of an item you like",
    )
if b:
    ultimate_outfit._genera_outfit(restriccions, False)
    number = st.number_input('How good is this outfit from 1 to 10?', value=5, min_value=1, max_value=10, step=1)

if b2:
    ultimate_outfit._genera_outfit(restriccions, True)
    number = st.number_input('How good is this outfit from 1 to 10?', value=5, min_value=1, max_value=10, step=1)
if text_input:
    print(text_input)
    ultimate_outfit._genera_outfit(restriccions, None, text_input)
    number = st.number_input('How good is this outfit from 1 to 10?', value=5, min_value=1, max_value=10, step=1)