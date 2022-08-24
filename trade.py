                                    #CryptoDataDownload
# No Express Warranty
# Consult Coinbase API Terms of Service
import pandas as pd
import json
import requests
import email, smtplib, ssl
from providers import PROVIDERS

def send_sms_via_email(
    number: str,
    message: str,
    provider: str,
    sender_credentials: tuple,
    subject: str = "sent using etext",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
):
    sender_email, email_password = sender_credentials
    receiver_email = f'{number}@{PROVIDERS.get(provider).get("sms")}'

    email_message = f"Subject:{subject}\nTo:{receiver_email}\n{message}"

    with smtplib.SMTP_SSL(
        smtp_server, smtp_port, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, email_message)
if __name__ == "__main__":
    """Simple script to query the Coinbase API and determine what cryptocurrency pairs are available.

       Will Save results to a CSV file.
    """
    number = "0703892272"
    message = "hello world!"
    provider = "Tre"

    sender_credentials = ("farhadd@gmail.com", "ywtfcrypkthiuqbb")

    #send_sms_via_email(number, message, provider, sender_credentials)
    currency_to_keep = ['USD','USDT'];
    # Set up our variables.
    # https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproducts -->  DOCUMENTATION
    while True:
        endpoint = 'https://api.exchange.coinbase.com/products'  # this is the coinbase API endpoint for the data
        response = requests.get(endpoint)
        
        resp = requests.get('https://api.crypto.com/v2/public/get-instruments')
        crypto_instruments = json.loads(resp.text)
        #print(crypto_instruments)
        if response.status_code == 200:  # checks if API says our request was OK
            data = json.loads(response.text)  # loads API data response
            #print(data);
            # next we create and store the JSON result into a Pandas Dataframe
            data_pd = pd.DataFrame(data)
             #print("Number of rows in the dataframe: %i\n" % (data_pd.shape[0]))
             #data_pd = data_pd.quote_currency.isin(currency_to_keep);
             #print("Number of rows in the dataframe: %i\n" % (data_pd.shape[0]))
             #print(data_pd[data_pd.quote_currency.isin(currency_to_keep)][['id', 'quote_currency']])
            data_pd.sort_values('id', inplace=True) 
            curr_list = data_pd[data_pd.quote_currency.isin(currency_to_keep)].id
            for f in curr_list:
                response = requests.get(endpoint+'/'+f+'/stats') 
                if response.status_code == 200:    
                    data2 = json.loads(response.text)            
                    data_curr = pd.DataFrame(data2,index = [f])
                    
                    f = f.replace('-','_')
                    filtered_inst = [p for p in crypto_instruments['result']['instruments'] if p['instrument_name'] == f
                    and
                    f[len(f)-4:] != "USDT"]
                    
                    if not any(filtered_inst) and f[len(f)-3:] == "USD":
                      f+="T"
                      filtered_inst = [p for p in crypto_instruments['result']['instruments'] if p['instrument_name'] == f]
                        
                    #print(f)
                    #print(f)
                    # if any(obj['instrument_name'] == f for obj in crypto_instruments['result']['instruments']):
                    for fi in filtered_inst:
                       # print(fi['instrument_name'])
                        request_string ='https://api.crypto.com/v2/public/get-ticker?instrument_name='+f
                        #request_string = "https://api.crypto.com/v2/public/get-ticker?instrument_name=ETH_USDT"
                        instrument_name_coinbase = f
                        #print(request_string)                
                        data_crypto_response = requests.get(request_string)
                        if data_crypto_response.status_code == 200:    
                            data_curr_crypto_json = json.loads(data_crypto_response.text)
                            # for obj in data_curr_crypto_json:
                            try:
                                crypto_last_price = data_curr_crypto_json['result']['data']['a']
                                coinbase_last_price = float(data2['last'])
                                priceDiff = abs(crypto_last_price - coinbase_last_price)
                                percentDiff = (priceDiff * 100.0) / min(crypto_last_price,coinbase_last_price) 
                                if percentDiff>5.0:
                                    print(f+": "+str(crypto_last_price)+" "+str(coinbase_last_price)+ " "+str(percentDiff))
                            except:              
                                print("An exception occured")
                        else:
                            print('shit2'); 
                    #print(data_curr);
                else:
                    print('shit '+f);    
        else:
            print("Oops. Bad Response from server. \n {response.status_code}")  # display our error message
                                   