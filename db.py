import pymssql

conn = pymssql.connect(server='ladegaardmoeller.dk', user='SA', password='He1ena@Hot', database='RaceBot', autocommit=True)
cursor = conn.cursor(as_dict=True)

def getCustFromDiscord(discordId):
    cursor.callproc('GetUserFromDiscord', (discordId,))
    for row in cursor:
        return row['CustId']

def createUser(discordId, custId):
    cursor.callproc('CreateUser', (discordId, custId))
    for row in cursor:
        return row['Altered']
