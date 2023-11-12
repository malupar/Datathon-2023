#Reading data
We use the pandas library to read the dataframe and transform it to the elements with the desired attributes in linear time
#Creating graphs
It uses the recommended outfits in outfit_data.csv and with this it creates or modifies the edges connecting two types of clothes, categories, color, etc... It also uses some chosen parameters (alpha, beta, gamma) that give more importance to color or specific types of clothes.
This process has a complexity of O(N*C^2) where N is the number of outfits and C is the number of clothes per outfit which can work as a constant in most cases.
#Creating outfits
The algorithm can take an element as a starting point from the streamlit user interface or pick one at random following two criteria: completely random or following a probability distribution which will prioritize the most compatible pieces. It chooses it in linear time

Then, it tries to maximize the weight of the edges, also in linear time.
#Showcasing the outfits
It is done using the streamlit user interface where an outfit is suggested with slight possible variations.
