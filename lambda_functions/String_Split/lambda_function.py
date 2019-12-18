import json

def lambda_handler(event, context):
    # TODO implement
    dict=address_split(event['address'])
    print(dict)
    return {
        'statusCode': 200,
        'body': json.dumps('complete')
    }
    
    
    
def address_split(str):
    #address1 = {"address":"1270 Amst Ave, New York NY"}
    #address
    strs=str.split(",")
    dict={}
    dict['street'] = strs[0].strip()
    city_state=strs[1].split()
    dict['state'] = city_state[-1].strip()
    city=""
    for i in city_state[0:-1]:
        city+=i+" "
        dict['city'] = city.strip()
    
    return dict
    
    