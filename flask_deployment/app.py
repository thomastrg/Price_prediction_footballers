import numpy as np
import pickle
import sklearn
from flask import Flask,render_template,request,jsonify
import pandas 


app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))
names = pickle.load(open('names.pkl', 'rb'))
df=pickle.load(open('df.pkl', 'rb'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/players',methods=["GET","POST"])
def predict_search_player():
    
    player_names = names
    if request.method == "POST":
        input_name=request.form.get('Name')
        if ('&#39;' in input_name ) : input_name = input_name.replace('&#39;',"'")

        if len(df[df["Name"] == str(input_name)]) != 0 : 
            player = df[df["Name"] == str(input_name)].sort_index().iloc[0].copy()
            player.drop(['Name', 'Value €', 'Value $', 'Value £', 'Wage £', 'Wage $'],  inplace=True)

            output= model.predict([player.values])[0]

            return render_template('index2.html', names=player_names, prediction_text='The predicted price of {} is {} €'.format(input_name, '{:0,.0f}'.format(output)))

        else : 
            return render_template('index2.html', names=player_names, prediction_text='We did not find data about this player.')
    
    else : return render_template('index2.html', names=player_names)


@app.route('/predict',methods=['POST'])
def predict():

    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0],1)

    return render_template('index.html' , prediction_text='The predicted price of the player is {} €'.format('{:0,.0f}'.format(output)))


if __name__ == "__main__":
    app.run(debug=True)