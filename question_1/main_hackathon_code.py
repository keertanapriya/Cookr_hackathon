import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QIcon
import pandas as pd
import sys
import csv
result_dict={}
# Step 1: Opening the dataset
data = pd.read_csv('cookr_food_data.csv')

# Step 2: Cleaning, Tokenization
data = data.drop(columns=['recipe'])
data.replace(-1, pd.NA, inplace=True)

# Step 3: Split the Data
from sklearn.model_selection import train_test_split
train, test = train_test_split(data, test_size=0.001, random_state=42)

# Step 4: Create List of 0's and 1's for Each Food Item
def create_feature_vector(row):
    res = []
    attributes = [
        'base_ingredient', 'diet', 'preparation_method',
        'taste', 'time_of_taking', 'cuisine_followed',
        'region', 'protein_rich_indicator', 'nutritional_benefits'
    ]
    for attr in attributes:
        possible_values = data[attr].unique()
        feature_vector = [0] * len(possible_values)
        if pd.notna(row[attr]):
            feature_vector[list(possible_values).index(row[attr])] = 1
        res.extend(feature_vector)
    return res

# Create dictionary for each food item
food_dict = {}
for index, row in train.iterrows():
    food_dict[row['name']] = create_feature_vector(row)

class CookrInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cookr")
        self.setGeometry(100, 100, 800, 800)
        self.setWindowIcon(QIcon('pressure-cooker.png'))
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header
        header_label = QLabel("Cookr")
        header_label.setStyleSheet("font-size: 28px; padding: 10px; background-color:#FAED3D;")
        layout.addWidget(header_label)

        # Navigation bar
        nav_layout = QHBoxLayout()
        nav_buttons = {"Home": self.show_home, "Recipes": self.show_recipes, "About Us": self.show_about_us, "Contact": self.show_contact}
        for btn_text, callback in nav_buttons.items():
            btn = QPushButton(btn_text)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
        layout.addLayout(nav_layout)

        # Main content area
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)

        # Footer
        footer_label = QLabel("© trialversion.")
        footer_label.setStyleSheet("background-color: #333; color: white; padding: 10px; text-align: center;")
        layout.addWidget(footer_label)

        # Show Home page by default
        self.show_home()
        self.previous_dishes = []

    def show_home(self):
        self.text_browser.setStyleSheet("background-color: #FFBF00")
        self.text_browser.setHtml("""
            <h2>Welcome to Cookr</h2><br>
            <div style="display: flex;">
                <img src="dosa_1.png" style="max-width: 200px; margin-right: 20px;">
                <div>
                    <p>Delicious Home-Cooked Meals</p>
                    <p>Explore a variety of mouth-watering recipes prepared by our talented home chefs.</p>
                </div>
            </div>
        """)

    def show_recipes(self):
        self.text_browser.clear()
        input_layout = QVBoxLayout()
        if not hasattr(self, "input_boxes"):
            self.input_boxes = []

        if len(self.input_boxes) == 0:
            new_dish_input = QLineEdit()
            new_dish_input.setPlaceholderText("Enter recipe here...")
            self.input_boxes.append(new_dish_input)
            input_layout.addWidget(new_dish_input)
        else:
            for dish_input in self.input_boxes:
                input_layout.addWidget(dish_input)

            new_dish_input = QLineEdit()
            new_dish_input.setPlaceholderText("Enter recipe here...")
            self.input_boxes.append(new_dish_input)
            input_layout.addWidget(new_dish_input)

        add_button = QPushButton("Add New Recipe")
        add_button.clicked.connect(lambda: self.add_new_recipe(new_dish_input))
        input_layout.addWidget(add_button)

        data = pd.read_csv('cookr_food_data.csv')
        recipes = data['name'].tolist()[:10]

        html_content = "<h2>Items</h2><ul>"
        for recipe in recipes:
            html_content += f"<li>{recipe}</li>"
        html_content += "</ul>"

        # Add the input layout to the main layout
        layout = self.centralWidget().layout()
        layout.addLayout(input_layout)
        self.text_browser.setStyleSheet("font-size:20px;background-color: #FFF; background-image: url('image_3.jpg'); background-position: center; background-repeat: no-repeat;")
        self.text_browser.setHtml(html_content)

    
    def add_new_recipe(self, new_dish_input):
        new_dish_name = new_dish_input.text()
        words = new_dish_name.split()
        if len(words) == 1:
            found = False
            for food_name, bool_list in food_dict.items():
                if words[0].lower() in food_name.lower():
                    print("\nFound Match:")
                    print(food_name)
                    self.print_features(food_name)
                    found = True
                    break
            
            if not found:
                print("\nDish not found.")
        else:
            dict_temp_2 = {}
            for word in words:
                dict_temp = {}
                for food_name, bool_list in food_dict.items():
                    if word.lower() in food_name.lower():
                        dict_temp[food_name] = bool_list
                dict_temp_2[word] = dict_temp

            print("\nJaccard Distances with Initial Data:")
            jaccard_results = []
            for word1 in words:
                for word2 in words:
                    if word1 != word2:
                        print(f"Pair: {word1}, {word2}")
                        for item1_name, item1_features in dict_temp_2[word1].items():
                            for item2_name, item2_features in dict_temp_2[word2].items():
                                if item1_name != item2_name:
                                    intersection = sum(x and y for x, y in zip(item1_features, item2_features))
                                    union = sum(x or y for x, y in zip(item1_features, item2_features))
                                    jaccard = intersection / union if union != 0 else 0

                                    jaccard_results.append((item1_name, item2_name, jaccard))

            max_jaccard = max(jaccard_results, key=lambda x: x[2])

            def merge_features(features1, features2):
                merged_features = [max(f1, f2) for f1, f2 in zip(features1, features2)]
                return merged_features

            new_dish_features = merge_features(food_dict[max_jaccard[0]], food_dict[max_jaccard[1]])
            food_dict[new_dish_name] = new_dish_features
            print("\nFeatures of New Dish Name:", new_dish_name)
            #self.print_features(new_dish_name)
            self.print_new_features(new_dish_name,new_dish_features)
            self.write_dict_to_csv()
            self.previous_dishes.append(new_dish_name)
            self.show_recipes()
    def write_dict_to_csv(self):
        global result_dict
        with open('cookr_food_data.csv', 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write header row with attribute names
            attributes = [
                'name', 'base_ingredient', 'diet', 'preparation_method',
                'taste', 'time_of_taking', 'cuisine_followed',
                'region', 'protein_rich_indicator', 'nutritional_benefits'
            ]
            
            # Write data rows
            for dish_name, attributes_list in result_dict.items():
                csvwriter.writerow([dish_name] + attributes_list)
    def print_features(self, food_name):
        if food_name in food_dict:
            attributes = [
                'base_ingredient', 'diet', 'preparation_method',
                'taste', 'time_of_taking', 'cuisine_followed',
                'region', 'protein_rich_indicator', 'nutritional_benefits'
            ]
            print("Features for", food_name)
            feature_values = food_dict[food_name]
            idx = 0
            l=['']
            for attribute in attributes:
                possible_values = data[attribute].unique()
                attribute_values = feature_values[idx:idx+len(possible_values)]
                idx += len(possible_values)
                if 1 in attribute_values:
                    print("-", attribute, ":", possible_values[attribute_values.index(1)])
                    l.append(possible_values[attribute_values.index(1)])
            global result_dict  
            result_dict[food_name]=l
            print(result_dict)      
    def print_new_features(self, dish_name, features):
        dialog = QDialog(self)
        dialog.setWindowTitle("Features of " + dish_name)
        dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(dialog)

        label = QLabel("Features of " + dish_name+"\n")
        layout.addWidget(label)

        # Get the feature names from the data
        attributes = [
            'base_ingredient', 'diet', 'preparation_method',
            'taste', 'time_of_taking', 'cuisine_followed',
            'region', 'protein_rich_indicator', 'nutritional_benefits'
        ]
        feature_values = food_dict[dish_name]
        idx = 0
        l=['']
        for attribute in attributes:
            possible_values = data[attribute].unique()
            attribute_values = feature_values[idx:idx+len(possible_values)]
            idx += len(possible_values)
            if 1 in attribute_values:
                print("-", attribute, ":", possible_values[attribute_values.index(1)])
                l.append(possible_values[attribute_values.index(1)])
                st=attribute+":"+possible_values[attribute_values.index(1)]
                feature_label = QLabel(st)
                layout.addWidget(feature_label)
        global result_dict  
        result_dict[dish_name]=l
        dialog.setLayout(layout)
        dialog.exec_()   
            
    def show_about_us(self):
        self.text_browser.setStyleSheet("background-color: #FFBF00")
        self.text_browser.setHtml("""
            <h2>About Us</h2>
            <p>We are a team passionate about cooking and sharing delicious recipes with the world.</p>
        """)
    
    def show_contact(self):
        self.text_browser.setStyleSheet("background-color: #FFBF00")
        self.text_browser.setHtml("""
            <h2>Contact</h2>
            <p>For any inquiries or feedback, please contact us at contact@cookr.com.</p>
        """)

app = QApplication(sys.argv)
interface = CookrInterface()
interface.show()
sys.exit(app.exec_())

