from buttonLine import *
import sqlalchemy as sa

con = ConnectDB('Line Data')
with con.begin() as conn:
    qry = sa.text('''SELECT Name,TaxId,[Firstname],[VIN] FROM [Line Data].[dbo].[Profile Line] PL INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]
    WHERE UserId = 'U97caf21a53b92919005e158b429c8c2b'
    ''')
    resultset = conn.execute(qry)
    results_as_dict = resultset.mappings().all()
    for i in results_as_dict:
        TaxID = i['TaxId']
        VIN = i['VIN']
        flex_message = Allvalue(TaxID,VIN)
        print(flex_message)